from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, LargeBinary
from app.common.db import Base

class ImageRecord(Base):
    __tablename__ = 'image_records'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    person_count = Column(Integer, nullable=False)
    image_data = Column(LargeBinary)

    def __repr__(self):
        return f"<ImageRecord(id={self.id}, timestamp={self.timestamp}, person_count={self.person_count})>" 