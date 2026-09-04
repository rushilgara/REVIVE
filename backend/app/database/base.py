import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import declarative_base
from app.utils.timestamps import utc_now

Base = declarative_base()


class TimestampMixin:
    """Provides created_at and updated_at UTC timestamps."""
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


def generate_uuid() -> str:
    return str(uuid.uuid4())
