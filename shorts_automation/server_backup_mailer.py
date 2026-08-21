import os
import smtplib
import zipfile
import logging
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from . import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("backup_mailer")

def create_backup_zip():
    backup_filename = f"server_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    backup_path = os.path.join(config.DATA_DIR, backup_filename)
    
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(config.BASE_DIR):
            for file in files:
                if file.endswith(('.py', '.json', '.db', '.sh', '.md', '.txt')):
                    abs_path = os.path.join(root, file)
                    rel_path = os.path.relpath(abs_path, config.BASE_DIR)
                    zipf.write(abs_path, rel_path)
                    
    return backup_path

def send_backup_email():
    if not config.ALERT_EMAIL_RECIPIENT or not config.SMTP_USER or not config.SMTP_PASSWORD:
        logger.info("E-posta ayarları eksik, yedek maili atlanıyor.")
        return
        
    zip_path = create_backup_zip()
    now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    msg = MIMEMultipart()
    msg["Subject"] = f"💾 [Sistem Yedeği] Haftalık Otomasyon Yedeği ({now_str})"
    msg["From"] = config.SMTP_USER
    msg["To"] = config.ALERT_EMAIL_RECIPIENT
    
    body = f"Merhaba,\n\n{now_str} tarihli sunucu otomasyon ve veritabanı yedeği ekte yer almaktadır."
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
    
    logger.info("Yedek e-postası başarıyla gönderildi.")
    if os.path.exists(zip_path):
        os.remove(zip_path)

if __name__ == "__main__":
    send_backup_email()
