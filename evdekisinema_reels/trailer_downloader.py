import os
import subprocess
import logging
import sys
import shutil
from . import config

logger = logging.getLogger("evdekisinema.downloader")

def get_ytdlp_cmd():
    which_yt = shutil.which("yt-dlp")
    if which_yt:
        return [which_yt]
    if os.name == 'nt':
        candidates = [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Python", "Python313", "Scripts", "yt-dlp.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Python", "Python312", "Scripts", "yt-dlp.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Python", "Python311", "Scripts", "yt-dlp.exe"),
            os.path.join(os.environ.get("APPDATA", ""), "Python", "Python313", "Scripts", "yt-dlp.exe"),
        ]
        for c in candidates:
            if os.path.exists(c):
                return [c]
    return [sys.executable, "-m", "yt_dlp"]

def search_youtube_trailer(query):
    ytdlp_base = get_ytdlp_cmd()
    cmd = ytdlp_base + [
        f"ytsearch1:{query}",
        "--get-id",
        "--no-warnings",
        "--no-playlist"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip().split("\n")[0]
    except Exception as e:
        logger.error(f"YouTube arama hatası ({query}): {e}")
    return None

def download_trailer(youtube_key, output_filename=None):
    if not youtube_key:
        return None
    if youtube_key.startswith("SEARCH:"):
        query = youtube_key.replace("SEARCH:", "").strip()
        vid_id = search_youtube_trailer(query)
        if not vid_id: return None
        youtube_key = vid_id
        
    os.makedirs(config.TRAILER_DIR, exist_ok=True)
    if not output_filename:
        output_filename = f"{youtube_key}.mp4"
    output_path = os.path.join(config.TRAILER_DIR, output_filename)
    
    if os.path.exists(output_path) and os.path.getsize(output_path) > 100000:
        return output_path
        
    url = f"https://www.youtube.com/watch?v={youtube_key}"
    ytdlp_base = get_ytdlp_cmd()
    cmd = ytdlp_base + [
        url,
        "-f", "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--merge-output-format", "mp4",
        "-o", output_path,
        "--no-playlist",
        "--no-warnings"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if res.returncode == 0 and os.path.exists(output_path):
            return output_path
    except Exception as e:
        logger.error(f"Fragman indirme hatası: {e}")
    return None
