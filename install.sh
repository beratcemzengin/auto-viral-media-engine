#!/usr/bin/env bash
# ==============================================================================
# 🚀 AUTO VIRAL MEDIA ENGINE - INTERACTIVE 1-CLICK INSTALLER WIZARD
# For Ubuntu 22.04 / 24.04 LTS & Debian Systems
# Developed by Berat Cem Zengin (https://github.com/beratcemzengin)
# ==============================================================================

set -e

# Renk Tanımlamaları
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
echo "    🚀 AUTO VIRAL MEDIA ENGINE - TEK KOMUTLA ETKİLEŞİMLİ KURULUM SİHİRBAZI   "
echo "        YouTube Shorts (Mikro-Belgesel) & Instagram Reels (Fragman)           "
echo "=============================================================================="
echo -e "${NC}"

# 1. ROOT / SUDO KONTROLÜ
if [ "$EUID" -ne 0 ]; then
    SUDO="sudo"
else
    SUDO=""
fi

echo -e "${BLUE}[1/7] 📦 Sistem Paketleri ve FFmpeg Güncelleniyor...${NC}"
$SUDO apt-get update -qq
$SUDO apt-get install -y python3 python3-pip python3-venv ffmpeg git curl fonts-dejavu fonts-freefont-ttf jq -qq

echo -e "${GREEN}✓ Sistem bağımlılıkları ve FFmpeg başarıyla kuruldu.${NC}\n"

# 2. HEDEF DİZİN SEÇİMİ
DEFAULT_INSTALL_DIR="/opt/auto-viral-media-engine"
echo -e "${BLUE}[2/7] 📁 Kurulum Dizini Belirleme:${NC}"
read -p "$(echo -e ${YELLOW}"Kurulum nereye yapılsın? [Varsayılan: ${DEFAULT_INSTALL_DIR}]: "${NC})" USER_DIR
INSTALL_DIR="${USER_DIR:-$DEFAULT_INSTALL_DIR}"

if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}Hedef dizin zaten mevcut. Güncellemeler alınıyor...${NC}"
    cd "$INSTALL_DIR"
    git pull origin main || true
else
    echo -e "${BLUE}Depo GitHub'dan klonlanıyor...${NC}"
    $SUDO git clone https://github.com/beratcemzengin/auto-viral-media-engine.git "$INSTALL_DIR"
    $SUDO chown -R $USER:$USER "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

echo -e "${GREEN}✓ Proje dosyaları hazırlandı: ${INSTALL_DIR}${NC}\n"

# 3. PYTHON SANAL ORTAM (VENV) KURULUMU
echo -e "${BLUE}[3/7] 🐍 Python Sanal Ortamı (Venv) ve Kütüphaneler Kuruluyor...${NC}"
python3 -m venv venv
./venv/bin/pip install --upgrade pip -q
./venv/bin/pip install -r requirements.txt -q
echo -e "${GREEN}✓ Python kütüphaneleri başarıyla yüklendi.${NC}\n"

# 4. ETKİLEŞİMLİ YAPILANDIRMA (.ENV OLUŞTURMA SİHİRBAZI)
echo -e "${CYAN}${BOLD}"
echo "=============================================================================="
echo "    🔑 [4/7] API VE HESAP YAPILANDIRMA SİHİRBAZI                             "
echo "    (Bilgileri girmek istemezseniz ENTER ile varsayılanı bırakabilirsiniz)    "
echo "=============================================================================="
echo -e "${NC}"

# Pexels API
echo -e "${MAGENTA}1. Pexels API Anahtarı (YouTube Shorts HD Dikey B-Roll İçin - pexels.com/api):${NC}"
read -p "PEXELS_API_KEY: " PEXELS_KEY

# TMDB API
echo -e "\n${MAGENTA}2. TMDB API v3 Anahtarı (Film/Dizi Keşfi İçin - themoviedb.org/settings/api):${NC}"
read -p "TMDB_API_KEY: " TMDB_KEY

# Instagram Bilgileri
echo -e "\n${MAGENTA}3. Instagram Bilgileri (@evdekisinema veya Kendi Hesabınız):${NC}"
read -p "Instagram Kullanıcı Adı: " IG_USER
read -sp "Instagram Şifresi: " IG_PASS
echo ""

# E-Posta Bildirimleri (SMTP)
echo -e "\n${MAGENTA}4. E-Posta Bildirimleri (Paylaşım Başarılı / Başarısız Bildirimleri):${NC}"
read -p "Bildirim Alacak E-Posta Adresi (Örn: adiniz@gmail.com): " ALERT_MAIL
read -p "SMTP Sunucusu [Varsayılan: smtp.yandex.com]: " SMTP_SRV
SMTP_SRV="${SMTP_SRV:-smtp.yandex.com}"
read -p "SMTP Portu [Varsayılan: 587]: " SMTP_PRT
SMTP_PRT="${SMTP_PRT:-587}"
read -p "SMTP Gönderici E-Posta (Örn: alert@domain.com): " SMTP_USR
read -sp "SMTP Şifresi (Uygulama Şifresi): " SMTP_PWD
echo ""

# .env Dosyasını Oluştur
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
echo -e "\n${GREEN}✓ .env yapılandırma dosyası güvenli bir şekilde kaydedildi.${NC}\n"

# 5. VERİTABANI İLKLENDİRME
echo -e "${BLUE}[5/7] 🗄️ SQLite Veritabanları ve Mükerrerlik Kalkanı İlklendiriliyor...${NC}"
./venv/bin/python3 -c "
import os, sys
sys.path.insert(0, '$INSTALL_DIR')
from shorts_automation import database as s_db, script_generator
from evdekisinema_reels import database as r_db
s_db.init_db()
script_generator._seed_stories()
r_db.init_db()
print('SQLite veritabanları ve 20+ viral senaryo havuzu hazır.')
"
echo -e "${GREEN}✓ Veritabanları ve 20+ doğrulanmış senaryo havuzu ilklendirildi.${NC}\n"

# 6. CRONTAB ZAMANLAYICI KURULUMU
echo -e "${BLUE}[6/7] ⏰ 7/24 Otonom Crontab Zamanlayıcısı Yapılandırılsın mı?${NC}"
echo -e "  - Instagram Reels: 09:00 ve 17:00 (TSİ)"
echo -e "  - YouTube Shorts: 07:30, 11:00, 17:30, 20:00 (TSİ)"
echo -e "  - Haftalık Sistem ZIP Yedeği: Her Pazar 03:00 (TSİ)"
read -p "$(echo -e ${YELLOW}"Crontab görevleri otomatik eklensin mi? (E/h): "${NC})" CRON_CHOICE

CRON_CHOICE="${CRON_CHOICE:-E}"
if [[ "$CRON_CHOICE" =~ ^[EeYy]$ ]]; then
    # Mevcut crontab'ı al
    TMP_CRON=$(mktemp)
    crontab -l > "$TMP_CRON" 2>/dev/null || true

    # Önceki kayıtları temizle
    sed -i '/auto-viral-media-engine/d' "$TMP_CRON"

    # Yeni görevleri ekle
    cat <<EOF >> "$TMP_CRON"
# Auto Viral Media Engine - Instagram Reels (09:00 & 17:00 TSİ)
0 6 * * * $INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/evdekisinema_reels/main.py >> $INSTALL_DIR/evdekisinema_reels/logs/reels.log 2>&1
0 14 * * * $INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/evdekisinema_reels/main.py >> $INSTALL_DIR/evdekisinema_reels/logs/reels.log 2>&1

# Auto Viral Media Engine - YouTube Shorts (07:30, 11:00, 17:30, 20:00 TSİ)
30 4 * * * $INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/shorts_automation/main.py >> $INSTALL_DIR/shorts_automation/logs/shorts.log 2>&1
0 8 * * * $INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/shorts_automation/main.py >> $INSTALL_DIR/shorts_automation/logs/shorts.log 2>&1
30 14 * * * $INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/shorts_automation/main.py >> $INSTALL_DIR/shorts_automation/logs/shorts.log 2>&1
0 17 * * * $INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/shorts_automation/main.py >> $INSTALL_DIR/shorts_automation/logs/shorts.log 2>&1

# Auto Viral Media Engine - Haftalık Yedek (Pazar 03:00 TSİ)
0 0 * * 0 $INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/shorts_automation/server_backup_mailer.py >> $INSTALL_DIR/shorts_automation/logs/backup.log 2>&1
EOF

    crontab "$TMP_CRON"
    rm -f "$TMP_CRON"
    echo -e "${GREEN}✓ Crontab zamanlayıcıları 7/24 tam otonom çalışma için kuruldu!${NC}\n"
else
    echo -e "${YELLOW}Crontab adımı atlandı. Dilediğiniz zaman manuel kurabilirsiniz.${NC}\n"
fi

# 7. TEBRİKLER & BİLGİLENDİRME
echo -e "${CYAN}${BOLD}"
echo "=============================================================================="
echo "    🎉 TEBRİKLER! OTONOM MEDYA FABRİKASI BAŞARIYLA KURULDU! 🚀               "
echo "=============================================================================="
echo -e "${NC}"
echo -e "📁 Kurulum Yolu: ${BOLD}${INSTALL_DIR}${NC}"
echo -e "📝 Çevre Değişkenleri: ${BOLD}${INSTALL_DIR}/.env${NC}"
echo -e "\n${YELLOW}▶ Manuel Test Çalıştırma Komutları:${NC}"
echo -e "  - YouTube Shorts Test: ${BOLD}${INSTALL_DIR}/venv/bin/python3 -m shorts_automation.main${NC}"
echo -e "  - Instagram Reels Test: ${BOLD}${INSTALL_DIR}/venv/bin/python3 -m evdekisinema_reels.main${NC}"
echo -e "\n${YELLOW}📊 Canlı Logları Takip Etmek İçin:${NC}"
echo -e "  - YouTube Log: ${BOLD}tail -f ${INSTALL_DIR}/shorts_automation/logs/shorts.log${NC}"
echo -e "  - Instagram Log: ${BOLD}tail -f ${INSTALL_DIR}/evdekisinema_reels/logs/reels.log${NC}"
echo -e "\n${GREEN}Sistem artık arka planda tamamen bağımsız çalışmaya hazırdır! Bol izlenmeler! 🍿🚀${NC}\n"
