import pytest

from backend.app import db


@pytest.fixture(autouse=True)
def isolate_db(tmp_path, monkeypatch):
    """Every test gets its own throwaway SQLite file - never touches the
    real app.db, and tests can't see each other's history rows."""
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
