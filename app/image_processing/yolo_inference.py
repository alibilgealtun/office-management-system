import torch
import cv2
from app.common.logger import get_logger
from app.config import YOLO_CONFIDENCE_THRESHOLD

logger = get_logger(__name__)

class YOLODetector:
    def __init__(self):
        try:
            # for CPU optimization
            torch.set_num_threads(2)
            self.model = torch.hub.load('ultralytics/yolov5', 'yolov5n', pretrained=True)
            self.model.classes = [0]  # Only detect 'person' class
            logger.info("YOLOv5 model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load YOLOv5 model: {str(e)}")
            raise

    def detect_persons(self, frame):
        try:
            # Resize for model 5n
            resized_frame = cv2.resize(frame, (640, 640))
            results = self.model(resized_frame)
            detections = results.xyxy[0]  # Bounding box'lar, skor ve sınıf id'leri

            person_boxes = []
            for *box, score, cls in detections:
                if int(cls) == 0 and score > YOLO_CONFIDENCE_THRESHOLD:
                    person_boxes.append(box)

            logger.debug(f"Detected {len(person_boxes)} persons in frame")
            return person_boxes
        except Exception as e:
            logger.error(f"Error during person detection: {str(e)}")
            raise

    def draw_boxes(self, frame, boxes):
        try:
            for box in boxes:
                x1, y1, x2, y2 = map(int, box)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            return frame
        except Exception as e:
            logger.error(f"Error drawing bounding boxes: {str(e)}")
            raise 