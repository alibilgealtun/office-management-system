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

    def send_report(self, report_content):
        """Sends the daily report via email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = self.recipient
            msg['Subject'] = f"Daily Usage Analysis Report - {datetime.today().date()}"
            msg.attach(MIMEText(report_content, 'html'))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            logger.info(f"Report sent successfully to {self.recipient}")
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            raise 