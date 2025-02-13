import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

load_dotenv()

# Database
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/image_processing"
)


# YOLO settings
YOLO_CONFIDENCE_THRESHOLD = 0.5

# Camera settings
CAMERA_ID = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# RFID settings
RFID_PORT = os.getenv("RFID_PORT", "/dev/ttyUSB0")  # Default USB port for RFID reader
RFID_BAUDRATE = 9600

# DeepSeek settings
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# Scheduler settings
IMAGE_PROCESSING_INTERVAL = 30  # seconds
REPORT_GENERATION_TIME = "0 21 * * *"  # This means 21:00 (9 PM) every day

# Email settings
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
REPORT_RECIPIENT = os.getenv("REPORT_RECIPIENT") 