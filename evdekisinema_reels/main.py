import logging
import os
import sys
import traceback
from datetime import datetime

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
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("evdekisinema.main")

def run_pipeline():
    logger.info("=" * 60)
    logger.info(f"🎬 EvdekiSinema Reels Otomasyonu Başlatıldı - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    logger.info("=" * 60)

    for attempt in range(1, 4):
        logger.info(f"\n--- DENEME {attempt}/3 ---")
        item = None
        trailer_path = None
        reel_path = None
        try:
            # 1. İçerik Keşfi
            logger.info("Adım 1/6: TMDB üzerinden içerik keşfediliyor...")
            item = movie_discovery.discover_next_content()
            if not item:
                logger.warning("Uygun içerik bulunamadı.")
                continue

            logger.info(f"✅ Seçilen: [{item['media_type'].upper()}] {item['title']} (IMDb: {item['vote_average']})")

            # 2. Fragman İndirme
            logger.info("Adım 2/6: Fragman indiriliyor...")
            trailer_path = trailer_downloader.download_trailer(item["youtube_key"])
            if not trailer_path or not os.path.exists(trailer_path):
                logger.warning("Fragman indirilemedi.")
                continue

            # 3. Kanca ve Video İşleme
            logger.info("Adım 3/6: Sinematik Reels montajı yapılıyor...")
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
                logger.warning("Video işleme başarısız.")
                continue

            # 4. Caption Hazırlama
            logger.info("Adım 4/6: Açıklama ve hashtagler hazırlanıyor...")
            caption = caption_builder.build_caption(item)

            # 5. Instagram'a Yükleme
            logger.info("Adım 5/6: Instagram Reels'e yükleniyor...")
            upload_result = instagram_poster.post_reel(reel_path, caption)
            if upload_result:
                # 6. Veritabanına Kaydet
                logger.info("Adım 6/6: Veritabanına kaydediliyor...")
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
                    platform="Instagram Reels",
                    status="SUCCESS",
                    title=f"{item['title']} ({item['media_type'].upper()})",
                    url=upload_result.get("url", "")
                )

                logger.info("🎉 BAŞARILI! Reel paylaşıldı.")
                return True
            else:
                logger.warning("Instagram yüklemesi başarısız.")

        except Exception as e:
            tb = traceback.format_exc()
            logger.error(f"Deneme hatası: {tb}")

        finally:
            # Geçici dosyaları temizle
            if trailer_path and os.path.exists(trailer_path):
                try: os.remove(trailer_path)
                except: pass
            if reel_path and os.path.exists(reel_path):
                try: os.remove(reel_path)
                except: pass

    email_notifier.send_notification_email(
        platform="Instagram Reels",
        status="FAILED",
        title="Tüm denemeler tükendi",
        error_msg="3 deneme sonucunda paylaşım yapılamadı."
    )
    return False

if __name__ == "__main__":
    run_pipeline()
