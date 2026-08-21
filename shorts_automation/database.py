import sqlite3
import os
import hashlib
from datetime import datetime
from . import config

DB_PATH = os.path.join(config.DATA_DIR, "posted_shorts.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posted_shorts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            text_hash TEXT UNIQUE NOT NULL,
            youtube_video_id TEXT,
            youtube_url TEXT,
            category TEXT,
            posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'success',
            error_message TEXT
        )
    """)
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_shorts_text_hash
        ON posted_shorts(text_hash)
    """)
    conn.commit()
    conn.close()

def compute_text_hash(text: str) -> str:
    """Computes unique SHA-256 hash of normalized text."""
    clean = " ".join(text.strip().lower().split())
    return hashlib.sha256(clean.encode('utf-8')).hexdigest()

def is_already_posted(text: str, title: str = "") -> bool:
    """Checks if text or title was already published."""
    t_hash = compute_text_hash(text)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM posted_shorts WHERE (text_hash = ? OR title = ?) AND status = 'success'",
        (t_hash, title)
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None

def record_posted_short(title: str, text: str, youtube_video_id: str, youtube_url: str, category: str = "General", status: str = "success", error_message: str = None):
    """Records a published video to database."""
    t_hash = compute_text_hash(text)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO posted_shorts
        (title, text_hash, youtube_video_id, youtube_url, category, posted_at, status, error_message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (title, t_hash, youtube_video_id, youtube_url, category, datetime.now().isoformat(), status, error_message))
    conn.commit()
    conn.close()

def get_posted_count() -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM posted_shorts WHERE status = 'success'")
    count = cursor.fetchone()[0]
    conn.close()
    return count

init_db()
