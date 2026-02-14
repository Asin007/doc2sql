# app/main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging

from app.routers import ingest, schema, tables, ui
from app.services.internal_db import initialize_metadata_table


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await initialize_metadata_table()
    yield
    # Shutdown (optional future cleanup)


app = FastAPI(
    title="Doc2SQL ETL API",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(ui.router)
app.include_router(ingest.router)
app.include_router(schema.router)
app.include_router(tables.router)


@app.get("/health")
def health():
    return {"status": "ok"}


logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
