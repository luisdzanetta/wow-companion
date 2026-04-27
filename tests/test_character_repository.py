"""Tests for CharacterRepository using an in-memory SQLite database."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.models import Character  # noqa: F401 — needed for metadata
from app.db.repositories.characters import CharacterRepository


@pytest.fixture
def session():
    """Provide a fresh in-memory SQLite session for each test."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def test_create_character(session):
    repo = CharacterRepository(session)
    char = repo.create(region="us", realm="Alterac Mountains", character_name="Stormpaladin")
    session.commit()

    assert char.id is not None
    assert char.region == "us"
    assert char.realm_slug == "alterac-mountains"
    assert char.name_slug == "stormpaladin"
    assert char.display_name == "Stormpaladin"


def test_get_or_create_returns_existing(session):
    repo = CharacterRepository(session)
    first, created_first = repo.get_or_create(
        region="us", realm="Thrall", character_name="Stormtroll"
    )
    session.commit()

    second, created_second = repo.get_or_create(
        region="us", realm="Thrall", character_name="Stormtroll"
    )

    assert created_first is True
    assert created_second is False
    assert first.id == second.id


def test_get_by_identity_is_case_insensitive(session):
    repo = CharacterRepository(session)
    repo.create(region="us", realm="Thrall", character_name="Stormtroll")
    session.commit()

    # Pass weird casings — should still find it
    found = repo.get_by_identity(region="US", realm_slug="THRALL", name_slug="StormTroll")
    assert found is not None
    assert found.name_slug == "stormtroll"


def test_list_all_returns_alphabetical_by_display_name(session):
    repo = CharacterRepository(session)
    repo.create(region="us", realm="Thrall", character_name="Stormtroll")
    repo.create(region="us", realm="Alterac Mountains", character_name="Stormpaladin")
    session.commit()

    chars = repo.list_all()
    names = [c.display_name for c in chars]
    assert names == ["Stormpaladin", "Stormtroll"]