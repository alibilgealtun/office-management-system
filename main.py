import cv2
import platform
from app.image_processing.service import PersonDetectionService
from app.common.logger import get_logger
from app.analytics.scheduler import setup_scheduler

logger = get_logger(__name__)

def main():
    service = None
    scheduler = None
    
    try:
        # Initialize services
        service = PersonDetectionService()
        scheduler = setup_scheduler()
        scheduler.start()
        
        logger.info("Starting main application loop")
        
        while True:
            try:
                frame = service.process_frame()
                if frame is not None:
                    cv2.imshow("Security Feed", frame)

                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        logger.info("Quitting the program")
                        break
                    elif key == ord('r'):
                        # Reset camera if needed
                        service.camera._initialize_camera()
                        
            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}")
                # Try to reinitialize camera
                try:
                    service.camera._initialize_camera()
                except:
                    break
    
    except Exception as e:
        logger.error(f"Fatal error in main application: {str(e)}")
    finally:
        if service:
            service.camera.release()
        if scheduler:
            scheduler.shutdown()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 