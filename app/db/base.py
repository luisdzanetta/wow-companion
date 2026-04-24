"""Base class for all ORM models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared base class. All ORM models should inherit from this."""
    pass