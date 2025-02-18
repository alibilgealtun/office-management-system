from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.common.logger import get_logger
from app.config import IMAGE_PROCESSING_INTERVAL, REPORT_GENERATION_TIME
from app.image_processing.service import PersonDetectionService
from .report_generator import ReportGenerator
from .email_notifier import EmailNotifier

logger = get_logger(__name__)

def setup_scheduler():
    """Sets up and configures the application scheduler"""
    try:
        scheduler = BackgroundScheduler()
        
        # Remove the image processing job since it's now handled in process_frame
        
        # Report generation and email job - runs daily at specified time
        report_generator = ReportGenerator()
        email_notifier = EmailNotifier()
        
        def generate_and_send_report():
            try:
                report = report_generator.generate_daily_report()
                email_notifier.send_report(report)
            except Exception as e:
                logger.error(f"Error in generate_and_send_report: {str(e)}")
        
        # Parse the cron expression
        try:
            scheduler.add_job(
                generate_and_send_report,
                CronTrigger.from_crontab(REPORT_GENERATION_TIME),
                id='daily_report_job'
            )
        except Exception as e:
            logger.error(f"Error setting up daily report job: {str(e)}")
            # Fallback to a default time if cron expression is invalid
            scheduler.add_job(
                generate_and_send_report,
                'cron',
                hour=21,
                minute=0,
                id='daily_report_job'
            )
        
        logger.info("Scheduler initialized successfully")
        return scheduler
    except Exception as e:
        logger.error(f"Error setting up scheduler: {str(e)}")
        raise 