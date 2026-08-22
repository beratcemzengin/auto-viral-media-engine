import subprocess
import os
import logging
from . import frame_builder

logger = logging.getLogger("kids.compiler")

def compile_quiz_video(output_path, monsters_base, differences, positions, audio_path, bg_color, duration=15, fps=30):
    """Compiles the quiz video programmatically by rendering frames and piping them to FFmpeg."""
    width, height = 1080, 1920
    temp_silent_video = output_path + ".silent.mp4"
    
    # 1. Start FFmpeg process for visual compilation
    ffmpeg_cmd = [
        'ffmpeg', '-y',
        '-f', 'rawvideo',
        '-pix_fmt', 'rgb24',
        '-s', f'{width}x{height}',
        '-r', str(fps),
        '-i', '-',  # Read from stdin
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-preset', 'ultrafast',
        '-crf', '22',
        temp_silent_video
    ]
    
    logger.info("Starting FFmpeg visual frame compilation...")
    try:
        process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        logger.error(f"Failed to start FFmpeg process: {e}")
        return None
        
    total_frames = duration * fps
    
    # Write frames to pipe
    for frame_idx in range(total_frames):
        try:
            frame_img = frame_builder.render_frame(
                monsters_base=monsters_base,
                differences=differences,
                positions=positions,
                frame_idx=frame_idx,
                total_frames=total_frames,
                bg_color=bg_color
            )
            # Write raw bytes
            process.stdin.write(frame_img.tobytes())
            if frame_idx % 90 == 0:
                logger.info(f"Render progress: {int((frame_idx / total_frames) * 100)}%")
        except Exception as e:
            logger.error(f"Error during frame rendering/writing: {e}")
            process.kill()
            return None
            
    process.stdin.close()
    process.wait()
    logger.info("Visual frames compiled successfully.")

    # 2. Mix visual video with synthesized soundtrack
    if not os.path.exists(audio_path):
        logger.error(f"Audio file not found: {audio_path}")
        return None

    mix_cmd = [
        'ffmpeg', '-y',
        '-i', temp_silent_video,
        '-i', audio_path,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-shortest',
        output_path
    ]
    
    logger.info("Mixing audio track with silent video...")
    try:
        subprocess.run(mix_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        logger.info(f"Final video generated: {output_path}")
    except Exception as e:
        logger.error(f"Audio mixing failed: {e}")
        return None
    finally:
        # Clean up temporary silent video
        if os.path.exists(temp_silent_video):
            try: os.remove(temp_silent_video)
            except: pass
            
    return output_path
