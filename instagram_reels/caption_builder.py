def build_caption(item):
    title = item.get("title", "")
    overview = item.get("overview", "")
    vote_average = item.get("vote_average", 0.0)
    genres_str = item.get("genres_str", "")
    media_type = "Dizi" if item.get("media_type") == "tv" else "Film"
    
    caption = (
        f"🍿 {title} ({media_type})\n\n"
        f"⭐ IMDb: {vote_average}/10 | 🎭 Tür: {genres_str}\n\n"
        f"📝 Konusu:\n{overview[:300]}...\n\n"
        f"📌 Bu yapımı izlemeyi düşündüğün arkadaşına gönder veya listene kaydet!\n\n"
        f"👉 Daha fazla film ve dizi önerisi için @reels_cinema hesabını takip et!\n\n"
        f"#film #dizi #filmtavsiyesi #dizitavsiyesi #sinema #movie_reels #netflix #primevideo #reels #keşfet"
    )
    return caption
