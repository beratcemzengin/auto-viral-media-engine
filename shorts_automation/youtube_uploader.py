import os
import time
import logging
import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request

try:
    from . import config
except ImportError:
    import config

logger = logging.getLogger("shorts.youtube")

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def get_authenticated_service():
    """Authenticates with YouTube API via OAuth2. Headless server compliant."""
    credentials = None

    if os.path.exists(config.CREDENTIALS_FILE):
        try:
            credentials = google.oauth2.credentials.Credentials.from_authorized_user_file(
                config.CREDENTIALS_FILE, SCOPES)
        except Exception as e:
            logger.warning(f"Failed to read credentials file: {e}")
            credentials = None

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            try:
                logger.info("Token expired, refreshing with refresh token...")
                credentials.refresh(Request())
                with open(config.CREDENTIALS_FILE, 'w') as f:
                    f.write(credentials.to_json())
                logger.info("Token refreshed successfully.")
            except Exception as e:
                logger.error(
                    f"Token refresh failed (revoked or expired): {e}\n"
                    f"SOLUTION: Run 'python reauth_oob.py' on a machine with a browser to regenerate it.")
                return None
        else:
            logger.error(
                "No valid credentials.json found or refresh_token is missing.\n"
                "SOLUTION: Run 'python reauth_oob.py' to generate a fresh token.")
            return None

    return build("youtube", "v3", credentials=credentials)


def upload_video(video_path, title, description, tags=None, max_retries=3, made_for_kids=False):
    """Uploads video to YouTube as a Short. Includes exponential backoff retries."""
    if not os.path.exists(video_path):
        logger.error(f"Video file not found: {video_path}")
        return None

    youtube = get_authenticated_service()
    if not youtube:
        logger.error("YouTube authentication failed. Re-authorization required.")
        return None

    if not tags:
        tags = ["shorts", "infotainment", "facts", "education", "viral"]

    if "#shorts" not in title.lower() and "#shorts" not in description.lower():
        title = f"{title} #shorts"

    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags,
            "categoryId": "27"  # Education category
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": made_for_kids,
        }
    }

    logger.info(f"Starting YouTube upload: {title}")

    for attempt in range(1, max_retries + 1):
        try:
            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
            request = youtube.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=media
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logger.info(f"Upload progress: {int(status.progress() * 100)}%")

            video_id = response.get("id")
            logger.info(f"Upload successful! Video ID: {video_id}")
            return f"https://www.youtube.com/shorts/{video_id}"

        except HttpError as e:
            error_code = e.resp.status
            logger.warning(f"YouTube HTTP Error (Attempt {attempt}/{max_retries}): {error_code} - {e}")

            if error_code == 400:
                logger.error("Invalid content policy or format (400). Skipping retries.")
                return None

            if error_code in (401, 403):
                logger.error(f"Authorization error ({error_code}). Re-authorization required.")
                return None

            if error_code in (500, 502, 503, 504):
                if attempt < max_retries:
                    wait_secs = (2 ** attempt) * 30  # 60s, 120s, 240s
                    logger.info(f"YouTube server error ({error_code}). Retrying in {wait_secs}s...")
                    time.sleep(wait_secs)
                    continue
                else:
                    logger.error(f"YouTube server error persisted after {max_retries} attempts.")
                    return None

            if attempt < max_retries:
                wait_secs = (2 ** attempt) * 15
                logger.info(f"Unexpected HTTP {error_code}. Retrying in {wait_secs}s...")
                time.sleep(wait_secs)
            else:
                logger.error(f"All attempts failed. Final error: {e}")
                return None

        except Exception as e:
            logger.warning(f"Unexpected upload exception (Attempt {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                wait_secs = (2 ** attempt) * 20
                logger.info(f"Retrying in {wait_secs}s...")
                time.sleep(wait_secs)
            else:
                logger.error(f"All attempts failed. Final error: {e}")
                return None

    return None
