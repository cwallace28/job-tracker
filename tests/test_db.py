import pytest

from tracker import db

REQUIRED = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]


@pytest.fixture
def full_env(monkeypatch):
    """Give every required variable a fake value."""
    for name in REQUIRED:
        monkeypatch.setenv(name, "x")


@pytest.mark.parametrize("missing", REQUIRED)
def test_connect_names_a_missing_variable(full_env, monkeypatch, missing):
    monkeypatch.delenv(missing)

    with pytest.raises(RuntimeError) as excinfo:
        db.connect()

    assert missing in str(excinfo.value)


def test_connect_lists_every_missing_variable(full_env, monkeypatch):
    monkeypatch.delenv("DB_NAME")
    monkeypatch.delenv("DB_USER")

    with pytest.raises(RuntimeError) as excinfo:
        db.connect()

    message = str(excinfo.value)
    assert "DB_NAME" in message
    assert "DB_USER" in message
    assert "DB_HOST" not in message