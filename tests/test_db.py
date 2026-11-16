import mysql.connector
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


def add_applications(*calls):
    """Act as the caller: add each application (kwargs dict), commit, and close."""
    conn = db.connect()
    cursor = conn.cursor()
    ids = [db.add_application(cursor, **kwargs) for kwargs in calls]
    conn.commit()
    cursor.close()
    conn.close()
    return ids


def fetch_all(conn, query, params=()):
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    return rows


APP = dict(company_name="Acme", title="Engineer", source="LinkedIn", applied_on="2026-01-15")


def test_add_application_inserts_new_row(test_conn):
    (app_id,) = add_applications(APP)

    assert isinstance(app_id, int)
    rows = fetch_all(test_conn, "SELECT title, source, current_status FROM applications")
    assert rows == [("Engineer", "LinkedIn", "applied")]


def test_add_application_stores_optional_fields(test_conn):
    add_applications({**APP, "job_url": "https://example.com/job", "follow_up_on": "2026-01-29"})

    ((url, follow_up),) = fetch_all(test_conn, "SELECT job_url, follow_up_on FROM applications")
    assert url == "https://example.com/job"
    assert str(follow_up) == "2026-01-29"


def test_add_application_duplicate_returns_same_id(test_conn):
    first_id, second_id = add_applications(APP, APP)

    assert first_id == second_id
    assert fetch_all(test_conn, "SELECT COUNT(*) FROM applications") == [(1,)]
    assert fetch_all(test_conn, "SELECT COUNT(*) FROM status_history") == [(1,)]


@pytest.mark.parametrize(
    "change",
    [
        {"title": "Senior Engineer"},
        {"source": "Indeed"},
        {"applied_on": "2026-02-01"},
        {"company_name": "Other Co"},
    ],
)
def test_add_application_differing_field_creates_new_row(test_conn, change):
    first_id, second_id = add_applications(APP, {**APP, **change})

    assert first_id != second_id
    assert fetch_all(test_conn, "SELECT COUNT(*) FROM applications") == [(2,)]


def test_add_application_records_initial_status_history(test_conn):
    (app_id,) = add_applications(APP)

    rows = fetch_all(test_conn, "SELECT application_id, status, changed_at FROM status_history")
    assert len(rows) == 1
    assert rows[0][0] == app_id
    assert rows[0][1] == "applied"
    assert str(rows[0][2]).startswith("2026-01-15")


def test_schema_enforces_unique_application(test_conn):
    (app_id,) = add_applications(APP)
    (company_id,) = fetch_all(test_conn, "SELECT company_id FROM applications WHERE id = %s", (app_id,))[0]

    cursor = test_conn.cursor()
    with pytest.raises(mysql.connector.IntegrityError):
        cursor.execute(
            "INSERT INTO applications (company_id, title, source, applied_on) VALUES (%s, %s, %s, %s)",
            (company_id, APP["title"], APP["source"], APP["applied_on"]),
        )
    cursor.close()
