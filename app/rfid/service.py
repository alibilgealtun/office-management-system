import datetime
from app.common.logger import get_logger
from app.common.db import Database
from app.models.rfid_record import RFIDRecord
from .rfid_reader import RFIDReader

logger = get_logger(__name__)

class RFIDService:
    def __init__(self):
        self.reader = RFIDReader()
        self.db = Database()
        self.last_readings = {}  # To track entry/exit status
        logger.info("RFID service initialized")

    def process_card_reading(self):
        try:
            card_data = self.reader.read_card()
            if card_data:
                self._handle_card_data(card_data)
        except Exception as e:
            logger.error(f"Error processing card reading: {str(e)}")
            raise

    def _handle_card_data(self, card_data):
        try:
            timestamp = datetime.datetime.now()
            last_reading = self.last_readings.get(card_data)
            
            # If no previous reading or last reading was more than 1 minute ago,
            # consider it as a new entry/exit
            if (not last_reading or 
                (timestamp - last_reading['timestamp']).total_seconds() > 60):
                
                # Toggle entry/exit status
                is_entry = not last_reading['is_entry'] if last_reading else True
                
                record = RFIDRecord(
                    card_id=card_data,
                    timestamp=timestamp,
                    is_entry=is_entry
                )
                self.db.save(record)
                
                self.last_readings[card_data] = {
                    'timestamp': timestamp,
                    'is_entry': is_entry
                }
                
                logger.info(f"Card {card_data} {'entered' if is_entry else 'exited'} at {timestamp}")
        except Exception as e:
            logger.error(f"Error handling card data: {str(e)}")
            raise

    def close(self):
        """Closes the RFID reader connection"""
        self.reader.close() 