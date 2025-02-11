import serial
from app.common.logger import get_logger
from app.config import RFID_PORT, RFID_BAUDRATE

logger = get_logger(__name__)

class RFIDReader:
    def __init__(self):
        try:
            self.serial = serial.Serial(RFID_PORT, RFID_BAUDRATE)
            logger.info(f"RFID reader initialized on port {RFID_PORT}")
        except Exception as e:
            logger.error(f"Failed to initialize RFID reader: {str(e)}")
            raise

    def read_card(self):
        """Reads RFID card data from the serial port"""
        try:
            if self.serial.in_waiting:
                card_data = self.serial.readline().decode('utf-8').strip()
                logger.debug(f"Read card data: {card_data}")
                return card_data
            return None
        except Exception as e:
            logger.error(f"Error reading RFID card: {str(e)}")
            raise

    def close(self):
        """Closes the serial connection"""
        try:
            self.serial.close()
            logger.info("RFID reader connection closed")
        except Exception as e:
            logger.error(f"Error closing RFID reader: {str(e)}") 