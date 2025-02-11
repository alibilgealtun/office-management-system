import cv2
from app.image_processing.service import PersonDetectionService
from app.common.logger import get_logger
from app.analytics.scheduler import setup_scheduler

logger = get_logger(__name__)

def main():
    try:
        # Initialize services
        service = PersonDetectionService()
        scheduler = setup_scheduler()
        scheduler.start()
        
        logger.info("Starting main application loop")
        
        while True:
            try:
                frame = service.process_frame()
                cv2.imshow("Security Feed", frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    logger.info("Quitting the program")
                    break
            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}")
                break
    
    except Exception as e:
        logger.error(f"Fatal error in main application: {str(e)}")
    finally:
        service.camera.release()
        scheduler.shutdown()

if __name__ == "__main__":
    main() 