import os
import subprocess
import logging
import re
from PIL import Image, ImageDraw
from . import config

try:
    import imageio_ffmpeg
    DEFAULT_FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    DEFAULT_FFMPEG = "ffmpeg"

logger = logging.getLogger("evdekisinema.processor")

def get_font_file():
    if os.name == 'nt':
        win_font = r"C:\Windows\Fonts\arialbd.ttf"
        if os.path.exists(win_font):
            return win_font.replace('\\', '/').replace(':', '\\:')
        return "Arial"
    else:
        if os.path.exists(config.FONT_PATH):
            return config.FONT_PATH
        return "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def get_media_duration(file_path):
    cmd = [DEFAULT_FFMPEG, "-i", file_path]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
        for line in res.stderr.split("\n"):
            if "Duration:" in line:
                parts = line.split("Duration:")[1].split(",")[0].strip()
                h, m, s = parts.split(":")
                return float(h)*3600 + float(m)*60 + float(s)
    except Exception as e:
        logger.warning(f"Süre tespit hatası: {e}")
    return 60.0

def clean_text_for_drawtext(text):
    if not text: return ""
    text = re.sub(r'[^\w\s\-\.\,\:\/\(\)\&\'\"\?\!\+\@\%çğıöşüÇĞİÖŞÜ]', '', str(text))
    text = text.replace("\\", "\\\\").replace("'", "\u2019").replace(":", "\\:").replace("%", "%%").replace("\n", " ").strip()
    return text

def ensure_cinematic_gradient_asset():
    assets_dir = os.path.join(config.DATA_DIR, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    gradient_path = os.path.join(assets_dir, "top_gradient.png")
    
    img = Image.new("RGBA", (1080, 560), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for y in range(560):
        alpha = int(210 * (1 - (y / 560) ** 1.3))
        draw.line([(0, y), (1080, y)], fill=(10, 10, 15, alpha))
        
    img.save(gradient_path, "PNG")
    return gradient_path

def process_trailer_to_reel(input_path, title, hook_text="HAFTANIN EN IYI FILM TAVSIYESI", genres_str="Gerilim", vote_average=7.5, platform_text="Sinemalarda & Dijitalde", output_filename=None, max_duration=90):
    if not input_path or not os.path.exists(input_path):
        logger.error(f"Giriş dosyası bulunamadı: {input_path}")
        return None

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    if not output_filename:
        base = os.path.splitext(os.path.basename(input_path))[0]
        output_filename = f"reel_{base}.mp4"
    output_path = os.path.join(config.OUTPUT_DIR, output_filename)

    ffmpeg_exe = DEFAULT_FFMPEG
    font_file = get_font_file()
    gradient_path = ensure_cinematic_gradient_asset().replace('\\', '/').replace(':', '\\:')

    raw_duration = get_media_duration(input_path)
    start_skip = 5.0 if raw_duration > 20 else 0.0
    effective_duration = raw_duration - start_skip
    final_render_duration = min(effective_duration, max_duration)
    if final_render_duration <= 5:
        final_render_duration = raw_duration
        start_skip = 0.0

    safe_title = clean_text_for_drawtext(title.upper())
    safe_hook = clean_text_for_drawtext(hook_text)
    safe_info = clean_text_for_drawtext(f"IMDb: {vote_average}/10   |   {genres_str}")
    safe_platform = clean_text_for_drawtext(f"Nerede İzlenir: {platform_text}" if platform_text else "Sinemalarda & Dijitalde")
    safe_cta = clean_text_for_drawtext("@evdekisinema   |   Kaydet & Arkadaşına Gönder")

    words = safe_hook.split()
    if len(words) >= 4:
        mid = len(words) // 2
        line1 = " ".join(words[:mid])
        line2 = " ".join(words[mid:])
    else:
        line1 = safe_hook
        line2 = ""

    # Yüksek Performanslı Downscale -> Blur -> Upscale Filtresi (CPU dostu)
    filter_complex = (
        f"[0:v]fps=30,scale=270:480:force_original_aspect_ratio=increase,crop=270:480,"
        f"boxblur=8:1,scale=1080:1920,colorchannelmixer=rr=0.4:gg=0.4:bb=0.4[bg];"
        
        f"[0:v]fps=30,scale=1080:608:force_original_aspect_ratio=decrease,pad=1080:608:(ow-iw)/2:(oh-ih)/2:black[fg];"
        
        f"[bg][fg]overlay=0:580[composed];"
        
        f"movie='{gradient_path}'[grad];"
        f"[composed][grad]overlay=0:0[with_grad];"
        
        f"[with_grad]drawtext=fontfile='{font_file}':text='{line1}':fontsize=48:fontcolor=white:"
        f"shadowcolor=black@0.9:shadowx=3:shadowy=4:borderw=1:bordercolor=black@0.5:"
        f"x=(w-text_w)/2:y=280,"
        f"drawtext=fontfile='{font_file}':text='{line2}':fontsize=48:fontcolor=#F5C518:"
        f"shadowcolor=black@0.9:shadowx=3:shadowy=4:borderw=1:bordercolor=black@0.5:"
        f"x=(w-text_w)/2:y=350,"
        
        f"drawbox=x=60:y=1220:w=960:h=90:color=black@0.75:t=fill,"
        f"drawbox=x=60:y=1220:w=960:h=90:color=white@0.15:t=2,"
        f"drawtext=fontfile='{font_file}':text='{safe_title}':fontsize=44:fontcolor=white:"
        f"x=(w-text_w)/2:y=1220+(90-text_h)/2,"
        
        f"drawbox=x=60:y=1320:w=960:h=70:color=black@0.65:t=fill,"
        f"drawtext=fontfile='{font_file}':text='{safe_info}':fontsize=32:fontcolor=#F5C518:"
        f"x=(w-text_w)/2:y=1320+(70-text_h)/2,"
        
        f"drawbox=x=60:y=1400:w=960:h=70:color=black@0.65:t=fill,"
        f"drawtext=fontfile='{font_file}':text='{safe_platform}':fontsize=28:fontcolor=white@0.9:"
        f"x=(w-text_w)/2:y=1400+(70-text_h)/2,"
        
        f"drawbox=x=0:y=1740:w=1080:h=90:color=black@0.85:t=fill,"
        f"drawtext=fontfile='{font_file}':text='{safe_cta}':fontsize=30:fontcolor=white@0.95:"
        f"x=(w-text_w)/2:y=1740+(90-text_h)/2[out_v]"
    )

    cmd = [
        ffmpeg_exe, "-y",
        "-ss", f"{start_skip:.1f}",
        "-i", input_path,
        "-t", f"{final_render_duration:.1f}",
        "-filter_complex", filter_complex,
        "-map", "[out_v]",
        "-map", "0:a?",
        "-threads", "0",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "21",
        "-c:a", "aac",
        "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        output_path
    ]

    logger.info(f"Tam Fragman Sinematik Kurgu başlıyor: {title} (Süre: {final_render_duration:.1f}s)")
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if res.returncode == 0 and os.path.exists(output_path):
            logger.info(f"Reel başarıyla üretildi: {output_path}")
            return output_path
        else:
            logger.error(f"FFmpeg hatası: {res.stderr[-400:]}")
    except Exception as e:
        logger.error(f"Video işleme hatası: {e}")
    return None
