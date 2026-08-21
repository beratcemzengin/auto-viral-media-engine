import os
import logging
from instagrapi import Client
from . import config

logger = logging.getLogger("instagram.poster")

def get_instagram_client():
    cl = Client()
    if os.path.exists(config.IG_SESSION_FILE):
        try:
            cl.load_settings(config.IG_SESSION_FILE)
            cl.login(config.IG_USERNAME, config.IG_PASSWORD)
            logger.info("Instagram oturumu başarıyla yüklendi.")
            return cl
        except Exception as e:
            logger.warning(f"Oturum dosyası geçersiz: {e}")
            
    if not config.IG_USERNAME or not config.IG_PASSWORD:
        raise ValueError("Instagram kullanıcı adı veya şifresi eksik!")
        
    cl.login(config.IG_USERNAME, config.IG_PASSWORD)
    cl.dump_settings(config.IG_SESSION_FILE)
    return cl

def post_reel(video_path, caption):
    if not os.path.exists(video_path):
        logger.error(f"Reel video dosyası bulunamadı: {video_path}")
        return None
        
    try:
        cl = get_instagram_client()
        logger.info(f"Reel Instagram'a yükleniyor: {video_path}")
        media = cl.clip_upload(video_path, caption=caption)
        if media:
            code = media.code
            media_id = media.id
            reel_url = f"https://www.instagram.com/reel/{code}/"
            logger.info(f"Reel başarıyla paylaşıldı: {reel_url}")
            return {
                "media_id": media_id,
                "code": code,
                "url": reel_url
            }
    except Exception as e:
        logger.error(f"Instagram yükleme hatası: {e}")
        
    return None
