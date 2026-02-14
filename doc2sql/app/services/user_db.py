# app/services/user_db.py

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from urllib.parse import quote_plus


def build_user_engine(host: str, db: str, user: str, password: str):
    """
    Dynamically builds async SQLAlchemy engine for USER database.
    Supports Neon / SSL-required Postgres.
    """

    # 🔹 Clean host input
    host = host.strip()
    host = host.replace("https://", "").replace("http://", "")

    # 🔹 Remove any accidental query params pasted by user
    if "?" in host:
        host = host.split("?")[0]

    # 🔹 Add default port if missing
    if ":" not in host:
        host = f"{host}:5432"

    # 🔹 Encode password safely (handles @, :, etc.)
    safe_password = quote_plus(password)

    db_url = f"postgresql+asyncpg://{user}:{safe_password}@{host}/{db}"

    engine = create_async_engine(
        db_url,
        echo=False,
        pool_size=3,
        max_overflow=5,
        pool_pre_ping=True,
        connect_args={"ssl": "require"}  # ✅ REQUIRED for Neon
    )

    return engine


async def validate_user_connection(engine):
    """
    Validates that user DB credentials are correct.
    """

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True

    except SQLAlchemyError:
        return False
