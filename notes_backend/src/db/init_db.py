from __future__ import annotations

from sqlalchemy.exc import SQLAlchemyError

from src.db.models import Base
from src.db.session import engine


# PUBLIC_INTERFACE
def init_db() -> None:
    """Initialize database schema (creates tables if they don't exist)."""
    try:
        Base.metadata.create_all(bind=engine)
    except SQLAlchemyError as exc:
        # Re-raise with context; FastAPI startup handler will surface it.
        raise RuntimeError("Database initialization failed") from exc
