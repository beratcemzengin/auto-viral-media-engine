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
OUTPUT_DIR = os.path.join(DATA_DIR, "output")
TRAILER_DIR = os.path.join(DATA_DIR, "trailers")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# TMDB API
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
TMDB_BASE_URL = "https://api.themoviedb.org/3"

# Instagram Credentials
IG_USERNAME = os.getenv("INSTAGRAM_USERNAME", "")
IG_PASSWORD = os.getenv("INSTAGRAM_PASSWORD", "")
IG_SESSION_FILE = os.path.join(BASE_DIR, "session.json")

# Email Notification Settings
ALERT_EMAIL_RECIPIENT = os.getenv("ALERT_EMAIL_RECIPIENT", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.yandex.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() in ("true", "1", "yes")

# Font configuration
FONT_PATH = os.getenv("FONT_PATH_LINUX", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")

# Video Settings
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30
MAX_REEL_DURATION = 90.0

for folder in [DATA_DIR, OUTPUT_DIR, TRAILER_DIR, LOGS_DIR]:
    os.makedirs(folder, exist_ok=True)
