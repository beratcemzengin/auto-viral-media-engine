import sqlite3
import os
from datetime import datetime

try:
    from . import config
except ImportError:
    import config

def get_connection():
    os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kids_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            puzzle_type TEXT NOT NULL,
            title TEXT NOT NULL,
            theme_key TEXT UNIQUE NOT NULL,
            youtube_video_id TEXT,
            youtube_url TEXT,
            posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'success',
            error_message TEXT
        )
    """)
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_kids_theme_key
        ON kids_posts(theme_key)
    """)
    conn.commit()
    conn.close()

def is_already_posted(theme_key: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM kids_posts WHERE theme_key = ? AND status = 'success'",
        (theme_key,)
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None

def record_post(puzzle_type: str, title: str, theme_key: str, youtube_video_id: str, youtube_url: str, status: str = "success", error_message: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO kids_posts
        (puzzle_type, title, theme_key, youtube_video_id, youtube_url, posted_at, status, error_message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (puzzle_type, title, theme_key, youtube_video_id, youtube_url, datetime.now().isoformat(), status, error_message))
    conn.commit()
    conn.close()

def optimize_and_clean_database(days_to_keep=90):
    """Prunes failed logs older than 90 days and vacuums to keep SQLite healthy."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM kids_posts WHERE status = 'failed' AND posted_at < datetime('now', ?)", (f"-{days_to_keep} days",))
        conn.execute("VACUUM")
        conn.execute("ANALYZE")
        conn.commit()
        import logging
        logging.getLogger("kids.database").info("Database vacuumed and cleaned successfully.")
    except Exception as e:
        import logging
        logging.getLogger("kids.database").error(f"Database optimization failed: {e}")
    finally:
        conn.close()

init_db()
