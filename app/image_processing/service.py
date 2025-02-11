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
        self.previous_count = 0
        self.DEBOUNCE_FRAMES = 5
        self.enter_counter = 0
        self.leave_counter = 0
        self.count_history = deque(maxlen=self.DEBOUNCE_FRAMES)
        logger.info("PersonDetectionService initialized")

    def process_frame(self):
        try:
            frame = self.camera.read_frame()
            person_boxes = self.detector.detect_persons(frame)
            current_count = len(person_boxes)

            self.count_history.append(current_count)
            most_common_count = max(set(self.count_history), key=self.count_history.count)

            self._handle_count_changes(most_common_count)
            self._save_to_database(current_count, frame)
            
            frame = self.detector.draw_boxes(frame, person_boxes)
            return frame
        except Exception as e:
            logger.error(f"Error processing frame: {str(e)}")
            raise

    def _handle_count_changes(self, most_common_count):
        try:
            if most_common_count > self.previous_count:
                self.enter_counter += 1
                self.leave_counter = 0
                if self.enter_counter == self.DEBOUNCE_FRAMES:
                    num_entered = most_common_count - self.previous_count
                    logger.info(f"{num_entered} Person(s) Entered at {datetime.datetime.now()}")
                    self.previous_count = most_common_count
                    self.enter_counter = 0
            elif most_common_count < self.previous_count:
                self.leave_counter += 1
                self.enter_counter = 0
                if self.leave_counter == self.DEBOUNCE_FRAMES:
                    num_left = self.previous_count - most_common_count
                    logger.info(f"{num_left} Person(s) Left at {datetime.datetime.now()}")
                    self.previous_count = most_common_count
                    self.leave_counter = 0
            else:
                self.enter_counter = 0
                self.leave_counter = 0
        except Exception as e:
            logger.error(f"Error handling count changes: {str(e)}")
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