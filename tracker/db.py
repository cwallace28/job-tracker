import os
from typing import cast
import mysql.connector
from dotenv import find_dotenv, load_dotenv


load_dotenv()

REQUIRED_VARS = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]

# established connection to the MySQL database using env variables
# from the .env file
def connect():
    missing = [name for name in REQUIRED_VARS if os.getenv(name) is None]
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            "Check your .env file (see .env.example for reference)"
        )

    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# retrieves the company ID from the database (if it exists)
# creates a new company in the database if it doesn't exist
def get_or_create_company(company_name):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM companies WHERE name = %s", (company_name,))
    result = cursor.fetchone()
    if result:
        # needed to cast the result to a tuple
        # before acessing the first element of the result
        company_id = cast(tuple, result)[0]
    else:
        # creates the new company in the database, since it doesnt exist yet
        cursor.execute("INSERT INTO companies (name) VALUES (%s)", (company_name,))
        company_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return company_id