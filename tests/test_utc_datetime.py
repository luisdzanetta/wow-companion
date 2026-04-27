"""Tests for the UTCDateTime TypeDecorator."""

from datetime import datetime, timezone, timedelta

import pytest
from sqlalchemy.exc import StatementError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.models import Character


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    s = TestSession()
    try:
        yield s
    finally:
        s.close()
        engine.dispose()


def test_utc_datetime_is_preserved(session):
    """A UTC datetime written and read back is unchanged."""
    char = Character(
        region="us", realm_slug="thrall", name_slug="test", display_name="Test"
    )
    expected = datetime(2026, 4, 27, 13, 37, 0, tzinfo=timezone.utc)
    char.created_at = expected
    session.add(char)
    session.commit()
    session.refresh(char)

    assert char.created_at == expected
    assert char.created_at.tzinfo is not None


def test_naive_datetime_is_rejected(session):
    """Writing a naive datetime raises ValueError."""
    char = Character(
        region="us", realm_slug="thrall", name_slug="test", display_name="Test"
    )
    char.created_at = datetime(2026, 4, 27, 13, 37, 0)  # naive!
    session.add(char)

    with pytest.raises((ValueError, StatementError), match="Naive datetime"):
        session.commit()


def test_non_utc_aware_is_normalized(session):
    """A datetime in a non-UTC timezone is converted to UTC on write."""
    brt = timezone(timedelta(hours=-3))  # Brasília
    char = Character(
        region="us", realm_slug="thrall", name_slug="test", display_name="Test"
    )
    char.created_at = datetime(2026, 4, 27, 10, 37, 0, tzinfo=brt)  # = 13:37 UTC
    session.add(char)
    session.commit()
    session.refresh(char)

    assert char.created_at.tzinfo == timezone.utc
    assert char.created_at.hour == 13