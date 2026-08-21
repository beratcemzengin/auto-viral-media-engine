import requests
import random
import logging
from . import config
from . import database

logger = logging.getLogger("instagram.discovery")

GENRE_MAP = {
    28: "Aksiyon", 12: "Macera", 16: "Animasyon", 35: "Komedi", 80: "Suç",
    99: "Belgesel", 18: "Dram", 10751: "Aile", 14: "Fantastik", 36: "Tarih",
    27: "Korku", 10402: "Müzik", 9648: "Gizem", 10749: "Romantik", 878: "Bilim-Kurgu",
    10770: "TV Filmi", 53: "Gerilim", 10752: "Savaş", 37: "Vahşi Batı",
    10759: "Aksiyon & Macera", 10762: "Çocuk", 10763: "Haber", 10764: "Reality",
    10765: "Bilim Kurgu & Fantazi", 10766: "Pembe Dizi", 10767: "Talk Show", 10768: "Savaş & Politik"
}

def get_genre_names(genre_ids):
    if not genre_ids: return "Sinema"
    names = [GENRE_MAP.get(gid, "") for gid in genre_ids if gid in GENRE_MAP]
    return " / ".join(names[:2]) if names else "Sinema"

def fetch_tmdb(endpoint, params=None):
    if not config.TMDB_API_KEY:
        logger.error("TMDB_API_KEY tanımlanmamış!")
        return None
    url = f"{config.TMDB_BASE_URL}/{endpoint}"
    default_params = {"api_key": config.TMDB_API_KEY, "language": "tr-TR"}
    if params: default_params.update(params)
    try:
        res = requests.get(url, params=default_params, timeout=10)
        if res.status_code == 200: return res.json()
    except Exception as e:
        logger.error(f"TMDB istek hatası ({endpoint}): {e}")
    return None

def get_trailer_key(tmdb_id, media_type="movie"):
    data = fetch_tmdb(f"{media_type}/{tmdb_id}/videos")
    if data and "results" in data:
        for vid in data["results"]:
            if vid.get("site") == "YouTube" and vid.get("type") in ["Trailer", "Teaser"]:
                return vid.get("key")
    # Fallback İngilizce
    data_en = fetch_tmdb(f"{media_type}/{tmdb_id}/videos", {"language": "en-US"})
    if data_en and "results" in data_en:
        for vid in data_en["results"]:
            if vid.get("site") == "YouTube" and vid.get("type") in ["Trailer", "Teaser"]:
                return vid.get("key")
    return None

def discover_next_content():
    endpoints = [
        ("trending/movie/week", "movie"),
        ("movie/now_playing", "movie"),
        ("trending/tv/week", "tv"),
        ("movie/upcoming", "movie")
    ]
    random.shuffle(endpoints)
    for ep, media_type in endpoints:
        data = fetch_tmdb(ep)
        if not data or "results" not in data: continue
        results = data["results"]
        random.shuffle(results)
        for item in results:
            tmdb_id = item.get("id")
            if not tmdb_id or database.is_already_posted(tmdb_id, media_type):
                continue
            title = item.get("title") if media_type == "movie" else item.get("name")
            overview = item.get("overview", "")
            if not title: continue
            
            trailer_key = get_trailer_key(tmdb_id, media_type)
            if not trailer_key:
                trailer_key = f"SEARCH:{title} Fragman"
                
            return {
                "tmdb_id": tmdb_id,
                "media_type": media_type,
                "title": title,
                "original_title": item.get("original_title") or item.get("original_name", ""),
                "overview": overview,
                "poster_path": item.get("poster_path", ""),
                "backdrop_path": item.get("backdrop_path", ""),
                "release_date": item.get("release_date") or item.get("first_air_date", ""),
                "vote_average": round(item.get("vote_average", 0.0), 1),
                "genre_ids": item.get("genre_ids", []),
                "genres_str": get_genre_names(item.get("genre_ids", [])),
                "youtube_key": trailer_key
            }
    return None
