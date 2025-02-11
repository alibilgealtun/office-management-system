from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from app.common.logger import get_logger
from app.config import DATABASE_URL

logger = get_logger(__name__)

Base = declarative_base()

class Database:
    def __init__(self):
        try:
            self.engine = create_engine(
                DATABASE_URL,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10
            )
            self.Session = sessionmaker(bind=self.engine)
            Base.metadata.create_all(self.engine)
            logger.info("Database connection initialized")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise

    def save(self, record):
        """Saves a record to the database"""
        try:
            session = self.Session()
            session.add(record)
            session.commit()
            logger.debug(f"Saved record: {record}")
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving to database: {str(e)}")
            raise
        finally:
            session.close()

    def query(self, model, **kwargs):
        """Queries the database"""
        try:
            session = self.Session()
            return session.query(model).filter_by(**kwargs).all()
        except Exception as e:
            logger.error(f"Error querying database: {str(e)}")
            raise
        finally:
            session.close() 