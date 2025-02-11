import cv2
from app.common.logger import get_logger

logger = get_logger(__name__)

class Camera:
    def __init__(self, camera_id=0):
        self.cap = cv2.VideoCapture(camera_id)
        if not self.cap.isOpened():
            logger.error("Cannot open camera")
            raise RuntimeError("Cannot open camera")

    def read_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            logger.error("Failed to capture frame from camera")
            raise RuntimeError("Failed to capture frame from camera")
        return cv2.resize(frame, (640, 480))

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows() 