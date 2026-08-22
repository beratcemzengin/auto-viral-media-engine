import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Ensure required directories exist
for folder in [DATA_DIR, OUTPUT_DIR, LOGS_DIR, ASSETS_DIR]:
    os.makedirs(folder, exist_ok=True)

# Bright kid-friendly background colors
KIDS_COLORS = [
    "#FFF5E4",  # Warm cream
    "#F5F0BB",  # Soft yellow
    "#DFFFD8",  # Mint green
    "#B4E4FF",  # Sky blue
    "#E5D1FA",  # Lilac
    "#FFE5F1",  # Pastel pink
    "#E8F9FD",  # Ice blue
]

# UI / Font Settings
FONT_PATH = os.getenv("FONT_PATH_LINUX", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
if not os.path.exists(FONT_PATH):
    FONT_PATH = "arial.ttf"

# Email Settings
ALERT_EMAIL_RECIPIENT = os.getenv("ALERT_EMAIL_RECIPIENT", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.yandex.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() in ("true", "1", "yes")

# Database Path
DB_PATH = os.path.join(DATA_DIR, "kids_posted.db")

# YouTube API Credentials
CLIENT_SECRETS_FILE = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", os.path.join(BASE_DIR, "client_secrets.json"))
CREDENTIALS_FILE = os.getenv("YOUTUBE_CREDENTIALS_FILE", os.path.join(BASE_DIR, "credentials.json"))
