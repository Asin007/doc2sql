# app/routers/tables.py

from fastapi import APIRouter, Form, HTTPException
from sqlalchemy import text
from app.services.user_db import build_user_engine

router = APIRouter()


@router.post("/tables")
async def list_tables(
    db_host: str = Form(...),
    db_name: str = Form(...),
    db_user: str = Form(...),
    db_password: str = Form(...)
):

    try:
        engine = build_user_engine(
            db_host,
            db_name,
            db_user,
            db_password
        )

        query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public';
        """

        async with engine.begin() as conn:
            result = await conn.execute(text(query))
            tables = [row[0] for row in result.fetchall()]

        await engine.dispose()

        return {"tables": tables}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
