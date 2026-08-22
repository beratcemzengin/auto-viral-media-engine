import os
import smtplib
import zipfile
import logging
import sqlite3
import shutil
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from . import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("backup_mailer")

def safe_online_backup(src_db_path, dest_db_path):
    """Performs a transaction-safe backup of an active SQLite database."""
    if not os.path.exists(src_db_path):
        return False
    os.makedirs(os.path.dirname(dest_db_path), exist_ok=True)
    try:
        src_conn = sqlite3.connect(src_db_path)
        dest_conn = sqlite3.connect(dest_db_path)
        with dest_conn:
            src_conn.backup(dest_conn)
        dest_conn.close()
        src_conn.close()
        return True
    except Exception as e:
        logger.error(f"Safe database backup failed for {src_db_path}: {e}")
        return False

def create_backup_zip():
    backup_filename = f"server_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    backup_path = os.path.join(config.DATA_DIR, backup_filename)
    
    # Paths for safe temporary database backups
    temp_dir = os.path.join(config.DATA_DIR, "temp_backup_dbs")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Backup active databases safely
    shorts_db_src = os.path.join(config.DATA_DIR, "posted_shorts.db")
    shorts_db_dest = os.path.join(temp_dir, "posted_shorts.db")
    safe_online_backup(shorts_db_src, shorts_db_dest)

    instagram_db_src = os.path.join(config.BASE_DIR, "..", "instagram_reels", "data", "posted.db")
    instagram_db_dest = os.path.join(temp_dir, "posted.db")
    # Try backup if it exists, otherwise fall back to database folder inside project root
    if not safe_online_backup(instagram_db_src, instagram_db_dest):
        # Check standard relative path to instagram_reels/data/posted.db
        alt_src = os.path.join(config.BASE_DIR, "instagram_reels", "data", "posted.db")
        safe_online_backup(alt_src, instagram_db_dest)
    
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(config.BASE_DIR):
            # Skip temp db dir during initial walk
            if "temp_backup_dbs" in root:
                continue
            for file in files:
                if file.endswith(('.py', '.json', '.sh', '.md', '.txt')):
                    abs_path = os.path.join(root, file)
                    rel_path = os.path.relpath(abs_path, config.BASE_DIR)
                    zipf.write(abs_path, rel_path)
                elif file.endswith('.db') and not "posted" in file:
                    # Catch miscellaneous databases safely, but skip main ones which are backed up online
                    abs_path = os.path.join(root, file)
                    rel_path = os.path.relpath(abs_path, config.BASE_DIR)
                    zipf.write(abs_path, rel_path)
        
        # Write the safely copied database files instead of active ones
        if os.path.exists(shorts_db_dest):
            zipf.write(shorts_db_dest, os.path.join("shorts_automation", "data", "posted_shorts.db"))
        if os.path.exists(instagram_db_dest):
            zipf.write(instagram_db_dest, os.path.join("instagram_reels", "data", "posted.db"))
                    
    # Clean up temp database backups
    try:
        shutil.rmtree(temp_dir)
    except Exception:
        pass
        
    return backup_path

def send_backup_email():
    if not config.ALERT_EMAIL_RECIPIENT or not config.SMTP_USER or not config.SMTP_PASSWORD:
        logger.info("Email configurations missing, skipping backup email.")
        return
        
    zip_path = create_backup_zip()
    now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    msg = MIMEMultipart()
    msg["Subject"] = f"💾 [System Backup] Weekly Automation Backup ({now_str})"
    msg["From"] = config.SMTP_USER
    msg["To"] = config.ALERT_EMAIL_RECIPIENT
    
    body = f"Hello,\n\nThe system backup from {now_str} is attached to this email. It contains safe transaction backups of all active databases, automation scripts, and settings configurations."
    msg.attach(MIMEText(body, "plain", "utf-8"))
    
    with open(zip_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(zip_path)}")
    msg.attach(part)
    
    if config.SMTP_PORT == 465:
        server = smtplib.SMTP_SSL(config.SMTP_SERVER, config.SMTP_PORT, timeout=30)
    else:
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT, timeout=30)
        if config.SMTP_USE_TLS:
            server.starttls()
            
    server.login(config.SMTP_USER, config.SMTP_PASSWORD)
    server.sendmail(config.SMTP_USER, config.ALERT_EMAIL_RECIPIENT, msg.as_string())
    server.quit()
    
    logger.info("Backup email sent successfully.")
    if os.path.exists(zip_path):
        os.remove(zip_path)

if __name__ == "__main__":
    send_backup_email()
