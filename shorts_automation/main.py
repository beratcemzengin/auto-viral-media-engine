import logging
import os
import time
import traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler

try:
    from . import config
    from . import script_generator
    from . import voice_subtitle
    from . import video_downloader
    from . import video_editor
    from . import youtube_uploader
    from . import email_notifier
    from . import database
except ImportError:
    import config
    import script_generator
    import voice_subtitle
    import video_downloader
    import video_editor
    import youtube_uploader
    import email_notifier
    import database

log_file = os.path.join(config.LOGS_DIR, "shorts.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("shorts.main")

def clear_old_temp_files(directory, max_age_hours=24):
    """Purges stray rendering temp files older than 24 hours."""
    now = time.time()
    if not os.path.exists(directory):
        return
    for root, _, files in os.walk(directory):
        for file in files:
            path = os.path.join(root, file)
            if os.stat(path).st_mtime < now - (max_age_hours * 3600):
                if file.endswith(('.mp4', '.ts', '.mp3', '.vtt')):
                    try:
                        os.remove(path)
                        logger.info(f"Purged stray temp file: {path}")
                    except Exception:
                        pass

def run_pipeline():
    logger.info("=" * 50)
    logger.info(f"🚀 YouTube Shorts Micro-Doc Engine Started - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    logger.info("=" * 50)
    
    # Clean stray temp files on startup
    clear_old_temp_files(config.DATA_DIR)
    
    # Weekly DB maintenance check
    if datetime.now().weekday() == 6: # Sunday
        logger.info("Running database vacuum and optimization routine...")
        database.optimize_and_clean_database()

    title = "Unknown Title"
    script_file_path = None
    audio_path, vtt_path = None, None
    video_paths = []
    final_video_path = None

    try:
        # 1. Queue Fact Curation
        logger.info("Step 1: Selecting next verified script from queue...")
        script_data = script_generator.generate_script()
        script_file_path = script_data.get("file_path")
        text = script_data["text"]
        title = script_data["title"]
        queries = script_data["search_queries"]
        tags = script_data.get("tags", ["shorts", "infotainment"])
        category = script_data.get("category", "General")
        
        logger.info(f"Title: {title}")
        logger.info(f"Category: {category}")
        logger.info(f"Queries: {queries}")
        
        # 2. Voice & Subtitles
        logger.info("Step 2: Generating voiceover and aligned subtitles...")
        output_prefix = f"short_{int(time.time())}"
        audio_path, vtt_path = voice_subtitle.generate_voice_and_subs(text, output_prefix=output_prefix)
        if not audio_path or not vtt_path:
            err_msg = "Voiceover audio or subtitle VTT generation failed."
            logger.error(err_msg)
            email_notifier.send_notification_email(
                platform_name="YouTube Shorts", 
                status="FAILED", 
                title=title, 
                error_msg=err_msg,
                attachments=[log_file] if os.path.exists(log_file) else None
            )
            return False
            
        # 3. Contextual B-Roll
        logger.info(f"Step 3: Downloading {len(queries)} matching HD B-Roll clips...")
        video_paths = video_downloader.get_multiple_pexels_videos(queries, max_videos=4)
        if not video_paths:
            err_msg = "Failed to download B-Roll scenes from Pexels."
            logger.error(err_msg)
            email_notifier.send_notification_email(
                platform_name="YouTube Shorts", 
                status="FAILED", 
                title=title, 
                error_msg=err_msg,
                attachments=[log_file] if os.path.exists(log_file) else None
            )
            return False
            
        # 4. Multi-Clip Composition
        logger.info("Step 4: Assembling video composition (Transitions + Subtitles + Music)...")
        final_video_name = f"final_{output_prefix}.mp4"
        final_video_path = video_editor.edit_video(video_paths, audio_path, vtt_path, output_filename=final_video_name)
        if not final_video_path:
            err_msg = "FFmpeg composition rendering failed."
            logger.error(err_msg)
            email_notifier.send_notification_email(
                platform_name="YouTube Shorts", 
                status="FAILED", 
                title=title, 
                error_msg=err_msg,
                attachments=[log_file] if os.path.exists(log_file) else None
            )
            return False
            
        # 5. Resumable Upload
        logger.info("Step 5: Uploading video to YouTube...")
        hashtag_str = " ".join([f"#{t.replace(' ', '')}" for t in tags] + ["#shorts", "#documentary", "#viral"])
        full_title = f"{title}"
        if not full_title.endswith("#shorts"):
            full_title = f"{full_title} #shorts"
            
        description = (
            f"{text}\n\n"
            f"🔔 Subscribe for more mysterious and interesting stories!\n\n"
            f"{hashtag_str}"
        )
        
        upload_url = youtube_uploader.upload_video(final_video_path, full_title, description, tags=tags)
        if upload_url:
            logger.info("=" * 50)
            logger.info(f"🎉 SUCCESS! New Shorts published: {upload_url}")
            logger.info("=" * 50)
            
            video_id = upload_url.split("/")[-1]
            
            # Step 6: Commit state and shift script to archive directory
            script_generator.mark_script_as_posted(
                file_path=script_file_path,
                title=title,
                text=text,
                youtube_video_id=video_id,
                youtube_url=upload_url,
                category=category
            )
            
            email_notifier.send_notification_email(
                platform_name="YouTube Shorts",
                status="SUCCESS",
                title=title,
                url=upload_url
            )
            
            # Safe temporary files cleanup
            try:
                if os.path.exists(audio_path): os.remove(audio_path)
                if os.path.exists(vtt_path): os.remove(vtt_path)
                for vp in video_paths:
                    if os.path.exists(vp): os.remove(vp)
                if os.path.exists(final_video_path): os.remove(final_video_path)
                logger.info("Temporary audio and video files purged.")
            except Exception as e:
                logger.warning(f"Temp cleanup warning: {e}")
                
            return True
        else:
            err_msg = "YouTube API returned failure during upload."
            logger.error(err_msg)
            email_notifier.send_notification_email(
                platform_name="YouTube Shorts", 
                status="FAILED", 
                title=title, 
                error_msg=err_msg,
                attachments=[log_file] if os.path.exists(log_file) else None
            )
            return False
            
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"Critical pipeline exception: {tb}")
        email_notifier.send_notification_email(
            platform_name="YouTube Shorts", 
            status="FAILED", 
            title=title, 
            error_msg=f"{str(e)}\n\n{tb}",
            attachments=[log_file] if os.path.exists(log_file) else None
        )
        # Cleanup
        try:
            if audio_path and os.path.exists(audio_path): os.remove(audio_path)
            if vtt_path and os.path.exists(vtt_path): os.remove(vtt_path)
            for vp in video_paths:
                if os.path.exists(vp): os.remove(vp)
            if final_video_path and os.path.exists(final_video_path): os.remove(final_video_path)
        except Exception:
            pass
        return False

if __name__ == "__main__":
    run_pipeline()
