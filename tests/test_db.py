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


def count_companies(conn, name):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM companies WHERE name = %s", (name,))
    (count,) = cursor.fetchone()
    cursor.close()
    return count


def create_companies(*names):
    """Act as the caller: connect, create each company, commit, and close."""
    conn = db.connect()
    cursor = conn.cursor()
    ids = [db.get_or_create_company(cursor, name) for name in names]
    conn.commit()
    cursor.close()
    conn.close()
    return ids


def test_get_or_create_company_creates_missing_company(test_conn):
    (company_id,) = create_companies("Test Company")

    assert isinstance(company_id, int)
    assert count_companies(test_conn, "Test Company") == 1


def test_get_or_create_company_twice_returns_same_id(test_conn):
    first_id, second_id = create_companies("Test Company", "Test Company")

    assert first_id == second_id
    assert count_companies(test_conn, "Test Company") == 1


def test_get_or_create_company_distinct_names_get_distinct_ids(test_conn):
    first_id, second_id = create_companies("Company A", "Company B")

    assert first_id != second_id
