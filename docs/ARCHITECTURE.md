# 🏛️ Sistem Mimarisi ve Teknik Tasarım (Architecture)

Bu belge, **Auto Viral Media Engine**'in modüler mimarisini, veri akışını ve video işleme algoritmalarını detaylandırır.

---

## 1. Veri Akışı ve Durum Yönetimi (State Machine)

### YouTube Shorts Akışı
1. `script_generator.py` kuyruktaki en eski doğrulanmış JSON dosyasını okur.
2. `database.is_already_posted(text)` fonksiyonu SHA-256 hash kontrolü yapar.
3. `voice_subtitle.py` Microsoft Edge-TTS WebSocket üzerinden nöral ses ve senkronize `.vtt` üretir.
4. `video_downloader.py` Pexels API'den 4 adet dikey HD video çeker.
5. `video_editor.py` FFmpeg ile sahneleri birleştirir, 1080x1920'ye ölçekler ve marka logosunu ekler.
6. `youtube_uploader.py` Google API ile videoyu kanala yükler.
7. Yükleme başarılıysa dosya `posted_scripts/` klasörüne taşınır ve `posted_shorts.db` içine işlenir.

---

## 2. FFmpeg Optimizasyonları (Hızlı Render)

Instagram Reels fragman işleme sürecinde video arka planı bulanıklaştırılırken doğrudan 1080p üzerinden filtre uygulamak CPU'yu kilitler. Bu nedenle **Downscale-Blur-Upscale** tekniği uygulanmıştır:

```text
[0:v] -> 270x480'e küçült -> boxblur=8:1 uygula -> 1080x1920'ye büyüt -> Koyu arka plan olarak yerleştir
```

Bu yöntem sayesinde render süresi **3 dakikadan 25 saniyeye** düşürülmüştür.

---

## 3. Veritabanı Şeması (SQLite)

### `posted_shorts.db`
```sql
CREATE TABLE posted_shorts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    text_hash TEXT UNIQUE NOT NULL,
    youtube_video_id TEXT,
    youtube_url TEXT,
    category TEXT,
    posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'success',
    error_message TEXT
);
```

### `posted.db` (Instagram)
```sql
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tmdb_id INTEGER NOT NULL,
    media_type TEXT NOT NULL DEFAULT 'movie',
    title TEXT NOT NULL,
    vote_average REAL,
    genres TEXT,
    instagram_code TEXT,
    posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'success'
);
```
