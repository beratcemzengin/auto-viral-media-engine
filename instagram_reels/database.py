import sqlite3
import os
from datetime import datetime

try:
    from . import config
except ImportError:
    import config

DB_PATH = os.path.join(config.DATA_DIR, "posted.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tmdb_id INTEGER NOT NULL,
            media_type TEXT NOT NULL DEFAULT 'movie',
            title TEXT NOT NULL,
            original_title TEXT,
            overview TEXT,
            poster_path TEXT,
            backdrop_path TEXT,
            release_date TEXT,
            vote_average REAL,
            genres TEXT,
            trailer_url TEXT,
            instagram_media_id TEXT,
            instagram_code TEXT,
            caption TEXT,
            posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'success',
            error_message TEXT
        )
    """)
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_tmdb_id_type
        ON posts(tmdb_id, media_type)
    """)
    conn.commit()
    conn.close()

def is_already_posted(tmdb_id, media_type="movie"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM posts WHERE tmdb_id = ? AND media_type = ? AND status = 'success'",
        (tmdb_id, media_type)
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None

def record_post(tmdb_id, media_type, title, original_title="", overview="",
                poster_path="", backdrop_path="", release_date="", vote_average=0.0,
                genres="", trailer_url="", instagram_media_id="", instagram_code="",
                caption="", status="success", error_message=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO posts
        (tmdb_id, media_type, title, original_title, overview, poster_path, backdrop_path,
         release_date, vote_average, genres, trailer_url, instagram_media_id, instagram_code,
         caption, posted_at, status, error_message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (tmdb_id, media_type, title, original_title, overview, poster_path, backdrop_path,
          release_date, vote_average, genres, trailer_url, instagram_media_id, instagram_code,
          caption, datetime.now().isoformat(), status, error_message))
    conn.commit()
    conn.close()

def get_posted_count():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM posts WHERE status = 'success'")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def optimize_and_clean_database(days_to_keep=90):
    """Prunes failed logs older than 90 days and vacuums/analyzes to keep SQLite healthy."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM posts WHERE status = 'failed' AND posted_at < datetime('now', ?)", (f"-{days_to_keep} days",))
        conn.execute("VACUUM")
        conn.execute("ANALYZE")
        conn.commit()
        import logging
        logging.getLogger("instagram.database").info("Database vacuumed, indexed and cleaned successfully.")
    except Exception as e:
        import logging
        logging.getLogger("instagram.database").error(f"Database optimization failed: {e}")
    finally:
        conn.close()

init_db()
