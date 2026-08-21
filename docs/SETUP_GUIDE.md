# 📖 A-Z Setup & Deployment Guide

This guide provides exhaustive step-by-step instructions for obtaining all required credentials and deploying the **Auto Viral Media Engine** from scratch on Linux (Ubuntu / Debian) and Windows.

---

## 📑 Table of Contents
1. [Obtaining Required API Credentials](#1-obtaining-required-api-credentials)
2. [Server & Hardware Requirements](#2-server--hardware-requirements)
3. [Ubuntu / Debian Server Setup](#3-ubuntu--debian-server-setup)
4. [Windows 10/11 Setup](#4-windows-1011-setup)
5. [24/7 Automation & Crontab](#5-247-automation--crontab)
6. [Monitoring & Maintenance](#6-monitoring--maintenance)

---

## 1. Obtaining Required API Credentials

### A. Pexels API Key (Free HD Vertical B-Roll)
1. Go to [Pexels API Portal](https://www.pexels.com/api/) and click **"Get Started"** to create a free account.
2. Once logged in, click **"Your API Key"** in the top navigation menu.
3. Fill in the short API request form (e.g., App Name: *Social Video Generator*, Description: *Autonomous micro-documentary B-roll curation*).
4. Copy your **API Key** (e.g., `563492ad6f91700001000001...`).
5. Add it to `.env`:
   ```ini
   PEXELS_API_KEY=your_pexels_api_key_here
   ```

---

### B. TMDB API Key (Free Movie & TV Discovery)
1. Create a free account at [themoviedb.org/signup](https://www.themoviedb.org/signup).
2. Confirm your registration via email.
3. Navigate to **Account Settings > API** ([themoviedb.org/settings/api](https://www.themoviedb.org/settings/api)).
4. Under **"Request an API Key"**, click **"Create"** and select **"Developer"**.
5. Accept the API terms and fill in the application form:
   * **Type of Use:** Personal / Media Automation
   * **Application Name:** `Auto Viral Media Engine`
   * **Application URL:** `https://github.com/beratcemzengin/auto-viral-media-engine`
   * **Summary:** `Automated movie/series trailer curation and Instagram Reels publisher.`
6. Copy the generated **API Key (v3 auth)** string.
7. Add it to `.env`:
   ```ini
   TMDB_API_KEY=your_tmdb_v3_api_key_here
   ```

---

### C. Google Cloud YouTube Data API v3 (YouTube Uploads)
1. Navigate to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click the project dropdown at the top and select **"NEW PROJECT"** (e.g., `Shorts-Automation-Production`).
3. In the left navigation menu, go to **APIs & Services > Library**.
4. Search for **"YouTube Data API v3"**, click on it, and click **ENABLE**.
5. Go to **APIs & Services > OAuth consent screen**:
   * Choose **External** and click **CREATE**.
   * Enter **App Name** (`Shorts Uploader`) and **User support email**.
   * Under **Developer contact information**, enter your email and click **SAVE AND CONTINUE**.
   * Under **Test users**, click **+ ADD USERS**, type the Gmail address of your YouTube channel, and click **SAVE AND CONTINUE**.
6. Go to **APIs & Services > Credentials**:
   * Click **+ CREATE CREDENTIALS > OAuth client ID**.
   * Select **Application type: Desktop app**.
   * Name: `Shorts-Desktop-Client`.
   * Click **CREATE**.
7. In the credentials list, click the **Download JSON** icon next to your client ID.
8. Rename the downloaded file to **`client_secrets.json`** and place it in the `shorts_automation/` directory.
9. **First Run Authentication:** Run `python -m shorts_automation.main` locally. An authorization URL will appear in your console. Open it in a browser, sign in with your YouTube channel Google account, and grant access. The token will be saved permanently as **`credentials.json`** for headless server execution.

---

### D. Instagram Credentials & Session Caching
1. In your `.env` file, supply your Instagram username and password:
   ```ini
   INSTAGRAM_USERNAME=your_instagram_username
   INSTAGRAM_PASSWORD=your_instagram_password
   ```
2. The engine uses `instagrapi` to emulate a physical Google Pixel 8 Pro device. Upon first login, it saves your authenticated session state to `instagram_reels/session.json`.
3. Subsequent requests load this cookie file directly, avoiding repeated password verifications and checkpoint challenges.

---

### E. SMTP Email Configuration (Instant Alerts & Weekly Backup Delivery)

#### Option 1: Yandex Mail
1. Log in to [Yandex ID Security](https://id.yandex.com/security/app-passwords).
2. Click **App passwords > Add app password > Mail**.
3. Copy the generated 16-letter app password and add to `.env`:
   ```ini
   ALERT_EMAIL_RECIPIENT=your_notification_email@gmail.com
   SMTP_SERVER=smtp.yandex.com
   SMTP_PORT=587
   SMTP_USER=alert@yourdomain.com
   SMTP_PASSWORD=your_yandex_app_password
   SMTP_USE_TLS=true
   ```

#### Option 2: Gmail (Google Workspace or @gmail.com)
1. Turn on **2-Step Verification** on your Google Account.
2. Go to [Google App Passwords](https://myaccount.google.com/apppasswords).
3. Create a new app password named **"Auto Media Mailer"**.
4. Copy the 16-character code and add to `.env`:
   ```ini
   ALERT_EMAIL_RECIPIENT=your_notification_email@gmail.com
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your_email@gmail.com
   SMTP_PASSWORD=your_16_char_gmail_app_password
   SMTP_USE_TLS=true
   ```

---

## 2. Server & Hardware Requirements

* **Cloud VPS (Recommended):**
  * **Hetzner Cloud:** CX22 (2 vCPU, 4GB RAM, 40GB SSD) ~ 4€/mo.
  * **DigitalOcean:** Basic Droplet (2 vCPU, 2GB RAM, 50GB SSD) ~ $12/mo.
  * **Contabo:** Cloud VPS S (4 vCPU, 6GB RAM, 100GB SSD) ~ 5.5€/mo.
* **Home Server / Bare Metal:**
  * Mini PC (Intel N100 / Core i3 / i5)
  * Raspberry Pi 4 or 5 (8GB RAM Model)
  * CasaOS / Debian Home Server.

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
