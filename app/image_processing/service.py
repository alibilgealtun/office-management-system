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

    def __init__(self, camera=None, detector=None, db=None):
        self.camera = camera or Camera()
        self.detector = detector or YOLODetector()
        self.db = db or Database()
        self.last_capture_time = 0

    def process_frame(self):
        """
        Processes frames for display and detection.
        When capture interval is reached:
        - Takes multiple photos in rapid succession
        - Selects the one with maximum person count
        - Saves only the best frame to database
        Otherwise, just returns the current frame.
        """
        try:
            frame = self.camera.read_frame()
            if frame is None:
                return None

            current_time = time.time()
            frame_with_boxes = frame.copy()  # Initialize with original frame

            # Only perform detection and storage if the interval has passed
            if current_time - self.last_capture_time >= self.CAPTURE_INTERVAL:
                # Variables to track the best frame
                best_count = -1
                best_frame = None
                best_frame_with_boxes = None

                logger.info(f"Starting batch capture of {self.CAPTURE_COUNT_AT_ONCE} frames")
                
                # Take CAPTURE_COUNT_AT_ONCE photos with delay
                for i in range(self.CAPTURE_COUNT_AT_ONCE):
                    try:
                        frame = self.camera.read_frame()
                        if frame is not None:
                            # Detect persons
                            person_boxes = self.detector.detect_persons(frame)
                            count = len(person_boxes)
                            
                            # Update best frame if this one has more persons
                            if count > best_count:
                                best_count = count
                                best_frame = frame.copy()
                                best_frame_with_boxes = self.detector.draw_boxes(frame.copy(), person_boxes)
                            
                            logger.debug(f"Batch frame {i+1}: detected {count} persons")
                        
                        time.sleep(self.CAPTURE_DELAY)  # Wait before next capture
                    except Exception as e:
                        logger.error(f"Error capturing batch frame {i+1}: {e}")

                # Save only the best frame from the batch
                if best_frame is not None:
                    self._save_to_database(best_count, best_frame)
                    frame_with_boxes = best_frame_with_boxes
                    logger.info(f"Saved single best frame with {best_count} persons from batch of {self.CAPTURE_COUNT_AT_ONCE}")
                
                self.last_capture_time = current_time

            return frame_with_boxes

        except Exception as e:
            logger.error(f"Error in process_frame: {str(e)}")
            raise

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
            logger.debug(f"Saved frame with {count} persons at {timestamp}")  # Changed to debug level
        except Exception as e:
            logger.error(f"Error saving to database: {str(e)}")
            raise