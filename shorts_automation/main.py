import logging
import os
import time
import traceback
from datetime import datetime

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
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("shorts.main")

def run_pipeline():
    logger.info("=" * 50)
    logger.info(f"🚀 YouTube Shorts Mikro-Belgesel Başlatıldı - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    logger.info("=" * 50)
    
    title = "Belirsiz Başlık"
    script_file_path = None
    try:
        # 1. Kuyruktan Doğrulanmış ve Paylaşılmamış Senaryo Seçimi
        logger.info("Adım 1: Kuyruktan benzersiz yeni mikro-belgesel hikayesi seçiliyor...")
        script_data = script_generator.generate_script()
        script_file_path = script_data.get("file_path")
        text = script_data["text"]
        title = script_data["title"]
        queries = script_data["search_queries"]
        tags = script_data.get("tags", ["shorts", "ilginçbilgiler"])
        category = script_data.get("category", "Genel")
        
        logger.info(f"Başlık: {title}")
        logger.info(f"Kategori: {category}")
        logger.info(f"B-Roll Sorguları: {queries}")
        
        # 2. Ses ve Altyazı
        logger.info("Adım 2: Seslendirme ve altyazı oluşturuluyor...")
        output_prefix = f"short_{int(time.time())}"
        audio_path, vtt_path = voice_subtitle.generate_voice_and_subs(text, output_prefix=output_prefix)
        if not audio_path or not vtt_path:
            err_msg = "Seslendirme veya altyazı dosyası oluşturulamadı."
            logger.error(err_msg)
            email_notifier.send_notification_email("YouTube Shorts", "FAILED", title=title, error_msg=err_msg)
            return False
            
        # 3. Çoklu B-Roll Video İndirme
        logger.info(f"Adım 3: {len(queries)} adet konuya özel sinematik B-Roll sahnesi indiriliyor...")
        video_paths = video_downloader.get_multiple_pexels_videos(queries, max_videos=4)
        if not video_paths:
            err_msg = "Pexels üzerinden gerekli B-Roll video sahneleri indirilemedi."
            logger.error(err_msg)
            email_notifier.send_notification_email("YouTube Shorts", "FAILED", title=title, error_msg=err_msg)
            return False
            
        # 4. Çoklu Sahne Montajı
        logger.info("Adım 4: Çoklu sahne montajı yapılıyor (Dinamik Geçişler + Logo + Fon Müziği)...")
        final_video_name = f"final_{output_prefix}.mp4"
        final_video_path = video_editor.edit_video(video_paths, audio_path, vtt_path, output_filename=final_video_name)
        if not final_video_path:
            err_msg = "FFmpeg montaj işlemi başarısız oldu."
            logger.error(err_msg)
            email_notifier.send_notification_email("YouTube Shorts", "FAILED", title=title, error_msg=err_msg)
            return False
            
        # 5. YouTube'a Yükleme
        logger.info("Adım 5: YouTube'a yükleniyor...")
        hashtag_str = " ".join([f"#{t.replace(' ', '')}" for t in tags] + ["#shorts", "#belgesel", "#keşfet", "#viral"])
        full_title = f"{title}"
        if not full_title.endswith("#shorts"):
            full_title = f"{full_title} #shorts"
            
        description = (
            f"{text}\n\n"
            f"🔔 Daha fazla gizemli ve ilginç hikaye için kanala abone olmayı unutmayın!\n\n"
            f"{hashtag_str}"
        )
        
        upload_url = youtube_uploader.upload_video(final_video_path, full_title, description, tags=tags)
        if upload_url:
            logger.info("=" * 50)
            logger.info(f"🎉 BAŞARILI! Yeni Mikro-Belgesel yüklendi: {upload_url}")
            logger.info("=" * 50)
            
            video_id = upload_url.split("/")[-1]
            
            # Adım 6: Senaryoyu Arşive Taşı ve SQLite Veritabanına İşle
            script_generator.mark_script_as_posted(
                file_path=script_file_path,
                title=title,
                text=text,
                youtube_video_id=video_id,
                youtube_url=upload_url,
                category=category
            )
            
            email_notifier.send_notification_email(
                platform="YouTube Shorts",
                status="SUCCESS",
                title=title,
                url=upload_url
            )
            
            # Geçici dosyaları temizle
            try:
                if os.path.exists(audio_path): os.remove(audio_path)
                if os.path.exists(vtt_path): os.remove(vtt_path)
                for vp in video_paths:
                    if os.path.exists(vp): os.remove(vp)
                if os.path.exists(final_video_path): os.remove(final_video_path)
                logger.info("Geçici video/ses dosyaları temizlendi.")
            except Exception as e:
                logger.warning(f"Geçici dosya temizleme uyarısı: {e}")
                
            return True
        else:
            err_msg = "YouTube API video yükleme adımında hata döndürdü."
            logger.error(err_msg)
            email_notifier.send_notification_email("YouTube Shorts", "FAILED", title=title, error_msg=err_msg)
            return False
            
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"Kritik pipeline hatası: {tb}")
        email_notifier.send_notification_email("YouTube Shorts", "FAILED", title=title, error_msg=f"{str(e)}\n\n{tb}")
        return False

if __name__ == "__main__":
    run_pipeline()
