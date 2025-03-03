from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.common.db import Base

class RFIDRecord(Base):
    __tablename__ = 'rfid_records'

    id = Column(Integer, primary_key=True)
    card_id = Column(String, ForeignKey('rfid_cards.card_id'), nullable=False)
    name = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_entry = Column(Boolean, nullable=False)  # True for entry, False for exit

    # Relationship with RFIDCard
    card = relationship("RFIDCard", back_populates="records")

    # Create indexes for faster queries
    __table_args__ = (
        Index('idx_rfid_records_card_id', 'card_id'),
        Index('idx_rfid_records_timestamp', 'timestamp'),
    )

    def __repr__(self):
        action = "Entry" if self.is_entry else "Exit"
        return f"<RFIDRecord({action}, {self.name}, {self.timestamp})>" 