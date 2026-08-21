# 📖 A-Z Setup & Deployment Guide

This guide provides step-by-step instructions for deploying and configuring the **Auto Viral Media Engine** from scratch on Linux (Ubuntu / Debian) and Windows.

---

## 📑 Table of Contents
1. [Server & Hardware Requirements](#1-server--hardware-requirements)
2. [Obtaining Required API Credentials](#2-obtaining-required-api-credentials)
3. [Ubuntu / Debian Server Setup](#3-ubuntu--debian-server-setup)
4. [Windows 10/11 Setup](#4-windows-1011-setup)
5. [24/7 Automation & Crontab](#5-247-automation--crontab)
6. [Monitoring & Maintenance](#6-monitoring--maintenance)

---

## 1. Server & Hardware Requirements

* **Cloud VPS (Recommended):**
  * **Hetzner Cloud:** CX22 (2 vCPU, 4GB RAM, 40GB SSD) ~ 4€/mo.
  * **DigitalOcean:** Basic Droplet (2 vCPU, 2GB RAM, 50GB SSD) ~ $12/mo.
  * **Contabo:** Cloud VPS S (4 vCPU, 6GB RAM, 100GB SSD) ~ 5.5€/mo.
* **Home Server / Bare Metal:**
  * Mini PC (Intel N100 / Core i3 / i5)
  * Raspberry Pi 4 or 5 (8GB RAM Model)
  * CasaOS / Debian Home Server.

---

## 2. Obtaining Required API Credentials

### A. Pexels API Key (Free)
1. Go to [pexels.com/api](https://www.pexels.com/api/) and create a free account.
2. Under **"Your API Key"**, copy your secret key.
3. Add to `.env`: `PEXELS_API_KEY=your_key`

### B. TMDB API Key (Free)
1. Register at [themoviedb.org](https://www.themoviedb.org/).
2. Navigate to **Settings > API** and request a free *Developer API v3* key.
3. Add to `.env`: `TMDB_API_KEY=your_key`

### C. YouTube Data API v3 (Google Cloud)
1. Open [Google Cloud Console](https://console.cloud.google.com/) and create a new project.
2. Enable **YouTube Data API v3** in **APIs & Services > Library**.
3. Under **OAuth Consent Screen**, select *External* and add your Google account email as a test user.
4. Under **Credentials > Create Credentials**, select **OAuth client ID** (Application Type: *Desktop App*).
5. Download the JSON file, rename it to `client_secrets.json`, and place it in the `shorts_automation/` folder.

### D. Instagram Credentials (instagrapi)
* Set `INSTAGRAM_USERNAME` and `INSTAGRAM_PASSWORD` in `.env`.
* The system automatically generates a persistent `session.json` upon first login to avoid checkpoint challenges.

---

## 3. Ubuntu / Debian Server Setup

```bash
# 1. Install system tools and FFmpeg
sudo apt update && sudo apt install -y python3 python3-pip python3-venv ffmpeg fonts-dejavu git curl

# 2. Clone repository
cd /opt
sudo git clone https://github.com/beratcemzengin/auto-viral-media-engine.git
sudo chown -R $USER:$USER /opt/auto-viral-media-engine
cd /opt/auto-viral-media-engine

# 3. Create Python virtual environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. Configure .env file
cp .env.example .env
nano .env
```

---

## 4. Windows 10/11 Setup

1. Install [Python 3.11 or 3.12](https://www.python.org/downloads/) (Check *"Add Python to PATH"* during installation).
2. Install [FFmpeg](https://www.gyan.dev/ffmpeg/builds/) and add its `bin` folder to the system PATH.
3. Open PowerShell:
```powershell
git clone https://github.com/beratcemzengin/auto-viral-media-engine.git
cd auto-viral-media-engine
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

---

## 5. 24/7 Automation & Crontab

Configure the crontab schedule on your Linux server using `crontab -e`:

```bash
# Instagram Reels (Daily at 09:00 & 17:00 TR Time / 06:00 & 14:00 UTC)
0 6 * * * /opt/auto-viral-media-engine/venv/bin/python3 /opt/auto-viral-media-engine/instagram_reels/main.py >> /opt/auto-viral-media-engine/instagram_reels/logs/reels.log 2>&1
0 14 * * * /opt/auto-viral-media-engine/venv/bin/python3 /opt/auto-viral-media-engine/instagram_reels/main.py >> /opt/auto-viral-media-engine/instagram_reels/logs/reels.log 2>&1

# YouTube Shorts (4 Times Daily: 07:30, 11:00, 17:30, 20:00 TR Time)
30 4 * * * /opt/auto-viral-media-engine/venv/bin/python3 /opt/auto-viral-media-engine/shorts_automation/main.py >> /opt/auto-viral-media-engine/shorts_automation/logs/shorts.log 2>&1
0 8 * * * /opt/auto-viral-media-engine/venv/bin/python3 /opt/auto-viral-media-engine/shorts_automation/main.py >> /opt/auto-viral-media-engine/shorts_automation/logs/shorts.log 2>&1
30 14 * * * /opt/auto-viral-media-engine/venv/bin/python3 /opt/auto-viral-media-engine/shorts_automation/main.py >> /opt/auto-viral-media-engine/shorts_automation/logs/shorts.log 2>&1
0 17 * * * /opt/auto-viral-media-engine/venv/bin/python3 /opt/auto-viral-media-engine/shorts_automation/main.py >> /opt/auto-viral-media-engine/shorts_automation/logs/shorts.log 2>&1

# Weekly System & Database Backup (Every Sunday at 03:00 TR Time)
0 0 * * 0 /opt/auto-viral-media-engine/venv/bin/python3 /opt/auto-viral-media-engine/shorts_automation/server_backup_mailer.py >> /opt/auto-viral-media-engine/shorts_automation/logs/backup.log 2>&1
```

---

## 6. Monitoring & Maintenance

* **Live Log Streaming:**
  * YouTube Shorts: `tail -f /opt/auto-viral-media-engine/shorts_automation/logs/shorts.log`
  * Instagram Reels: `tail -f /opt/auto-viral-media-engine/instagram_reels/logs/reels.log`
* **Disk Cleaning:** All temporary clips, rendered drafts, and voiceover audio files are automatically purged (`os.remove`) after every post attempt.
