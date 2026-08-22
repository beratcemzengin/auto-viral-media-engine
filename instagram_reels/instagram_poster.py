import os
import logging
from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired, TwoFactorRequired

try:
    from . import config
except ImportError:
    import config

logger = logging.getLogger("instagram.poster")

def get_instagram_client():
    cl = Client()
    session_loaded = False
    
    # 1. Attempt to load and verify existing session without credentials first
    if os.path.exists(config.IG_SESSION_FILE):
        try:
            cl.load_settings(config.IG_SESSION_FILE)
            # Lightweight API call to verify if session is active
            cl.get_timeline_feed()
            session_loaded = True
            logger.info("Instagram session verified and loaded successfully without raw login.")
        except Exception as e:
            logger.warning(f"Saved session is invalid or expired: {e}")
            try:
                os.remove(config.IG_SESSION_FILE)
                logger.info("Removed expired session file.")
            except Exception:
                pass

    # 2. Fallback to password login
    if not session_loaded:
        if not config.IG_USERNAME or not config.IG_PASSWORD:
            raise ValueError("Instagram credentials missing in config!")
        
        logger.info("Performing fresh login with credentials...")
        try:
            cl.login(config.IG_USERNAME, config.IG_PASSWORD)
            cl.dump_settings(config.IG_SESSION_FILE)
            logger.info("Fresh login successful. Session settings saved.")
        except (ChallengeRequired, TwoFactorRequired) as cre:
            logger.critical(f"Instagram Login Challenge Encountered: {cre}")
            raise cre
        except Exception as e:
            logger.error(f"Fresh Instagram login failed: {e}")
            raise e
            
    return cl

def post_reel(video_path, caption):
    if not os.path.exists(video_path):
        logger.error(f"Reel video file not found: {video_path}")
        return None
        
    try:
        cl = get_instagram_client()
        logger.info(f"Uploading Reel to Instagram: {video_path}")
        media = cl.clip_upload(video_path, caption=caption)
        if media:
            code = media.code
            media_id = media.id
            reel_url = f"https://www.instagram.com/reel/{code}/"
            logger.info(f"Reel shared successfully: {reel_url}")
            return {
                "media_id": media_id,
                "code": code,
                "url": reel_url
            }
    except Exception as e:
        logger.error(f"Instagram upload error: {e}")
        
    return None
