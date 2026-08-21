# 🏛️ Technical Architecture & Internal Engine Design

This document details the modular architecture, data pipelines, and video rendering optimizations powering the **Auto Viral Media Engine**.

---

## 1. Pipeline Execution Flow

### YouTube Shorts Engine
1. `script_generator.py` queries the queue for the oldest verified brief.
2. `database.is_already_posted(text)` performs a SHA-256 hash check to verify deduplication.
3. `voice_subtitle.py` streams Microsoft Edge-TTS via WebSocket to generate human-like audio and timed `.vtt` subtitles.
4. `video_downloader.py` requests 4 contextual vertical HD video clips from Pexels API.
5. `video_editor.py` executes an FFmpeg filter chain (scale to 1080x1920, concatenate clips, duck background audio, overlay gold branding badge).
6. `youtube_uploader.py` uploads the final MP4 using YouTube Data API v3 resumable chunking.
7. Upon success, the script JSON is migrated to `posted_scripts/` and indexed in `posted_shorts.db`.

---

## 2. FFmpeg Performance Optimizations

Generating blurred background canvas on 1080x1920 video can severely throttle single-threaded CPUs. To maximize rendering speed, the engine implements a **Downscale-Blur-Upscale** pipeline:

```text
[0:v] -> Downscale to 270x480 -> Apply boxblur=8:1 -> Upscale to 1080x1920 -> Overlay under main 16:9 trailer
```

This reduces pixel blur computation by ~90%, cutting render times from **3+ minutes down to 25–35 seconds** on modest 2-core cloud VPS nodes.

---

## 3. SQLite Database Schemas

### `posted_shorts.db` (YouTube Pipeline)
```sql
CREATE TABLE posted_shorts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    text_hash TEXT UNIQUE NOT NULL,
    youtube_video_id TEXT,
    youtube_url TEXT,
    category TEXT,
    posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'success',
    error_message TEXT
);
CREATE UNIQUE INDEX idx_shorts_text_hash ON posted_shorts(text_hash);
```

### `posted.db` (Instagram Pipeline)
```sql
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tmdb_id INTEGER NOT NULL,
    media_type TEXT NOT NULL DEFAULT 'movie',
    title TEXT NOT NULL,
    vote_average REAL,
    genres TEXT,
    instagram_code TEXT,
    posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'success'
);
CREATE UNIQUE INDEX idx_tmdb_id_type ON posts(tmdb_id, media_type);
```
