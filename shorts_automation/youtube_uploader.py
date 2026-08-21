import os
import logging
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from . import config

logger = logging.getLogger("shorts.youtube")

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    creds = None
    if os.path.exists(config.CREDENTIALS_FILE):
        try:
            creds = Credentials.from_authorized_user_file(config.CREDENTIALS_FILE, SCOPES)
        except Exception as e:
            logger.warning(f"Kayıtlı kimlik dosyası geçersiz: {e}")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.warning(f"Token yenileme başarısız: {e}")
                creds = None
        
        if not creds:
            if not os.path.exists(config.CLIENT_SECRETS_FILE):
                raise FileNotFoundError(f"YouTube client_secrets.json dosyası bulunamadı: {config.CLIENT_SECRETS_FILE}")
            flow = InstalledAppFlow.from_client_secrets_file(config.CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(config.CREDENTIALS_FILE, "w") as token:
            token.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)

def upload_video(file_path, title, description, tags=None, category_id="22", privacy_status="public"):
    if not os.path.exists(file_path):
        logger.error(f"Yüklenecek video bulunamadı: {file_path}")
        return None

    try:
        youtube = get_authenticated_service()
        body = {
            "snippet": {
                "title": title[:100],
                "description": description,
                "tags": tags or ["shorts"],
                "categoryId": category_id
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False
            }
        }

        media = MediaFileUpload(file_path, mimetype="video/mp4", resumable=True, chunksize=1024*1024*5)
        logger.info(f"YouTube yüklemesi başlıyor: {title}")
        
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                logger.info(f"Yükleme ilerlemesi: %{int(status.progress() * 100)}")

        video_id = response.get("id")
        if video_id:
            logger.info(f"Yükleme başarılı! Video ID: {video_id}")
            return f"https://www.youtube.com/shorts/{video_id}"
    except Exception as e:
        logger.error(f"YouTube yükleme hatası: {e}")

    return None
