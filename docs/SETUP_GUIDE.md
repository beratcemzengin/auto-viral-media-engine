# 📖 A-Z Setup & Deployment Guide

This guide covers every step from zero to a fully running 24/7 autonomous publishing server.

---

## 📑 Table of Contents
1. [Obtaining Required API Credentials](#1-obtaining-required-api-credentials)
2. [Server & Hardware Requirements](#2-server--hardware-requirements)
3. [Ubuntu / Debian Server Setup (Step by Step)](#3-ubuntu--debian-server-setup)
4. [Windows 10/11 Local Setup](#4-windows-1011-local-setup)
5. [YouTube OAuth First-Time Authorization](#5-youtube-oauth-first-time-authorization)
6. [Publishing Google OAuth App to Production](#6-publishing-google-oauth-app-to-production)
7. [24/7 Automation & Crontab](#7-247-automation--crontab)
8. [Re-authorization If Token Expires](#8-re-authorization-if-token-expires)
9. [Monitoring & Maintenance](#9-monitoring--maintenance)

---

## 1. Obtaining Required API Credentials

### A. Pexels API Key (Free)
1. Visit [pexels.com/api](https://www.pexels.com/api/) → **"Get Started"** → create a free account.
2. After login, click **"Your API Key"** in the top navigation.
3. Fill in:
   - **App Name:** `Auto Viral Media Engine`
   - **Description:** `Automated micro-documentary B-roll curation and video generation`
4. Copy the API Key (56-character string).
5. Add to `.env`:
   ```ini
   PEXELS_API_KEY=your_pexels_api_key_here
   ```

---

### B. TMDB API Key (Free)
1. Sign up at [themoviedb.org/signup](https://www.themoviedb.org/signup) and verify your email.
2. Go to **Account Settings > API** ([themoviedb.org/settings/api](https://www.themoviedb.org/settings/api)).
3. Click **"Create" → "Developer"** and accept the terms.
4. Fill in:
   - **Application Name:** `Auto Viral Media Engine`
   - **Application URL:** `https://github.com/beratcemzengin/auto-viral-media-engine`
   - **Summary:** `Automated movie/series trailer curation for Instagram Reels.`
5. Copy the **API Key (v3 auth)**.
6. Add to `.env`:
   ```ini
   TMDB_API_KEY=your_tmdb_v3_api_key_here
   ```

---

### C. Google Cloud — YouTube Data API v3

#### C-1. Create Project & Enable API
1. Go to [console.cloud.google.com](https://console.cloud.google.com/).
2. Click the project dropdown → **"NEW PROJECT"** → name it `YouTube-Shorts-Automation` → **"CREATE"**.
3. In the left menu → **APIs & Services > Library** → search **"YouTube Data API v3"** → **"ENABLE"**.

#### C-2. Configure OAuth Consent Screen (Branding)
1. Go to **Google Auth Platform > Branding** (or **APIs & Services > OAuth consent screen**).
2. Select **User Type: External** → **"CREATE"**.
3. Fill in every required field:

   | Field | Value |
   |---|---|
   | **App name** | `Shorts Uploader` |
   | **User support email** | your Gmail address |
   | **Homepage URL** | `https://github.com/beratcemzengin/auto-viral-media-engine` |
   | **Privacy policy URL** | `https://github.com/beratcemzengin/auto-viral-media-engine/blob/main/PRIVACY.md` |
   | **Developer contact email** | your Gmail address |

4. Click **"SAVE AND CONTINUE"** through all steps.

#### C-3. Add Test User (Audience Tab)
1. Go to **Google Auth Platform > Audience**.
2. Under **"Test users"**, click **"+ Add users"**.
3. Enter the Gmail address of your YouTube channel.
4. Click **"SAVE"**.

#### C-4. ⚠️ Publish App to Production (CRITICAL)
> **Do NOT skip this step.** Without it, your refresh token expires every 7 days causing `invalid_grant` errors that break all uploads.

1. In **Google Auth Platform > Audience**, find **"Publishing status"**.
2. Click **"Publish app"** → confirm the dialog.
3. Status must show **"In production"** ✅

#### C-5. Create OAuth Credentials
1. Go to **APIs & Services > Credentials**.
2. Click **"+ CREATE CREDENTIALS > OAuth client ID"**.
3. Select **Application type: Desktop app**, name it `Shorts-Desktop-Client` → **"CREATE"**.
4. Click **"Download JSON"** on the created entry.
5. Rename the downloaded file to **`client_secrets.json`**.
6. Copy it to the `shorts_automation/` directory.

---

### D. Instagram Credentials
1. Add to `.env`:
   ```ini
   INSTAGRAM_USERNAME=your_instagram_username
   INSTAGRAM_PASSWORD=your_instagram_password
   ```
2. On first run the engine saves an authenticated device session to `instagram_reels/session.json` and reuses it for all future posts — no repeated logins or 2FA.

---

### E. SMTP Email (Instant Alerts & Weekly Backup)

**Option 1 — Yandex Mail (Recommended):**
1. Go to [Yandex ID > App Passwords](https://id.yandex.com/security/app-passwords) → **"Add app password" > "Mail"**.
2. Copy the 16-character password.
3. Add to `.env`:
   ```ini
   ALERT_EMAIL_RECIPIENT=notification@gmail.com
   SMTP_SERVER=smtp.yandex.com
   SMTP_PORT=587
   SMTP_USER=your_address@yandex.com
   SMTP_PASSWORD=your_16_char_app_password
   SMTP_USE_TLS=true
   ```

**Option 2 — Gmail:**
1. Enable **2-Step Verification** on your Google Account.
2. Go to [Google App Passwords](https://myaccount.google.com/apppasswords) → create password named `Auto Media Mailer`.
3. Add to `.env`:
   ```ini
   ALERT_EMAIL_RECIPIENT=notification@gmail.com
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your_email@gmail.com
   SMTP_PASSWORD=your_16_char_app_password
   SMTP_USE_TLS=true
   ```

---

## 2. Server & Hardware Requirements

| Component | Minimum | Recommended | Note |
|---|---|---|---|
| **CPU** | 2 Cores | 4 Cores | FFmpeg encoding & blur |
| **RAM** | 2 GB | 4 GB | ~1.2 GB during render |
| **Storage** | 15 GB SSD | 40 GB NVMe | Temp files auto-deleted |
| **Network** | 10 Mbps | 50+ Mbps | Download & upload speed |
| **OS** | Ubuntu 22.04 / 24.04 LTS, Debian 11/12 | Ubuntu 24.04 LTS | Windows also supported |

**Recommended VPS Providers:**
- [Hetzner Cloud](https://hetzner.com/cloud) — CX22 (2 vCPU, 4GB RAM) ~4€/mo
- [DigitalOcean](https://digitalocean.com) — Basic Droplet ~$12/mo
- [Contabo](https://contabo.com) — VPS S ~5.5€/mo
- Home server: Raspberry Pi 5 (8GB), mini PC with Ubuntu, or CasaOS device

---

## 3. Ubuntu / Debian Server Setup

```bash
# Step 1: Install system packages
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv ffmpeg fonts-dejavu fonts-freefont-ttf git curl

# Step 2: Clone repository
cd /opt
sudo git clone https://github.com/beratcemzengin/auto-viral-media-engine.git
sudo chown -R $USER:$USER /opt/auto-viral-media-engine
cd /opt/auto-viral-media-engine

# Step 3: Create Python virtual environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Step 4: Configure environment variables
cp .env.example .env
nano .env
# Fill in all API keys, Instagram credentials, and SMTP settings

# Step 5: Create required directories
mkdir -p shorts_automation/logs instagram_reels/logs
mkdir -p shorts_automation/approved_scripts shorts_automation/posted_scripts
mkdir -p shorts_automation/data shorts_automation/output

# Step 6: Upload your credentials files (from local machine)
# Run this on your LOCAL machine:
# scp client_secrets.json user@server-ip:/opt/auto-viral-media-engine/shorts_automation/client_secrets.json
# scp credentials.json user@server-ip:/opt/auto-viral-media-engine/shorts_automation/credentials.json

# Step 7: Make retry script executable
chmod +x shorts_automation/run_shorts_with_retry.sh

# Step 8: Test run
export ALLOW_YOUTUBE_UPLOAD=1
python3 -m shorts_automation.main
```

---

## 4. Windows 10/11 Local Setup

1. Install [Python 3.11 or 3.12](https://www.python.org/downloads/) — check **"Add Python to PATH"**.
2. Install [FFmpeg](https://www.gyan.dev/ffmpeg/builds/) and add the `bin` folder to your system PATH.
3. Open PowerShell:
```powershell
git clone https://github.com/beratcemzengin/auto-viral-media-engine.git
cd auto-viral-media-engine
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```

---

## 5. YouTube OAuth First-Time Authorization

Run this step once on your **local machine** (not the server — you need a browser):

```bash
cd shorts_automation
python reauth_oob.py
```

The script will:
1. Print a Google authorization URL in your terminal.
2. You open the URL in your browser.
3. Sign in with the YouTube channel's Google account.
4. Click **"Allow"**.
5. Google shows a **code** on screen — copy it.
6. Paste it back into the terminal.
7. `credentials.json` is generated automatically.

Then copy it to your server:
```bash
scp shorts_automation/credentials.json user@your-server-ip:/opt/auto-viral-media-engine/shorts_automation/credentials.json
```

---

## 6. Publishing Google OAuth App to Production

> **Must be done once. Without this, tokens expire every 7 days.**

1. Go to [console.cloud.google.com](https://console.cloud.google.com/).
2. Select your YouTube automation project.
3. Navigate to **Google Auth Platform > Audience**.
4. Under **"Publishing status"**, click **"Publish app"**.
5. Confirm the dialog.
6. Status should show **"In production"** ✅

After publishing, your `credentials.json` refresh token never expires automatically.

---

## 7. 24/7 Automation & Crontab

Run `crontab -e` on your server and add:

```bash
# ==============================================================================
# AUTO VIRAL MEDIA ENGINE — SCHEDULE (UTC+3 / Turkey Time)
# All times below are UTC. Turkey is UTC+3.
# ==============================================================================

# 🍿 Instagram Reels — 09:00 & 17:00 TR (06:00 & 14:00 UTC)
0 6 * * * /opt/auto-viral-media-engine/venv/bin/python3 /opt/auto-viral-media-engine/instagram_reels/main.py >> /opt/auto-viral-media-engine/instagram_reels/logs/reels.log 2>&1
0 14 * * * /opt/auto-viral-media-engine/venv/bin/python3 /opt/auto-viral-media-engine/instagram_reels/main.py >> /opt/auto-viral-media-engine/instagram_reels/logs/reels.log 2>&1

# 🧠 YouTube Shorts — 07:30, 11:00, 17:30, 20:00 TR (with 3-attempt retry)
30 4 * * * /opt/auto-viral-media-engine/shorts_automation/run_shorts_with_retry.sh
0 8 * * * /opt/auto-viral-media-engine/shorts_automation/run_shorts_with_retry.sh
30 14 * * * /opt/auto-viral-media-engine/shorts_automation/run_shorts_with_retry.sh
0 17 * * * /opt/auto-viral-media-engine/shorts_automation/run_shorts_with_retry.sh

# 💾 Weekly Backup — Every Sunday 03:00 TR (00:00 UTC)
0 0 * * 0 /opt/auto-viral-media-engine/venv/bin/python3 /opt/auto-viral-media-engine/shorts_automation/server_backup_mailer.py >> /opt/auto-viral-media-engine/shorts_automation/logs/backup.log 2>&1
```

**How `run_shorts_with_retry.sh` works:**
- Attempt 1 → runs immediately
- Attempt 2 → if failed, waits 10 minutes and retries
- Attempt 3 → if still failed, waits 20 more minutes and retries
- If all 3 fail → failure email is sent

---

## 8. Re-authorization If Token Expires

If you ever receive an email with `invalid_grant` error:

**Option A — OOB flow (recommended, works without setting up anything):**
```bash
# Run on your LOCAL machine
cd shorts_automation
python reauth_oob.py
# Follow the URL → paste the code back → scp the new credentials.json to server
```

**Option B — Console flow on server directly:**
```bash
# Run directly on server (SSH in first)
cd /opt/auto-viral-media-engine/shorts_automation
source ../venv/bin/activate
python reauth_oob.py
# Follow the URL (can open on your phone/another device) → paste code
```

After re-authorization, the pipeline resumes automatically at the next scheduled cron time.

> **Prevention:** Ensure your Google Cloud app is in **"In production"** mode (Section 6). This prevents token expiry entirely.

---

## 9. Monitoring & Maintenance

**Live log streaming:**
```bash
# YouTube Shorts
tail -f /opt/auto-viral-media-engine/shorts_automation/logs/shorts_$(date +%Y%m%d)*.log

# Instagram Reels
tail -f /opt/auto-viral-media-engine/instagram_reels/logs/reels.log
```

**Check what has been posted:**
```bash
cd /opt/auto-viral-media-engine
# YouTube Shorts history
sqlite3 shorts_automation/data/posted_shorts.db "SELECT title, posted_at, youtube_url FROM posted_shorts ORDER BY posted_at DESC LIMIT 10;"

# Instagram Reels history
sqlite3 instagram_reels/data/posted.db "SELECT title, posted_at FROM posts ORDER BY posted_at DESC LIMIT 10;"
```

**Manual test run:**
```bash
cd /opt/auto-viral-media-engine
export ALLOW_YOUTUBE_UPLOAD=1
venv/bin/python3 -m shorts_automation.main
```

**Check server disk usage:**
```bash
du -sh /opt/auto-viral-media-engine/shorts_automation/output/
du -sh /opt/auto-viral-media-engine/instagram_reels/
```

**Disk note:** All temporary video clips, rendered MP4 files, and TTS audio are automatically deleted after each successful or failed post attempt. No manual cleanup is needed.
