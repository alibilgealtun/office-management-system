import time
import datetime
import cv2
from app.common.logger import get_logger
from app.common.db import Database
from app.models.image_record import ImageRecord
from .camera import Camera
from .yolo_inference import YOLODetector

logger = get_logger(__name__)

class PersonDetectionService:
    CAPTURE_INTERVAL = 30         # Seconds between each batch capture
    CAPTURE_COUNT_AT_ONCE = 5     # Number of photos taken per batch
    CAPTURE_DELAY = 0.2          # Delay between individual captures in a batch
    ERROR_COOLDOWN = 20          # Seconds to wait after an error

    def __init__(self, camera=None, detector=None, db=None):
        self.camera = camera or Camera()
        self.detector = detector or YOLODetector()
        self.db = db or Database()
        self.last_capture_time = 0
        self.last_error_time = 0
        self.error_count = 0

    def process_frame(self):
        """
        Processes frames for display and detection.
        Handles errors gracefully and continues operation.
        """
        current_time = time.time()

        try:
            # Check if we're in error cooldown
            if self.error_count > 0 and (current_time - self.last_error_time) < self.ERROR_COOLDOWN:
                return None

            frame = self.camera.read_frame()
            if frame is None:
                raise RuntimeError("Failed to capture frame")

            frame_with_boxes = frame.copy()

            # Only perform detection and storage if the interval has passed
            if current_time - self.last_capture_time >= self.CAPTURE_INTERVAL:
                best_count = -1
                best_frame = None
                best_frame_with_boxes = None
                batch_success = False

                logger.info(f"Starting batch capture of {self.CAPTURE_COUNT_AT_ONCE} frames")
                
                # Take CAPTURE_COUNT_AT_ONCE photos with delay
                for i in range(self.CAPTURE_COUNT_AT_ONCE):
                    try:
                        frame = self.camera.read_frame()
                        if frame is not None:
                            person_boxes = self.detector.detect_persons(frame)
                            count = len(person_boxes)
                            
                            if count > best_count:
                                best_count = count
                                best_frame = frame.copy()
                                best_frame_with_boxes = self.detector.draw_boxes(frame.copy(), person_boxes)
                            
                            batch_success = True
                            logger.debug(f"Batch frame {i+1}: detected {count} persons")
                        
                        time.sleep(self.CAPTURE_DELAY)
                    except Exception as e:
                        logger.warning(f"Error capturing batch frame {i+1}: {e}")
                        continue

                if batch_success and best_frame is not None:
                    self._save_to_database(best_count, best_frame)
                    frame_with_boxes = best_frame_with_boxes
                    logger.info(f"Saved best frame with {best_count} persons from batch")
                    self.error_count = 0  # Reset error count on success
                
                self.last_capture_time = current_time

            return frame_with_boxes

        except Exception as e:
            self.error_count += 1
            self.last_error_time = current_time
            logger.error(f"Error in process_frame: {str(e)}")
            
            # Try to reinitialize camera if multiple errors occur
            if self.error_count >= 3:
                try:
                    logger.info("Attempting to reinitialize camera...")
                    self.camera._initialize_camera()
                    self.error_count = 0  # Reset error count if reinitialization succeeds
                except Exception as cam_error:
                    logger.error(f"Failed to reinitialize camera: {str(cam_error)}")
            
            return None

    def _save_to_database(self, count, frame):
        """Saves the frame and detection count to the database."""
        try:
            timestamp = datetime.datetime.now()
            image_data = cv2.imencode('.jpg', frame)[1].tobytes()
            record = ImageRecord(
                timestamp=timestamp,
                person_count=count,
                image_data=image_data
            )
            self.db.save(record)
            logger.debug(f"Saved frame with {count} persons at {timestamp}")
        except Exception as e:
            logger.error(f"Error saving to database: {str(e)}")