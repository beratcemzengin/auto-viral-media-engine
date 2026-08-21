import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from . import config

logger = logging.getLogger("shorts.notifier")

def send_notification_email(platform: str, status: str, title: str = "", url: str = "", error_msg: str = ""):
    if not config.ALERT_EMAIL_RECIPIENT or not config.SMTP_USER or not config.SMTP_PASSWORD:
        logger.info("E-posta bildirim ayarları yapılandırılmamış, bildirim atlanıyor.")
        return False

    is_success = (status.upper() == "SUCCESS")
    subject_status = "✅ Paylaşım Başarılı" if is_success else "❌ Paylaşım Başarısız Oldu!"
    subject = f"[{platform}] {subject_status}: {title[:50]}"
    now_str = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    if is_success:
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f7; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: #ffffff; padding: 25px; border-radius: 8px; border-top: 5px solid #28a745;">
                <h2 style="color: #28a745; margin-top: 0;">🎉 Otomatik Paylaşım Başarılı!</h2>
                <p><strong>Platform:</strong> {platform}</p>
                <p><strong>İçerik Başlığı:</strong> {title}</p>
                <p><strong>Paylaşım Zamanı:</strong> {now_str}</p>
                <div style="margin: 25px 0;">
                    <a href="{url}" style="background-color: #007bff; color: #ffffff; padding: 12px 20px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">İçeriği Görüntüle ↗</a>
                </div>
            </div>
        </body>
        </html>
        """
    else:
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f7; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: #ffffff; padding: 25px; border-radius: 8px; border-top: 5px solid #dc3545;">
                <h2 style="color: #dc3545; margin-top: 0;">⚠️ Otomasyon Hatası Oluştu</h2>
                <p><strong>Platform:</strong> {platform}</p>
                <p><strong>Hedef İçerik:</strong> {title if title else 'Belirlenemedi'}</p>
                <p><strong>Hata Zamanı:</strong> {now_str}</p>
                <pre style="background-color: #f8f9fa; border-left: 3px solid #dc3545; padding: 12px; font-size: 13px;">{error_msg}</pre>
            </div>
        </body>
        </html>
        """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = config.SMTP_USER
    msg["To"] = config.ALERT_EMAIL_RECIPIENT
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        if config.SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(config.SMTP_SERVER, config.SMTP_PORT, timeout=15)
        else:
            server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT, timeout=15)
            if config.SMTP_USE_TLS:
                server.starttls()

        server.login(config.SMTP_USER, config.SMTP_PASSWORD)
        server.sendmail(config.SMTP_USER, config.ALERT_EMAIL_RECIPIENT, msg.as_string())
        server.quit()
        logger.info(f"E-posta başarıyla gönderildi: {config.ALERT_EMAIL_RECIPIENT}")
        return True
    except Exception as e:
        logger.error(f"E-posta gönderme hatası: {e}")
        return False
