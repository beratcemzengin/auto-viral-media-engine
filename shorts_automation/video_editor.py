import os
import subprocess
import logging
from . import config

try:
    import imageio_ffmpeg
    DEFAULT_FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    DEFAULT_FFMPEG = "ffmpeg"

logger = logging.getLogger("shorts.editor")

def get_font_file():
    if os.name == 'nt':
        win_font = r"C:\Windows\Fonts\arialbd.ttf"
        if os.path.exists(win_font):
            return win_font.replace('\\', '/').replace(':', '\\:')
        return "Arial"
    else:
        return "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def get_audio_duration(audio_path):
    cmd = [DEFAULT_FFMPEG, "-i", audio_path]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
        for line in res.stderr.split("\n"):
            if "Duration:" in line:
                parts = line.split("Duration:")[1].split(",")[0].strip()
                h, m, s = parts.split(":")
                return float(h)*3600 + float(m)*60 + float(s)
    except Exception as e:
        logger.warning(f"Süre tespit hatası: {e}")
    return 45.0

def edit_video(video_paths, audio_path, vtt_path, output_filename=None):
    """
    Çoklu B-Roll sahnelerini birleştirip, ses, altyazı ve logo ile miksler.
    """
    if not video_paths or not os.path.exists(audio_path):
        logger.error("Gerekli video veya ses dosyaları eksik!")
        return None
        
    if not output_filename:
        output_filename = f"final_{os.path.basename(audio_path)}.mp4"
    output_path = os.path.join(config.OUTPUT_DIR, output_filename)
    
    duration = get_audio_duration(audio_path)
    num_clips = len(video_paths)
    clip_dur = duration / num_clips if num_clips > 0 else duration
    
    # FFmpeg komut inşası
    cmd = [DEFAULT_FFMPEG, "-y"]
    
    for vp in video_paths:
        cmd.extend(["-t", f"{clip_dur:.2f}", "-i", vp])
        
    cmd.extend(["-i", audio_path])
    
    # Filter complex
    filter_inputs = ""
    for i in range(num_clips):
        filter_inputs += f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30[v{i}];"
        
    concat_filter = "".join([f"[v{i}]" for i in range(num_clips)]) + f"concat=n={num_clips}:v=1:a=0[vconcat];"
    
    font_file = get_font_file()
    text_filter = (
        f"[vconcat]drawtext=fontfile='{font_file}':text='BUNU BİLİYOR MUYDUNUZ?':"
        f"fontsize=42:fontcolor=#F5C518:shadowcolor=black@0.8:shadowx=2:shadowy=2:"
        f"x=(w-text_w)/2:y=240[vtagged]"
    )
    
    final_filter = filter_inputs + concat_filter + text_filter
    
    cmd.extend([
        "-filter_complex", final_filter,
        "-map", "[vtagged]",
        "-map", f"{num_clips}:a",
        "-t", f"{duration:.2f}",
        "-threads", "0",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        output_path
    ])
    
    logger.info(f"FFmpeg montajı başlatılıyor ({num_clips} sahne, {duration:.1f} sn)...")
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if res.returncode == 0 and os.path.exists(output_path):
            logger.info(f"Montaj tamamlandı: {output_path}")
            return output_path
        else:
            logger.error(f"FFmpeg montaj hatası: {res.stderr[-400:]}")
    except Exception as e:
        logger.error(f"Montaj hatası: {e}")
        
    return None
