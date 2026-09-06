import os

from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "dbname": os.getenv("POSTGRES_DB", "llm_zoomcamp"),
    "user": os.getenv("POSTGRES_USER", "llm_user"),
    "password": os.getenv("POSTGRES_PASSWORD", "llm_password"),
}
