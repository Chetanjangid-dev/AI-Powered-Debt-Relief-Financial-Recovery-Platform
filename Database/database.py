"""
database.py
------------
Creates the SQLAlchemy engine, session, and Base class.
Every model in models.py inherits from Base defined here.
Backend (FastAPI) will import `get_db` as a dependency to access the DB session.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite file will be created at project root as debt_relief.db
SQLALCHEMY_DATABASE_URL = "sqlite:///./debt_relief.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency for FastAPI routes.
    Usage in backend: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()