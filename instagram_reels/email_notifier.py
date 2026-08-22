import smtplib
import logging
import os
import shutil
import platform
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from . import config

logger = logging.getLogger("instagram.notifier")

def get_system_diagnostics():
    report = ["=== System Diagnostics ==="]
    # Disk space check
    try:
        total, used, free = shutil.disk_usage(".")
        report.append(f"Disk Space: Total: {total // 2**30}GB | Used: {used // 2**30}GB | Free: {free // 2**30}GB")
    except Exception:
        pass
    # CPU load average (Linux only)
    if hasattr(os, 'getloadavg'):
        try:
            load = os.getloadavg()
            report.append(f"CPU Load: 1m: {load[0]}, 5m: {load[1]}, 15m: {load[2]}")
        except Exception:
            pass
    report.append(f"Python Version: {platform.python_version()}")
    report.append(f"Platform: {platform.system()} {platform.release()}")
    return "\n".join(report)

def send_notification_email(platform_name: str, status: str, title: str = "", url: str = "", error_msg: str = "", attachments: list = None):
    if not config.ALERT_EMAIL_RECIPIENT or not config.SMTP_USER or not config.SMTP_PASSWORD:
        return False

    is_success = (status.upper() == "SUCCESS")
    subject_status = "✅ Post Successful" if is_success else "❌ Post Failed!"
    subject = f"[{platform_name}] {subject_status}: {title[:50]}"
    now_str = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    diagnostics = ""
    if not is_success:
        diagnostics = get_system_diagnostics()

    if is_success:
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f7; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: #ffffff; padding: 25px; border-radius: 8px; border-top: 5px solid #28a745;">
                <h2 style="color: #28a745; margin-top: 0;">🍿 Instagram Reel Published!</h2>
                <p><strong>Platform:</strong> {platform_name}</p>
                <p><strong>Movie / Show:</strong> {title}</p>
                <p><strong>Publish Time:</strong> {now_str}</p>
                <div style="margin: 25px 0;">
                    <a href="{url}" style="background-color: #E1306C; color: #ffffff; padding: 12px 20px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">View Reel ↗</a>
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
                <h2 style="color: #dc3545; margin-top: 0;">⚠️ Instagram Upload Error Occurred</h2>
                <p><strong>Platform:</strong> {platform_name}</p>
                <p><strong>Target Movie / Show:</strong> {title if title else 'Unknown'}</p>
                <p><strong>Failure Time:</strong> {now_str}</p>
                <h4 style="color: #dc3545; margin-bottom: 5px;">Error Message:</h4>
                <pre style="background-color: #f8f9fa; border-left: 3px solid #dc3545; padding: 12px; font-size: 13px; white-space: pre-wrap; font-family: monospace;">{error_msg}</pre>
                <h4 style="color: #6c757d; margin-bottom: 5px;">Diagnostics Report:</h4>
                <pre style="background-color: #f8f9fa; border-left: 3px solid #6c757d; padding: 12px; font-size: 13px; white-space: pre-wrap; font-family: monospace;">{diagnostics}</pre>
            </div>
        </body>
        </html>
        """

    # Use 'mixed' type to allow both alternative html body and file attachments
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = config.SMTP_USER
    msg["To"] = config.ALERT_EMAIL_RECIPIENT

    body_container = MIMEMultipart("alternative")
    body_container.attach(MIMEText(html_body, "html", "utf-8"))
    msg.attach(body_container)

    # Attach diagnostic log files if specified
    if attachments:
        for file_path in attachments:
            if os.path.exists(file_path):
                try:
                    with open(file_path, "rb") as f:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
                    msg.attach(part)
                except Exception as e:
                    logger.error(f"Failed to attach diagnostic file {file_path}: {e}")

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
        logger.info(f"Notification email sent successfully to {config.ALERT_EMAIL_RECIPIENT}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email notification: {e}")
        return False
