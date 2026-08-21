# 📖 A-Z Kurulum ve Yapılandırma Rehberi (Setup Guide)

Bu rehber, **Auto Viral Media Engine** projesini sıfırdan kurup 7/24 kesintisiz çalışır hale getirmek isteyen geliştiriciler ve içerik üreticileri için hazırlanmıştır.

---

## 📑 İçindekiler
1. [Sunucu ve Donanım Seçimi](#1-sunucu-ve-donanım-seçimi)
2. [Gerekli API'lerin Alınması](#2-gerekli-apilerin-alınması)
3. [Ubuntu / Debian Sunucu Kurulumu](#3-ubuntu--debian-sunucu-kurulumu)
4. [Windows Kurulumu](#4-windows-kurulumu)
5. [Docker ile Kurulum (Opsiyonel)](#5-docker-ile-kurulum-opsiyonel)
6. [7/24 Otonom Çalışma ve Crontab](#6-724-otonom-çalışma-ve-crontab)
7. [Güvenlik ve Bakım](#7-güvenlik-ve-bakım)

---

## 1. Sunucu ve Donanım Seçimi

Projenin kararlı ve kesintisiz çalışması için aşağıdaki sunucu modellerinden birini tercih edebilirsiniz:

* **Bulut VPS (Önerilen):**
  * **Hetzner Cloud:** CX22 (2 vCPU, 4GB RAM, 40GB SSD) ~ 4€/ay.
  * **DigitalOcean:** Basic Droplet (2 vCPU, 2GB RAM, 50GB SSD) ~ $12/ay.
  * **Contabo:** Cloud VPS S (4 vCPU, 6GB RAM, 100GB SSD) ~ 5.5€/ay.
* **Ev Sunucusu (Sıfır Maliyetli):**
  * Mini PC (Intel N100 / i3 / i5)
  * Raspberry Pi 4 veya 5 (8GB RAM Modeli)
  * CasaOS / Ubuntu Server kurulu eski bir laptop.

---

## 2. Gerekli API'lerin Alınması

### A. Pexels API (Ücretsiz)
1. [Pexels API Sitesine](https://www.pexels.com/api/) gidin.
2. Ücretsiz hesap oluşturun ve **"Your API Key"** sekmesinden anahtarı alın.
3. `.env` içine ekleyin: `PEXELS_API_KEY=your_key`

### B. TMDB API (Ücretsiz)
1. [TheMovieDatabase (TMDB)](https://www.themoviedb.org/) hesabı açın.
2. **Ayarlar > API** sekmesinden ücretsiz *Developer API v3* anahtarı oluşturun.
3. `.env` içine ekleyin: `TMDB_API_KEY=your_key`

### C. YouTube Data API v3 (Google Cloud)
1. [Google Cloud Console](https://console.cloud.google.com/) açın ve yeni bir proje oluşturun.
2. **APIs & Services > Library** aramasında **YouTube Data API v3**'ü etkinleştirin.
3. **OAuth Consent Screen:** User Type = External seçin, test kullanıcılarına kendi Gmail adresinizi ekleyin.
4. **Credentials > Create Credentials > OAuth client ID:** Application Type = Desktop App.
5. JSON dosyasını indirin ve adını `client_secrets.json` yaparak `shorts_automation/` klasörüne koyun.

### D. Instagram Hesabı (instagrapi)
* `.env` dosyasında `INSTAGRAM_USERNAME` ve `INSTAGRAM_PASSWORD` alanlarını tanımlayın.
* Sistem ilk başarılı girişte bir `session.json` dosyası üreterek sonraki isteklerde IP/Challenge sormadan oturumu sürdürür.

---

## 3. Ubuntu / Debian Sunucu Kurulumu

```bash
# 1. Gerekli sistem araçlarını kurun
sudo apt update && sudo apt install -y python3 python3-pip python3-venv ffmpeg fonts-dejavu git curl

# 2. Projeyi klonlayın
cd /opt
sudo git clone https://github.com/beratcemzengin/auto-viral-media-engine.git
sudo chown -R $USER:$USER /opt/auto-viral-media-engine
cd /opt/auto-viral-media-engine

# 3. Python sanal ortamını kurun
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. .env dosyasını yapılandırın
cp .env.example .env
nano .env
```

---

## 4. Windows Kurulumu

1. [Python 3.11 veya 3.12](https://www.python.org/downloads/) indirin (Kurulumda *"Add Python to PATH"* kutucuğunu işaretleyin).
2. [FFmpeg](https://www.gyan.dev/ffmpeg/builds/) indirin ve PATH ortam değişkenine ekleyin.
3. PowerShell terminalini açın:
```powershell
git clone https://github.com/beratcemzengin/auto-viral-media-engine.git
cd auto-viral-media-engine
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

---

## 5. 7/24 Otonom Çalışma ve Crontab

Sunucunuzda `crontab -e` komutunu çalıştırarak zamanlanmış görevleri ekleyin:

```bash
# EvdekiSinema Instagram Reels (09:00 ve 17:00 TSİ)
0 6 * * * /opt/auto-viral-media-engine/venv/bin/python3 /opt/auto-viral-media-engine/evdekisinema_reels/main.py >> /opt/auto-viral-media-engine/evdekisinema_reels/logs/reels.log 2>&1
0 14 * * * /opt/auto-viral-media-engine/venv/bin/python3 /opt/auto-viral-media-engine/evdekisinema_reels/main.py >> /opt/auto-viral-media-engine/evdekisinema_reels/logs/reels.log 2>&1

# YouTube Shorts Mikro-Belgesel (Günde 4 Video: 07:30, 11:00, 17:30, 20:00 TSİ)
30 4 * * * /opt/auto-viral-media-engine/venv/bin/python3 /opt/auto-viral-media-engine/shorts_automation/main.py >> /opt/auto-viral-media-engine/shorts_automation/logs/shorts.log 2>&1
0 8 * * * /opt/auto-viral-media-engine/venv/bin/python3 /opt/auto-viral-media-engine/shorts_automation/main.py >> /opt/auto-viral-media-engine/shorts_automation/logs/shorts.log 2>&1
30 14 * * * /opt/auto-viral-media-engine/venv/bin/python3 /opt/auto-viral-media-engine/shorts_automation/main.py >> /opt/auto-viral-media-engine/shorts_automation/logs/shorts.log 2>&1
0 17 * * * /opt/auto-viral-media-engine/venv/bin/python3 /opt/auto-viral-media-engine/shorts_automation/main.py >> /opt/auto-viral-media-engine/shorts_automation/logs/shorts.log 2>&1

# Haftalık Sistem ve Veritabanı Yedeği (Pazar 03:00 TSİ)
0 0 * * 0 /opt/auto-viral-media-engine/venv/bin/python3 /opt/auto-viral-media-engine/shorts_automation/server_backup_mailer.py >> /opt/auto-viral-media-engine/shorts_automation/logs/backup.log 2>&1
```

---

## 6. Güvenlik ve Bakım

* **Log Takibi:**
  * YouTube Shorts: `tail -f /opt/auto-viral-media-engine/shorts_automation/logs/shorts.log`
  * Instagram Reels: `tail -f /opt/auto-viral-media-engine/evdekisinema_reels/logs/reels.log`
* **Disk Temizliği:** Sistem, her başarılı veya başarısız paylaşımın ardından geçici video ve ses dosyalarını otomatik olarak temizler (`os.remove`).
