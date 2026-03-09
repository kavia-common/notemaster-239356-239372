from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.core.settings import get_settings

_settings = get_settings()

# Engine: keep it simple (sync SQLAlchemy) for template friendliness.
engine = create_engine(_settings.sqlalchemy_database_uri(), pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# PUBLIC_INTERFACE
def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a SQLAlchemy session and ensures it is closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def db_context() -> Generator[Session, None, None]:
    """Context manager for scripts/one-offs."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
