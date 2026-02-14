# app/services/internal_db.py

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.config import DATABASE_URL
import ssl


if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not configured")


# Strip any URL query params (e.g. ?sslmode=require) because asyncpg
# does not accept the `sslmode` keyword. Then convert to asyncpg URL.
ASYNC_DB_URL = DATABASE_URL.split("?")[0].replace(
    "postgresql://",
    "postgresql+asyncpg://"
)


# Create a proper SSLContext and pass it via connect_args as `ssl`.
# asyncpg expects `ssl` to be a boolean or an ssl.SSLContext — not
# the `sslmode` query string which causes the TypeError you saw.
ssl_context = ssl.create_default_context()

engine = create_async_engine(
    ASYNC_DB_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    connect_args={"ssl": ssl_context}
)


async def initialize_metadata_table():
    """
    Creates ingestion_history table inside INTERNAL database.
    """

    query = """
    CREATE TABLE IF NOT EXISTS ingestion_history (
        id SERIAL PRIMARY KEY,
        file_name TEXT,
        table_name TEXT,
        rows_inserted INTEGER,
        status TEXT,
        db_host TEXT,
        error_message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    async with engine.begin() as conn:
        await conn.execute(text(query))


async def log_internal_history(
    file_name,
    table_name,
    rows,
    status,
    db_host,
    error_message
):
    """
    Logs ingestion activity in internal metadata database.
    """

    query = text("""
        INSERT INTO ingestion_history 
        (file_name, table_name, rows_inserted, status, db_host, error_message)
        VALUES (:file_name, :table_name, :rows, :status, :db_host, :error_message)
    """)

    try:
        async with engine.begin() as conn:
            await conn.execute(query, {
                "file_name": file_name,
                "table_name": table_name,
                "rows": rows,
                "status": status,
                "db_host": db_host,
                "error_message": error_message
            })
    except Exception:
        # Do not crash main ingestion if logging fails
        pass
