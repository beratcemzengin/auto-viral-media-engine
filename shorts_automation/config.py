import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root or current folder
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Pexels API
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

# Voice / TTS Settings
TTS_VOICE = os.getenv("TTS_VOICE", "tr-TR-AhmetNeural")
TTS_RATE = os.getenv("TTS_RATE", "+5%")

# YouTube API Credentials
CLIENT_SECRETS_FILE = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", os.path.join(BASE_DIR, "client_secrets.json"))
CREDENTIALS_FILE = os.getenv("YOUTUBE_CREDENTIALS_FILE", os.path.join(BASE_DIR, "credentials.json"))

# Email Notification Settings
ALERT_EMAIL_RECIPIENT = os.getenv("ALERT_EMAIL_RECIPIENT", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.yandex.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() in ("true", "1", "yes")

# Ensure required directories exist
for folder in [DATA_DIR, OUTPUT_DIR, LOGS_DIR]:
    os.makedirs(folder, exist_ok=True)
