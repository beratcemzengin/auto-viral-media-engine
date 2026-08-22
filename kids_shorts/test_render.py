import os
import logging
from kids_shorts import frame_builder, audio_generator, compiler, config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("kids.test")

def run_dry_test():
    logger.info("Starting dry-run test for kids_shorts video compilation...")
    
    # Generate puzzle layout
    monsters_base, differences, positions = frame_builder.build_puzzle_layout()
    bg_color = "#FFF5E4"
    
    temp_audio = os.path.join(config.DATA_DIR, "test_audio.wav")
    test_video = os.path.join(config.OUTPUT_DIR, "test_kids_video.mp4")
    
    # Generate soundtrack
    logger.info("Generating synthesized soundtrack...")
    audio_generator.generate_kids_audio_track(temp_audio)
    
    # Compile video
    logger.info("Compiling final video (this executes FFmpeg via rawvideo pipe)...")
    compiler.compile_quiz_video(
        output_path=test_video,
        monsters_base=monsters_base,
        differences=differences,
        positions=positions,
        audio_path=temp_audio,
        bg_color=bg_color,
        duration=15,
        fps=30
    )
    
    if os.path.exists(test_video):
        logger.info("=======================================================")
        logger.info(f"🎉 DRY-RUN SUCCESSFUL! Test video rendered successfully.")
        logger.info(f"📁 Path: {os.path.abspath(test_video)}")
        logger.info(f"📊 Size: {os.path.getsize(test_video) / 1024 / 1024:.2f} MB")
        logger.info("=======================================================")
    else:
        logger.error("❌ Test video was not generated.")

if __name__ == "__main__":
    run_dry_test()
