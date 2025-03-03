from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.common.logger import get_logger
from app.config import IMAGE_PROCESSING_INTERVAL, REPORT_GENERATION_TIME
from app.image_processing.service import PersonDetectionService
from .report_generator import ReportGenerator
from .email_notifier import EmailNotifier

logger = get_logger(__name__)

def setup_scheduler(rfid_service=None):
    """Sets up and configures the application scheduler"""
    try:
        scheduler = BackgroundScheduler()
        
        # Remove the image processing job since it's now handled in process_frame
        
        # Report generation and email job - runs daily at specified time
        report_generator = ReportGenerator()
        email_notifier = EmailNotifier()
        
        def generate_and_send_report():
            """Generate and send daily report"""
            try:
                report = report_generator.generate_daily_report()
                email_notifier.send_report(report)
                logger.info("Daily report generated and sent successfully")
            except Exception as e:
                logger.error(f"Error generating/sending daily report: {str(e)}")
        
        # Schedule daily report generation
        scheduler.add_job(
            generate_and_send_report,
            CronTrigger.from_crontab(REPORT_GENERATION_TIME)
        )
        
        # Add admin card report generation capability to RFID service
        if rfid_service:
            rfid_service.report_generator = report_generator
            rfid_service.email_notifier = email_notifier
            logger.info("Added report generation capability to RFID service")
        
        logger.info("Scheduler initialized successfully")
        return scheduler
    except Exception as e:
        logger.error(f"Error setting up scheduler: {str(e)}")
        raise 