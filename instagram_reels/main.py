import logging
import os
import sys
import time
import traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler

try:
    from . import config
    from . import database
    from . import movie_discovery
    from . import trailer_downloader
    from . import hook_generator
    from . import video_processor
    from . import caption_builder
    from . import instagram_poster
    from . import email_notifier
except ImportError:
    import config
    import database
    import movie_discovery
    import trailer_downloader
    import hook_generator
    import video_processor
    import caption_builder
    import instagram_poster
    import email_notifier

log_file = os.path.join(config.LOGS_DIR, "reels.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("instagram.main")

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
    logger.info("=" * 60)
    logger.info(f"🎬 Instagram Reels Automation Started - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    logger.info("=" * 60)

    # Clean stray temp files on startup
    clear_old_temp_files(config.DATA_DIR)
    
    # Weekly DB maintenance check
    if datetime.now().weekday() == 6: # Sunday
        logger.info("Running database vacuum and optimization routine...")
        database.optimize_and_clean_database()

    last_error_traceback = ""
    for attempt in range(1, 4):
        logger.info(f"\n--- ATTEMPT {attempt}/3 ---")
        item = None
        trailer_path = None
        reel_path = None
        try:
            # 1. Content Discovery
            logger.info("Step 1/6: Discovering movie/show from TMDB...")
            item = movie_discovery.discover_next_content()
            if not item:
                logger.warning("No suitable trending movies found.")
                continue

            logger.info(f"Selected: [{item['media_type'].upper()}] {item['title']} (IMDb: {item['vote_average']})")

            # 2. Download Trailer
            logger.info("Step 2/6: Downloading trailer...")
            trailer_path = trailer_downloader.download_trailer(item["youtube_key"])
            if not trailer_path or not os.path.exists(trailer_path):
                logger.warning("Failed to download trailer video.")
                continue

            # 3. Process Video
            logger.info("Step 3/6: Generating cinematic 9:16 vertical render...")
            hook_text = hook_generator.generate_viral_hook(item["genres_str"], item["vote_average"])
            reel_path = video_processor.process_trailer_to_reel(
                input_path=trailer_path,
                title=item["title"],
                hook_text=hook_text,
                genres_str=item["genres_str"],
                vote_average=item["vote_average"],
                max_duration=config.MAX_REEL_DURATION
            )
            if not reel_path or not os.path.exists(reel_path):
                logger.warning("Failed to render final vertical Reels video.")
                continue

            # 4. Prepare Caption
            logger.info("Step 4/6: Building tags and caption...")
            caption = caption_builder.build_caption(item)

            # 5. Publish to Instagram
            logger.info("Step 5/6: Publishing to Instagram Reels...")
            upload_result = instagram_poster.post_reel(reel_path, caption)
            if upload_result:
                # 6. Database Commit
                logger.info("Step 6/6: Logging success in database...")
                database.record_post(
                    tmdb_id=item["tmdb_id"],
                    media_type=item["media_type"],
                    title=item["title"],
                    original_title=item["original_title"],
                    overview=item["overview"],
                    poster_path=item["poster_path"],
                    backdrop_path=item["backdrop_path"],
                    release_date=item["release_date"],
                    vote_average=item["vote_average"],
                    genres=item["genres_str"],
                    trailer_url=item["youtube_key"],
                    instagram_media_id=upload_result.get("media_id", ""),
                    instagram_code=upload_result.get("code", ""),
                    caption=caption,
                    status="success"
                )

                email_notifier.send_notification_email(
                    platform_name="Instagram Reels",
                    status="SUCCESS",
                    title=f"{item['title']} ({item['media_type'].upper()})",
                    url=upload_result.get("url", "")
                )

                logger.info("🎉 SUCCESS! Reel shared on Instagram.")
                return True
            else:
                logger.warning("Instagram upload step failed.")

        except Exception as e:
            last_error_traceback = traceback.format_exc()
            logger.error(f"Attempt error: {last_error_traceback}")

        finally:
            # Clean temp files
            if trailer_path and os.path.exists(trailer_path):
                try: os.remove(trailer_path)
                except: pass
            if reel_path and os.path.exists(reel_path):
                try: os.remove(reel_path)
                except: pass

    # If all attempts failed, send diagnostic alert
    email_notifier.send_notification_email(
        platform_name="Instagram Reels",
        status="FAILED",
        title="All Attempts Exhausted",
        error_msg=f"Failed to post to Instagram after 3 attempts.\n\nTraceback:\n{last_error_traceback}",
        attachments=[log_file] if os.path.exists(log_file) else None
    )
    return False

if __name__ == "__main__":
    run_pipeline()
