import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.common.logger import get_logger
from app.config import (
    SMTP_HOST, SMTP_PORT, SMTP_USERNAME,
    SMTP_PASSWORD, REPORT_RECIPIENT
)

logger = get_logger(__name__)

class EmailNotifier:
    def __init__(self):
        self.smtp_host = SMTP_HOST
        self.smtp_port = SMTP_PORT
        self.username = SMTP_USERNAME
        self.password = SMTP_PASSWORD
        self.recipient = REPORT_RECIPIENT
        logger.info("Email notifier initialized")

    def send_report(self, html_content):
        """Send HTML report via email"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = SMTP_USERNAME
            msg['To'] = REPORT_RECIPIENT
            msg['Subject'] = f"Daily Office Usage Report - {datetime.now().date()}"

            # Attach HTML content
            msg.attach(MIMEText(html_content, 'html'))

            # Send email
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(msg)

            logger.info("HTML report email sent successfully")
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            raise 