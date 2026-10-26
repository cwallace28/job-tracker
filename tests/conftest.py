import os
from pathlib import Path

import mysql.connector
import pytest

from tracker import db  # noqa: F401  (importing loads .env)

TEST_DB_NAME = "job_tracker_test"
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema.sql"


def _server_connection(database=None):
    """Connect with the .env credentials, optionally without selecting a database."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=database,
    )


@pytest.fixture(scope="session")
def test_database():
    """Create job_tracker_test (if needed) and apply schema.sql to it."""
    conn = _server_connection()
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {TEST_DB_NAME}")
    cursor.execute(f"USE {TEST_DB_NAME}")
    statements = [s.strip() for s in SCHEMA_PATH.read_text().split(";") if s.strip()]
    for statement in statements:
        cursor.execute(statement)
    conn.commit()
    cursor.close()
    conn.close()
    return TEST_DB_NAME


@pytest.fixture
def test_env(test_database, monkeypatch):
    """Point db.connect() at the test database instead of the real one."""
    monkeypatch.setenv("DB_NAME", test_database)


@pytest.fixture
def test_conn(test_env):
    """A dedicated connection to the test database, with tables emptied before and after."""
    conn = _server_connection(database=TEST_DB_NAME)
    _clean(conn)
    yield conn
    _clean(conn)
    conn.close()


def _clean(conn):
    assert conn.database == TEST_DB_NAME, "refusing to clean a non-test database"
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    for table in tables:
        cursor.execute(f"TRUNCATE TABLE {table}")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()
    cursor.close()
