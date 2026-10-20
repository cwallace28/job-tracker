import os 
import mysql.connector
from dotenv import find_dotenv, load_dotenv


load_dotenv()

REQUIRED_VARS = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]

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
