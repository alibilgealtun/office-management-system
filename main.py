import cv2
import multiprocessing as mp
import time
from app.image_processing.service import PersonDetectionService
from app.rfid.service import MFRC522Service
from app.common.logger import get_logger
from app.analytics.scheduler import setup_scheduler

logger = get_logger(__name__)

def rfid_process(stop_event):
    """Dedicated process for RFID monitoring"""
    try:
        logger.info("Starting RFID monitoring process")
        rfid_service = MFRC522Service()
        
        while not stop_event.is_set():
            try:
                # Read card
                card_id = rfid_service.read_card()
                if card_id:
                    logger.info(f"Card detected: {card_id}")
                
            except Exception as e:
                logger.error(f"Error in RFID monitoring: {str(e)}")
                time.sleep(0.5)
                
    except Exception as e:
        logger.error(f"Fatal error in RFID process: {str(e)}")
    finally:
        if rfid_service:
            rfid_service.cleanup()

def image_process(stop_event):
    """Dedicated process for image processing"""
    try:
        logger.info("Starting image processing process")
        image_service = PersonDetectionService()
        
        while not stop_event.is_set():
            try:
                frame = image_service.process_frame()
                if frame is not None:
                    cv2.imshow("Security Feed", frame)

                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        logger.info("Quit signal received")
                        stop_event.set()
                        break
                    elif key == ord('r'):
                        image_service.camera._initialize_camera()
                else:
                    # When no frame is captured, yield a bit of CPU time
                    time.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"Error in image processing: {str(e)}")
                try:
                    image_service.camera._initialize_camera()
                except:
                    stop_event.set()
                    break
                
    except Exception as e:
        logger.error(f"Fatal error in image process: {str(e)}")
    finally:
        if image_service:
            image_service.camera.release()
        cv2.destroyAllWindows()

def main():
    # Create a shared event for stopping processes
    stop_event = mp.Event()
    
    try:
        # Start RFID process
        rfid_proc = mp.Process(
            target=rfid_process,
            args=(stop_event,),
            daemon=True
        )
        rfid_proc.start()
        
        # Start image processing process
        image_proc = mp.Process(
            target=image_process,
            args=(stop_event,),
            daemon=True
        )
        image_proc.start()
        
        # Start scheduler in main process
        scheduler = setup_scheduler()
        scheduler.start()
        
        logger.info("Main application running - Press Ctrl+C to quit")
        
        # Wait for processes to finish
        while True:
            if stop_event.is_set() or not rfid_proc.is_alive() or not image_proc.is_alive():
                break
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
    except Exception as e:
        logger.error(f"Fatal error in main application: {str(e)}")
    finally:
        # Cleanup
        stop_event.set()
        
        # Wait for processes to finish
        rfid_proc.join(timeout=2)
        image_proc.join(timeout=2)
        
        # Force terminate if necessary
        if rfid_proc.is_alive():
            rfid_proc.terminate()
        if image_proc.is_alive():
            image_proc.terminate()
            
        if scheduler:
            scheduler.shutdown()

if __name__ == "__main__":
    # Required for Windows support
    mp.freeze_support()
    main() 