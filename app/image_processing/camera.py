import cv2
import platform
import os
from app.common.logger import get_logger

logger = get_logger(__name__)

class Camera:
    def __init__(self, camera_id=0):
        self.camera_id = camera_id
        self.cap = None
        self._initialize_camera()

    def _initialize_camera(self):
        try:
            system = platform.system().lower()
            
            # Release existing capture if any
            if self.cap is not None:
                self.cap.release()
            
            if system == 'darwin':  # macOS
                # Try to use AVFoundation backend for macOS
                self.cap = cv2.VideoCapture(self.camera_id)
                if not self.cap.isOpened():
                    # Try with different backend
                    self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_AVFOUNDATION)
            elif system == 'windows':
                self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW)
            else:  # Linux and others
                self.cap = cv2.VideoCapture(self.camera_id)
            
            if not self.cap.isOpened():
                # Try different camera indices if the first one fails
                for i in range(1, 5):
                    if system == 'darwin':
                        self.cap = cv2.VideoCapture(i, cv2.CAP_AVFOUNDATION)
                    elif system == 'windows':
                        self.cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                    else:
                        self.cap = cv2.VideoCapture(i)
                    if self.cap.isOpened():
                        self.camera_id = i
                        break
                
                if not self.cap.isOpened():
                    raise RuntimeError("Cannot open camera")
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            # For macOS, try to disable auto focus and exposure
            if system == 'darwin':
                self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
                self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
            
            logger.info(f"Camera initialized successfully with ID {self.camera_id}")
            
        except Exception as e:
            logger.error(f"Error initializing camera: {str(e)}")
            raise RuntimeError(f"Failed to initialize camera: {str(e)}")

    def read_frame(self):
        if self.cap is None or not self.cap.isOpened():
            self._initialize_camera()
            
        for _ in range(3):  # Try up to 3 times to read a frame
            ret, frame = self.cap.read()
            if ret:
                return cv2.resize(frame, (640, 480))
            
        logger.error("Failed to capture frame from camera")
        raise RuntimeError("Failed to capture frame from camera")

    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        cv2.destroyAllWindows() 