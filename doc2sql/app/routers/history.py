# app/routers/history.py

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy import text
from app.services.internal_db import engine

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/history", response_class=HTMLResponse)
async def get_ingestion_history(request: Request):

    query = text("""
        SELECT file_name, table_name, rows_inserted, status, foreign_keys, created_at
        FROM ingestion_history
        ORDER BY created_at DESC
    """)

    async with engine.begin() as conn:
        result = await conn.execute(query)
        rows = result.mappings().all()

    return templates.TemplateResponse(
        "history.html",
        {
            "request": request,
            "history": rows
        }
    )
