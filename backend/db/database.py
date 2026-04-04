"""
Ultron Empire — Database Connection
SQLAlchemy engine, session factory, and dependency injection.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

from backend.config import settings
from backend.db.models import Base


engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=(settings.APP_ENV == "development"),
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create all tables. Use Alembic for production migrations."""
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db_session():
    """Context manager for database sessions."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db() -> Session:
    """Get a database session. For use in FastAPI dependencies."""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


async def get_db_dep():
    """FastAPI async dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
