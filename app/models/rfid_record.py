from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.common.db import Base

class RFIDRecord(Base):
    __tablename__ = 'rfid_records'

    id = Column(Integer, primary_key=True)
    card_id = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_entry = Column(Boolean, nullable=False)  # True for entry, False for exit

    def __repr__(self):
        return f"<RFIDRecord(id={self.id}, card_id={self.card_id}, timestamp={self.timestamp}, is_entry={self.is_entry})>" 