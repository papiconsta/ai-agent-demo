# pip install psycopg2-binary
# Connection pattern source - https://stackoverflow.com/a/59860229
# Posted by Nikolay Baranenko
# Retrieved 2026-08-26, License - CC BY-SA 4.0

import os
from json import load
import sys
import time
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from pymilvus import MilvusClient, client, model

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "dbname": os.getenv("POSTGRES_DB", "llm_zoomcamp"),
    "user": os.getenv("POSTGRES_USER", "llm_user"),
    "password": os.getenv("POSTGRES_PASSWORD", "llm_password"),
}

SQL_FILES = [
    "2_create_users.sql",
    "3_create_chat_history.sql",
    "4_conversations.sql"
]

MILVUS_HOST = os.environ.get("MILVUS_HOST", "localhost")
MILVUS_PORT = os.environ.get("MILVUS_PORT", "19530")


def wait_for_db(retries: int = 10, delay: float = 2.0) -> None:
    for attempt in range(1, retries + 1):
        try:
            with psycopg2.connect(**DB_CONFIG) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
            print(f"Database is healthy ({DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']})")
            return
        except psycopg2.OperationalError as e:
            print(f"[{attempt}/{retries}] Database not ready yet: {e}")
            time.sleep(delay)
    print("Database did not become healthy in time.")
    sys.exit(1)


def run_sql_files() -> None:
    base_dir = Path(__file__).parent
    with psycopg2.connect(**DB_CONFIG) as connection:
        with connection.cursor() as cursor:
            for filename in SQL_FILES:
                sql_path = base_dir / filename
                print(f"Executing {filename}...")
                cursor.execute(sql_path.read_text())
        connection.commit()
    print("Schema is up to date.")

def vectormilvusdb() -> None:

    # This will download a small embedding model "paraphrase-albert-small-v2" (~50MB).
    embedding_fn = model.dense.SentenceTransformerEmbeddingFunction(model_name="intfloat/multilingual-e5-base")
    embedding_model_dimension = embedding_fn.dim

    DATA_PATH = Path(__file__).resolve().parents[2] / "data/data.json"


    def load_data():
        with open(DATA_PATH, encoding="utf-8") as f:
            return load(f)


    def record_to_text(record):
        fields = [record.get("name"), record.get("measurements"), record.get("type"), record.get("material")]
        return "passage: " + " ".join(str(f) for f in fields if f)

    client = MilvusClient(uri=f"http://{MILVUS_HOST}:{MILVUS_PORT}")

    if client.has_collection(collection_name="llm_zoomcamp_db"):
        client.drop_collection(collection_name="llm_zoomcamp_db")

    client.create_collection(
        collection_name="llm_zoomcamp_db",
        dimension=embedding_model_dimension,
    )

    data = load_data()
    docs = [record_to_text(data_piece) for data_piece in data]
    vectors = embedding_fn.encode_documents(docs)

    for data_piece, vector in zip(data, vectors):
        data_piece["vector"] = vector

    client.insert(collection_name="llm_zoomcamp_db", data=data)
    


if __name__ == "__main__":
    wait_for_db()
    run_sql_files()
    vectormilvusdb()
