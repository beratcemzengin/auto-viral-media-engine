import logging
import os
import sys
import time
import hashlib
import json
import random
import traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Setup path fallback
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from kids_shorts import config
    from kids_shorts import database
    from kids_shorts import frame_builder
    from kids_shorts import audio_generator
    from kids_shorts import compiler
except ImportError:
    import config
    import database
    import frame_builder
    import audio_generator
    import compiler

# Safe import for uploader and notifier (supports flat server layout and nested repo layout)
try:
    from shorts_automation import youtube_uploader
    from shorts_automation import email_notifier
except ImportError:
    try:
        import youtube_uploader
        import email_notifier
    except ImportError:
        raise ImportError("Could not find youtube_uploader or email_notifier modules.")

log_file = os.path.join(config.LOGS_DIR, "kids_shorts.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("kids.main")

def generate_theme_hash(monsters, differences):
    """Generates a unique SHA-256 hash for the puzzle configuration to prevent duplicate uploads."""
    payload = {
        "monsters": [
            {
                "body_color": m["body_color"],
                "body_type": m["body_type"],
                "eye_type": m["eye_type"],
                "mouth_type": m["mouth_type"],
                "accessory": m["accessory"]
            } for m in monsters
        ],
        "differences": [
            {
                "monster_idx": d["monster_idx"],
                "type": d["type"],
                "new_val": d["new_val"]
            } for d in differences
        ]
    }
    dumped = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(dumped.encode('utf-8')).hexdigest()

def run_pipeline():
    logger.info("=" * 60)
    logger.info(f"🍼 Kids Interactive Shorts Pipeline Started - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    logger.info("=" * 60)

    # 1. Weekly DB cleanup check on Sunday
    if datetime.now().weekday() == 6:
        logger.info("Running database vacuum and optimization...")
        database.optimize_and_clean_database()

    temp_audio_path = os.path.join(config.DATA_DIR, f"temp_kids_{int(time.time())}.wav")
    final_video_path = os.path.join(config.OUTPUT_DIR, f"kids_spot_diff_{int(time.time())}.mp4")
    
    try:
        # 2. Select Unique Puzzle Layout
        logger.info("Step 1: Generating randomized puzzle configurations...")
        monsters_base, differences, positions = frame_builder.build_puzzle_layout()
        theme_key = generate_theme_hash(monsters_base, differences)
        
        # Check database to prevent duplicates
        if database.is_already_posted(theme_key):
            logger.warning("This puzzle layout has already been published. Regenerating next turn...")
            return False

        bg_color = random.choice(config.KIDS_COLORS)
        logger.info(f"Puzzle generated (Differences target indices: {[d['monster_idx'] for d in differences]})")
        logger.info(f"Unique Theme Key: {theme_key}")

        # 3. Generate Audio Track
        logger.info("Step 2: Synthesizing kids background music and SFX...")
        audio_generator.generate_kids_audio_track(temp_audio_path)
        logger.info(f"Audio track ready: {temp_audio_path}")

        # 4. Compile Video
        logger.info("Step 3: Rendering frames and compiling final video...")
        compiler.compile_quiz_video(
            output_path=final_video_path,
            monsters_base=monsters_base,
            differences=differences,
            positions=positions,
            audio_path=temp_audio_path,
            bg_color=bg_color
        )
        
        if not os.path.exists(final_video_path):
            raise FileNotFoundError("Final compiled video not found on disk.")

        # 5. Upload to YouTube (with COPPA Made For Kids flag set to True)
        logger.info("Step 4: Uploading video to YouTube (Made For Kids = True)...")
        title = "SPOT THE DIFFERENCE! 👁️ Can you find all 3 differences? 🧸 #shorts"
        description = (
            "Spot the 3 differences before the timer runs out! ⏰\n\n"
            "Comment below how many differences you found! 💬\n\n"
            "🔔 Subscribe for more fun puzzles, riddles, and kids quizzes!\n\n"
            "#shorts #spotthedifference #kidsgames #puzzles #children #viral"
        )
        tags = ["shorts", "spotthedifference", "kidsgames", "puzzles", "quizzes", "kids", "interactive"]
        
        # Temporary config overrides to use the kids channel's tokens
        youtube_uploader.config.CREDENTIALS_FILE = config.CREDENTIALS_FILE
        youtube_uploader.config.CLIENT_SECRETS_FILE = config.CLIENT_SECRETS_FILE

        # Call uploader with made_for_kids=True
        upload_url = youtube_uploader.upload_video(
            video_path=final_video_path,
            title=title,
            description=description,
            tags=tags,
            made_for_kids=True
        )
        
        if upload_url:
            logger.info("=" * 60)
            logger.info(f"🎉 SUCCESS! Kids Quiz published: {upload_url}")
            logger.info("=" * 60)
            
            video_id = upload_url.split("/")[-1]
            
            # Step 6: Log success to database
            database.record_post(
                puzzle_type="Spot the Difference",
                title=title,
                theme_key=theme_key,
                youtube_video_id=video_id,
                youtube_url=upload_url,
                status="success"
            )
            
            email_notifier.send_notification_email(
                platform_name="YouTube Kids Shorts",
                status="SUCCESS",
                title=title,
                url=upload_url
            )
            
            # Cleanup temp files
            try:
                if os.path.exists(temp_audio_path): os.remove(temp_audio_path)
                if os.path.exists(final_video_path): os.remove(final_video_path)
                logger.info("Temporary visual/audio assets cleaned.")
            except Exception as e:
                logger.warning(f"Temp files cleanup warning: {e}")
                
            return True
        else:
            err_msg = "YouTube upload failed."
            logger.error(err_msg)
            email_notifier.send_notification_email(
                platform_name="YouTube Kids Shorts",
                status="FAILED",
                title=title,
                error_msg=err_msg,
                attachments=[log_file] if os.path.exists(log_file) else None
            )
            return False

    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"Critical kids pipeline error: {tb}")
        email_notifier.send_notification_email(
            platform_name="YouTube Kids Shorts",
            status="FAILED",
            title="Kids Pipeline Crash",
            error_msg=f"{str(e)}\n\n{tb}",
            attachments=[log_file] if os.path.exists(log_file) else None
        )
        # Cleanup
        try:
            if os.path.exists(temp_audio_path): os.remove(temp_audio_path)
            if os.path.exists(final_video_path): os.remove(final_video_path)
        except Exception:
            pass
        return False

if __name__ == "__main__":
    run_pipeline()
