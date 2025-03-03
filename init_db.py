from sqlalchemy import create_engine
from app.models.image_record import Base as ImageBase
from app.models.rfid_card import Base as RFIDCardBase
from app.models.rfid_record import Base as RFIDRecordBase
from app.config import DATABASE_URL

def init_db():
    engine = create_engine(DATABASE_URL)
    
    # Create tables in the correct order
    # 1. Create image_records table
    ImageBase.metadata.create_all(engine)
    
    # 2. Create rfid_cards table
    RFIDCardBase.metadata.create_all(engine)
    
    # 3. Create rfid_records table (depends on rfid_cards)
    RFIDRecordBase.metadata.create_all(engine)
    
    print("Database tables created successfully")

if __name__ == "__main__":
    init_db() 