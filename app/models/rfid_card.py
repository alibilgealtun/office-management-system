from sqlalchemy import Column, Integer, String, Boolean, DateTime, Index
from sqlalchemy.orm import relationship
from app.common.db import Base

class RFIDCard(Base):
    __tablename__ = 'rfid_cards'

    id = Column(Integer, primary_key=True)
    card_id = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False)

    # Relationship with records
    records = relationship("RFIDRecord", back_populates="card", cascade="all, delete-orphan")

    # Create indexes for faster queries
    __table_args__ = (
        Index('idx_rfid_cards_card_id', 'card_id'),
    )

    def __repr__(self):
        return f"<RFIDCard({self.name}, ID:{self.card_id}, Admin:{self.is_admin})>"