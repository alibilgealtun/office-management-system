import time
from collections import deque
import datetime
import cv2
from app.common.logger import get_logger
from app.common.db import Database
from app.models.image_record import ImageRecord
from .camera import Camera
from .yolo_inference import YOLODetector

logger = get_logger(__name__)

class PersonDetectionService:
    def __init__(self):
        self.camera = Camera()
        self.detector = YOLODetector()
        self.db = Database()
        self.previous_count = 0  # Track previous person count
        self.last_capture_time = 0  # Track last image capture time
        self.CAPTURE_INTERVAL = 2  # Minimum seconds between captures

    def capture_and_store_image(self):
        current_time = time.time()
        if current_time - self.last_capture_time < self.CAPTURE_INTERVAL:
            logger.info("Skipping capture to avoid excessive image storage.")
            return

        frame = self.camera.capture_frame()
        if frame is not None:
            timestamp = datetime.datetime.now()
            image_path = f"images/{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
            cv2.imwrite(image_path, frame)
            self.db.insert(ImageRecord(timestamp=timestamp, image_path=image_path))
            logger.info(f"Image saved at {image_path}")
            self.last_capture_time = current_time  # Update last capture time

    def process_frame(self):
        try:
            frame = self.camera.read_frame()
            if frame is None:
                logger.warning("No frame captured from camera.")
                return

            person_boxes = self.detector.detect_persons(frame)
            current_count = len(person_boxes)

            if current_count != self.previous_count:
                logger.info(f"Person count changed: {self.previous_count} -> {current_count}")
                self._save_to_database(current_count, frame)
                self.previous_count = current_count

            frame_with_boxes = self.detector.draw_boxes(frame, person_boxes)
            return frame_with_boxes

        except Exception as e:
            logger.error(f"Error in process_frame: {str(e)}")
            raise

    def _save_to_database(self, count, frame):
        try:
            timestamp = datetime.datetime.now()
            record = ImageRecord(
                timestamp=timestamp,
                person_count=count,
                image_data=cv2.imencode('.jpg', frame)[1].tobytes()
            )
            self.db.save(record)
            logger.debug(f"Saved record to database: {count} persons at {timestamp}")
        except Exception as e:
            logger.error(f"Error saving to database: {str(e)}")
            raise

    def run(self):
        while True:
            try:
                self.process_frame()
                time.sleep(0.5)  # Small delay to prevent excessive CPU usage
            except Exception as e:
                logger.error(f"Error in detection loop: {e}")
                time.sleep(2)  # Delay before retrying to prevent crash loops