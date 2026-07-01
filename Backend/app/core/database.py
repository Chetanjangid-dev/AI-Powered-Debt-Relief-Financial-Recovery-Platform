import sys
import os

# Add Database/ folder to Python path so we can import teammate's modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "Database"))

from database import SessionLocal, engine, Base
from app.core.config import settings


def get_db():
    """
    Dependency function for FastAPI routes.
    Yields a database session and closes it after the request is done.
    Usage in routes: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """
    Creates all tables if they don't exist.
    Called once on application startup.
    """
    Base.metadata.create_all(bind=engine)