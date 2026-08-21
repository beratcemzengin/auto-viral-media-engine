import os
import requests
import random
import logging
from . import config

logger = logging.getLogger("shorts.video")

def get_pexels_video(query, duration=15):
    """Pexels API üzerinden dikey video arar ve indirir."""
    if not config.PEXELS_API_KEY:
        logger.error("PEXELS_API_KEY tanımlanmamış!")
        return None
        
    url = f"https://api.pexels.com/videos/search?query={query}&orientation=portrait&per_page=15&size=medium"
    headers = {"Authorization": config.PEXELS_API_KEY}
    
    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code == 200:
            data = res.json()
            videos = data.get("videos", [])
            if not videos:
                return None
                
            selected_video = random.choice(videos[:5])
            video_files = selected_video.get("video_files", [])
            
            hd_files = [f for f in video_files if f.get("width", 0) >= 720 and f.get("link")]
            if not hd_files:
                hd_files = video_files
                
            download_url = hd_files[0]["link"]
            video_path = os.path.join(config.DATA_DIR, f"bg_clip_{random.randint(1000, 9999)}.mp4")
            
            with requests.get(download_url, stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(video_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        
            return video_path
    except Exception as e:
        logger.error(f"Pexels indirme hatası ({query}): {e}")
        
    return None

def get_multiple_pexels_videos(queries, max_videos=4):
    """Çoklu sorgu ile farklı B-Roll klipleri indirir."""
    video_paths = []
    for i, q in enumerate(queries[:max_videos]):
        logger.info(f"Pexels B-Roll araması [{i+1}/{min(len(queries), max_videos)}]: {q}")
        vp = get_pexels_video(q)
        if vp:
            video_paths.append(vp)
            
    return video_paths
