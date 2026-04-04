"""
Ultron Empire — Test Configuration
Shared fixtures for all tests.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.db.models import Base


@pytest.fixture(scope="session")
def db_engine():
    """Create a test database engine (SQLite for speed)."""
    engine = create_engine("sqlite:///test_ultron.db")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db_engine):
    """Create a test database session."""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()
