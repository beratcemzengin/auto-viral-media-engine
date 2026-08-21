import os
import json
import logging
import shutil
from pathlib import Path
from . import config
from . import database

logger = logging.getLogger("shorts.script")

APPROVED_DIR = Path(config.DATA_DIR) / "approved_scripts"
POSTED_DIR = Path(config.DATA_DIR) / "posted_scripts"

MASTER_VIRAL_STORIES = [
    {
        "id": "story_001_lamborghini",
        "category": "Şirket Savaşları & Rekabet",
        "title": "Bunu Biliyor Muydunuz? Ferrari'nin Aşağıladığı Traktörcü 🏎️ #shorts",
        "text": "Bunu biliyor muydunuz? Dünyanın en ünlü süper spor arabası Lamborghini, aslında bir intikam yüzünden doğdu. 1963 yılında traktör üreticisi Ferruccio Lamborghini, satın aldığı Ferrari'nin debriyajı sürekli bozulunca şikayet etmek için Enzo Ferrari'nin ofisine gitti. Ancak Enzo Ferrari onu tersleyerek, 'Sorun arabada değil sende. Sen sadece traktör sürmeyi bilirsin, bir Ferrari'yi asla kullanamazsın' diyerek kovdu. Bu hakarete öfkelenen Lamborghini, kendi spor otomobil fabrikasını kurdu ve Ferrari'ye meydan okuyan efsanevi süper spor arabaları üretti.",
        "search_queries": [
            "luxury sports car drifting",
            "vintage red sports car driving",
            "angry businessman luxury office",
            "supercar acceleration highway night"
        ],
        "tags": ["bunu biliyor muydunuz", "ferrari", "lamborghini", "otomobil", "intikam", "shorts"]
    },
    {
        "id": "story_002_netflix_blockbuster",
        "category": "Şirket Savaşları & Teknoloji",
        "title": "Bunu Biliyor Muydunuz? 50 Milyon Dolara Alınmayan 300 Milyar Dolarlık Fikir 🎬 #shorts",
        "text": "Bunu biliyor muydunuz? Bir zamanlar dünyanın en büyük film kiralama devi olan Blockbuster, Netflix'i satın alma fırsatını kahkahalarla reddetti. 2000 yılında Netflix'in kurucuları, henüz küçük bir DVD kiralama şirketiyken Blockbuster yönetimine gidip 'Bizi 50 milyon dolara satın alın' teklifinde bulundu. Ancak Blockbuster CEO'su bu teklife gülerek onları kapı dışarı etti. Aradan geçen yıllarda dijital dönüşüme ayak uyduramayan Blockbuster iflas edip tüm mağazalarını kapatırken, Netflix bugün 300 milyar doların üzerinde bir eğlence imparatorluğuna dönüştü.",
        "search_queries": [
            "movie cinema popcorn projector",
            "streaming video server technology",
            "corporate board meeting executive",
            "abandoned empty store closing down"
        ],
        "tags": ["bunu biliyor muydunuz", "netflix", "blockbuster", "milyar dolarlık hata", "iş dünyası", "shorts"]
    },
    {
        "id": "story_003_adidas_puma",
        "category": "Şirket Savaşları & Tarih",
        "title": "Bunu Biliyor Muydunuz? İki Düşman Kardeşin İntikamı 👟 #shorts",
        "text": "Bunu biliyor muydunuz? Dünyanın en büyük iki spor markası Adidas ve Puma, birbirine düşman iki kardeş yüzünden kuruldu. 1940'larda Almanya'da ayakkabı üreten Adolf ve Rudolf Dassler kardeşler, İkinci Dünya Savaşı sırasında büyük bir kavgaya tutuştu. Asla barışmayan kardeşlerden Adolf kasabanın bir yakasında Adidas'ı kurarken, Rudolf diğer yakasında Puma'yı kurdu. Rekabet o kadar büyüdü ki, kasaba halkı bile giydikleri ayakkabı markasına göre birbirleriyle konuşmayı bıraktı.",
        "search_queries": [
            "running athletic sneakers closeup",
            "vintage shoemaker workshop crafting",
            "angry brothers arguing shadow silhouette",
            "modern sports stadium running shoes"
        ],
        "tags": ["bunu biliyor muydunuz", "adidas", "puma", "şirket savaşları", "tarihi olaylar", "shorts"]
    },
    {
        "id": "story_004_yahoo_google",
        "category": "Şirket Savaşları & Teknoloji",
        "title": "Bunu Biliyor Muydunuz? 1 Milyon Dolara Alınmayan Trilyon Dolarlık Fikir 🔍 #shorts",
        "text": "Bunu biliyor muydunuz? Bir şirket, sadece 1 milyon dolarlık bir teklifi reddederek tam 2 trilyon dolar kaybetti. 1998 yılında Google'ın kurucuları Larry Page ve Sergey Brin, geliştirdikleri PageRank arama motorunu dönemin internet devi Yahoo'ya 1 milyon dolara satmak istedi. Ancak Yahoo yönetimi, 'Bizim amacımız kullanıcıları sitemizde uzun süre tutmak, bu algoritma insanları aradıkları şeye çok hızlı ulaştırıyor' diyerek teklifi reddetti. Bugün Google 2 trilyon dolar değerine ulaşırken, Yahoo küçülerek satıldı.",
        "search_queries": [
            "computer code matrix programming screen",
            "vintage 90s server computer laboratory",
            "modern glass skyscraper corporate headquarters",
            "stock market investment charts glowing"
        ],
        "tags": ["bunu biliyor muydunuz", "google", "yahoo", "teknoloji rekabeti", "milyar dolarlık hata", "shorts"]
    },
    {
        "id": "story_005_einstein_brain",
        "category": "Bilim & Gizem",
        "title": "Bunu Biliyor Muydunuz? Einstein'ın Çalınan Beyni 🧠 #shorts",
        "text": "Bunu biliyor muydunuz? Albert Einstein'ın beyni öldüğü gün kafatasından gizlice çalındı. 1955 yılında dahi fizikçinin otopsisini yapan Doktor Thomas Harvey, ailesinden hiçbir izin almadan beyni kavanoza koyup kaçırdı. Harvey, dehanın sırrını çözmek amacıyla beyni tam 40 yıl boyunca arabasının bagajındaki bir bira soğutucusunda saklayarak Amerika'yı dolaştı. Yıllar süren incelemeler sonucunda bulunan tek şey ise, beynin sadece matematiği işleyen bölgesinin sıradan insanlardan yüzde 15 daha geniş olduğuydu.",
        "search_queries": [
            "vintage doctor hospital autopsy",
            "brain medical science jar",
            "driving old car at night highway",
            "creepy laboratory dark test"
        ],
        "tags": ["bunu biliyor muydunuz", "einstein", "bilim", "tarih", "gizem", "shorts"]
    }
]

def _seed_stories():
    APPROVED_DIR.mkdir(parents=True, exist_ok=True)
    POSTED_DIR.mkdir(parents=True, exist_ok=True)
    
    for story in MASTER_VIRAL_STORIES:
        if not database.is_already_posted(story["text"], story["title"]):
            file_path = APPROVED_DIR / f"{story['id']}.json"
            posted_path = POSTED_DIR / f"{story['id']}.json"
            if not file_path.exists() and not posted_path.exists():
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(story, f, ensure_ascii=False, indent=2)

def generate_script() -> dict:
    _seed_stories()
    candidates = sorted(APPROVED_DIR.glob("*.json"))
    
    for path in candidates:
        try:
            with open(path, "r", encoding="utf-8") as f:
                brief = json.load(f)
                
            text = brief.get("text", "")
            title = brief.get("title", "")
            
            if database.is_already_posted(text, title):
                logger.warning(f"Senaryo zaten paylaşıldı, arşive taşınıyor: {path.name}")
                shutil.move(str(path), str(POSTED_DIR / path.name))
                continue
                
            logger.info(f"Seçilen Sıradaki Senaryo: {path.name} ({title})")
            return {
                "file_path": str(path),
                "title": title,
                "text": text,
                "search_queries": brief.get("search_queries", []),
                "category": brief.get("category", "Genel"),
                "tags": brief.get("tags", ["shorts", "ilginçbilgiler"])
            }
        except Exception as e:
            logger.error(f"Dosya okuma hatası {path.name}: {e}")
            continue
            
    raise RuntimeError("Kuyrukta paylaşılmamış yeni senaryo kalmadı!")

def mark_script_as_posted(file_path: str, title: str, text: str, youtube_video_id: str, youtube_url: str, category: str = "Genel"):
    database.record_posted_short(
        title=title,
        text=text,
        youtube_video_id=youtube_video_id,
        youtube_url=youtube_url,
        category=category,
        status="success"
    )
    if file_path and os.path.exists(file_path):
        POSTED_DIR.mkdir(parents=True, exist_ok=True)
        dest = POSTED_DIR / os.path.basename(file_path)
        shutil.move(file_path, str(dest))
