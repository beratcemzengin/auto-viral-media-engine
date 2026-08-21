#!/usr/bin/env bash
# ==============================================================================
# 🚀 AUTO VIRAL MEDIA ENGINE - INTERACTIVE 1-CLICK INSTALLER WIZARD
# For Ubuntu 22.04 / 24.04 LTS & Debian Systems
# Developed by Berat Cem Zengin (https://github.com/beratcemzengin)
# ==============================================================================

set -e

# Color Palette
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m' # No Color

clear

echo -e "${CYAN}${BOLD}"
echo "=============================================================================="
echo "    🚀 AUTO VIRAL MEDIA ENGINE - INTERACTIVE 1-CLICK SETUP WIZARD            "
echo "        YouTube Shorts (Micro-Docs) & Instagram Reels (Trailers)              "
echo "=============================================================================="
echo -e "${NC}"

# 1. ROOT / SUDO CHECK
if [ "$EUID" -ne 0 ]; then
    SUDO="sudo"
else
    SUDO=""
fi

echo -e "${BLUE}[1/7] 📦 Updating System Packages & Installing FFmpeg...${NC}"
$SUDO apt-get update -qq
$SUDO apt-get install -y python3 python3-pip python3-venv ffmpeg git curl fonts-dejavu fonts-freefont-ttf jq -qq

echo -e "${GREEN}✓ System dependencies and FFmpeg installed successfully.${NC}\n"

# 2. INSTALLATION DIRECTORY
DEFAULT_INSTALL_DIR="/opt/auto-viral-media-engine"
echo -e "${BLUE}[2/7] 📁 Target Installation Directory:${NC}"
read -p "$(echo -e ${YELLOW}"Where should the project be installed? [Default: ${DEFAULT_INSTALL_DIR}]: "${NC})" USER_DIR
INSTALL_DIR="${USER_DIR:-$DEFAULT_INSTALL_DIR}"

if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}Target directory already exists. Fetching latest updates...${NC}"
    cd "$INSTALL_DIR"
    git pull origin main || true
else
    echo -e "${BLUE}Cloning repository from GitHub...${NC}"
    $SUDO git clone https://github.com/beratcemzengin/auto-viral-media-engine.git "$INSTALL_DIR"
    $SUDO chown -R $USER:$USER "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

echo -e "${GREEN}✓ Project directory ready: ${INSTALL_DIR}${NC}\n"

# 3. PYTHON VIRTUAL ENVIRONMENT
echo -e "${BLUE}[3/7] 🐍 Setting up Python Virtual Environment (venv) & Dependencies...${NC}"
python3 -m venv venv
./venv/bin/pip install --upgrade pip -q
./venv/bin/pip install -r requirements.txt -q
echo -e "${GREEN}✓ Python packages installed successfully.${NC}\n"

# 4. INTERACTIVE CONFIGURATION WIZARD
echo -e "${CYAN}${BOLD}"
echo "=============================================================================="
echo "    🔑 [4/7] API & CREDENTIALS CONFIGURATION WIZARD                          "
echo "    (Press ENTER to leave blank or use defaults)                             "
echo "=============================================================================="
echo -e "${NC}"

# Pexels API
echo -e "${MAGENTA}1. Pexels API Key (Used for YouTube Shorts HD Vertical B-Roll - pexels.com/api):${NC}"
read -p "PEXELS_API_KEY: " PEXELS_KEY

# TMDB API
echo -e "\n${MAGENTA}2. TMDB API v3 Key (Used for Movie/TV Discovery - themoviedb.org/settings/api):${NC}"
read -p "TMDB_API_KEY: " TMDB_KEY

# Instagram Credentials
echo -e "\n${MAGENTA}3. Instagram Credentials (Used for Reels Automation):${NC}"
read -p "Instagram Username: " IG_USER
read -sp "Instagram Password: " IG_PASS
echo ""

# Email Notifications
echo -e "\n${MAGENTA}4. Email Notifications (SMTP Alerts on Success / Failure):${NC}"
read -p "Notification Recipient Email (e.g. your_email@gmail.com): " ALERT_MAIL
read -p "SMTP Server [Default: smtp.yandex.com]: " SMTP_SRV
SMTP_SRV="${SMTP_SRV:-smtp.yandex.com}"
read -p "SMTP Port [Default: 587]: " SMTP_PRT
SMTP_PRT="${SMTP_PRT:-587}"
read -p "SMTP Username (e.g. alert@domain.com): " SMTP_USR
read -sp "SMTP Password (App Password): " SMTP_PWD
echo ""

# Generate .env File
cat <<EOF > "$INSTALL_DIR/.env"
# ==============================================================================
# AUTO VIRAL MEDIA ENGINE - ENVIRONMENT CONFIGURATION
# Generated automatically by install.sh wizard
# ==============================================================================

# 1. NOTIFICATION & EMAIL SETTINGS
ALERT_EMAIL_RECIPIENT=${ALERT_MAIL}
SMTP_SERVER=${SMTP_SRV}
SMTP_PORT=${SMTP_PRT}
SMTP_USER=${SMTP_USR}
SMTP_PASSWORD=${SMTP_PWD}
SMTP_USE_TLS=true

# 2. PEXELS API
PEXELS_API_KEY=${PEXELS_KEY}

# 3. TMDB API
TMDB_API_KEY=${TMDB_KEY}

# 4. INSTAGRAM CREDENTIALS
INSTAGRAM_USERNAME=${IG_USER}
INSTAGRAM_PASSWORD=${IG_PASS}

# 5. YOUTUBE OAUTH FILES
YOUTUBE_CLIENT_SECRETS_FILE=${INSTALL_DIR}/shorts_automation/client_secrets.json
YOUTUBE_CREDENTIALS_FILE=${INSTALL_DIR}/shorts_automation/credentials.json

# 6. SYSTEM PATHS
TTS_VOICE=tr-TR-AhmetNeural
FONT_PATH_LINUX=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
EOF

chmod 600 "$INSTALL_DIR/.env"
echo -e "\n${GREEN}✓ .env configuration file saved securely.${NC}\n"

# 5. INITIALIZE DATABASES
echo -e "${BLUE}[5/7] 🗄️ Initializing SQLite Databases & Anti-Duplicate Queues...${NC}"
./venv/bin/python3 -c "
import os, sys
sys.path.insert(0, '$INSTALL_DIR')
from shorts_automation import database as s_db, script_generator
from evdekisinema_reels import database as r_db
s_db.init_db()
script_generator._seed_stories()
r_db.init_db()
print('SQLite databases and 20+ viral script pool ready.')
"
echo -e "${GREEN}✓ SQLite databases and viral script queues initialized.${NC}\n"

# 6. CRONTAB CONFIGURATION
echo -e "${BLUE}[6/7] ⏰ Set up 24/7 Automated Crontab Schedule?${NC}"
echo -e "  - Instagram Reels: 09:00 & 17:00 (TR Time / 06:00 & 14:00 UTC)"
echo -e "  - YouTube Shorts: 07:30, 11:00, 17:30, 20:00 (TR Time)"
echo -e "  - Weekly System Backup: Every Sunday at 03:00 (TR Time)"
read -p "$(echo -e ${YELLOW}"Install automated crontab tasks? (Y/n): "${NC})" CRON_CHOICE

CRON_CHOICE="${CRON_CHOICE:-Y}"
if [[ "$CRON_CHOICE" =~ ^[YyEe]$ ]]; then
    TMP_CRON=$(mktemp)
    crontab -l > "$TMP_CRON" 2>/dev/null || true

    sed -i '/auto-viral-media-engine/d' "$TMP_CRON"

    cat <<EOF >> "$TMP_CRON"
# Auto Viral Media Engine - Instagram Reels (09:00 & 17:00 TR Time)
0 6 * * * $INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/evdekisinema_reels/main.py >> $INSTALL_DIR/evdekisinema_reels/logs/reels.log 2>&1
0 14 * * * $INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/evdekisinema_reels/main.py >> $INSTALL_DIR/evdekisinema_reels/logs/reels.log 2>&1

# Auto Viral Media Engine - YouTube Shorts (07:30, 11:00, 17:30, 20:00 TR Time)
30 4 * * * $INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/shorts_automation/main.py >> $INSTALL_DIR/shorts_automation/logs/shorts.log 2>&1
0 8 * * * $INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/shorts_automation/main.py >> $INSTALL_DIR/shorts_automation/logs/shorts.log 2>&1
30 14 * * * $INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/shorts_automation/main.py >> $INSTALL_DIR/shorts_automation/logs/shorts.log 2>&1
0 17 * * * $INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/shorts_automation/main.py >> $INSTALL_DIR/shorts_automation/logs/shorts.log 2>&1

# Auto Viral Media Engine - Weekly Backup (Sunday 03:00 TR Time)
0 0 * * 0 $INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/shorts_automation/server_backup_mailer.py >> $INSTALL_DIR/shorts_automation/logs/backup.log 2>&1
EOF

    crontab "$TMP_CRON"
    rm -f "$TMP_CRON"
    echo -e "${GREEN}✓ Crontab schedule installed for 24/7 autonomous publishing!${NC}\n"
else
    echo -e "${YELLOW}Crontab setup skipped. You can configure it manually later.${NC}\n"
fi

# 7. COMPLETION BANNER
echo -e "${CYAN}${BOLD}"
echo "=============================================================================="
echo "    🎉 CONGRATULATIONS! AUTO VIRAL MEDIA ENGINE INSTALLED SUCCESSFULLY! 🚀    "
echo "=============================================================================="
echo -e "${NC}"
echo -e "📁 Install Directory: ${BOLD}${INSTALL_DIR}${NC}"
echo -e "📝 Configuration: ${BOLD}${INSTALL_DIR}/.env${NC}"
echo -e "\n${YELLOW}▶ Manual Test Commands:${NC}"
echo -e "  - YouTube Shorts Test: ${BOLD}${INSTALL_DIR}/venv/bin/python3 -m shorts_automation.main${NC}"
echo -e "  - Instagram Reels Test: ${BOLD}${INSTALL_DIR}/venv/bin/python3 -m evdekisinema_reels.main${NC}"
echo -e "\n${YELLOW}📊 Live Log Monitoring:${NC}"
echo -e "  - YouTube Log: ${BOLD}tail -f ${INSTALL_DIR}/shorts_automation/logs/shorts.log${NC}"
echo -e "  - Instagram Log: ${BOLD}tail -f ${INSTALL_DIR}/evdekisinema_reels/logs/reels.log${NC}"
echo -e "\n${GREEN}The engine is now fully autonomous and running in the background! 🍿🚀${NC}\n"
