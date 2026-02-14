# app/routers/ingest.py

import os
import logging

from fastapi import APIRouter, UploadFile, File, HTTPException, Form

from app.config import UPLOAD_DIR
from app.utils.validators import validate_file
from app.utils.table_namer import generate_table_name
from app.services.file_router import route_file
from app.services.schema_infer import infer_schema
from app.services.user_db import build_user_engine, validate_user_connection
from app.services.internal_db import log_internal_history
from app.models.response_models import IngestResponse

from sqlalchemy import text


router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_file(
    file: UploadFile = File(...),
    db_host: str = Form(...),
    db_name: str = Form(...),
    db_user: str = Form(...),
    db_password: str = Form(...)
):

    validate_file(file.filename)

    table_name = generate_table_name(file.filename)
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    user_engine = None

    try:
        # Save uploaded file
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Parse file
        extension = file.filename.split(".")[-1].lower()
        df = route_file(file_path, extension)

        # Infer schema
        schema, df, foreign_keys = infer_schema(df)

        # Build user DB engine dynamically
        user_engine = build_user_engine(
            db_host,
            db_name,
            db_user,
            db_password
        )
        is_valid = await validate_user_connection(user_engine)

        if not is_valid:
            await user_engine.dispose()
            raise HTTPException(
                status_code=400,
                detail="Invalid database credentials or unable to connect"
            )
                
        # Create table + insert into USER DB
        columns = ", ".join([f'"{col}" {dtype}' for col, dtype in schema.items()])
        create_query = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns});'

        async with user_engine.begin() as conn:
            await conn.execute(text(create_query))
            await conn.run_sync(
                lambda sync_conn: df.to_sql(
                    table_name,
                    sync_conn,
                    if_exists="append",
                    index=False
                )
            )

        # Log success internally
        await log_internal_history(
            file.filename,
            table_name,
            len(df),
            "success",
            db_host,
            None
        )

        logging.info(f"Ingested file successfully: {file.filename}")

        return IngestResponse(
            table_created=table_name,
            rows_inserted=len(df),
            columns=schema,
            potential_foreign_keys=foreign_keys
        )

    except Exception as e:

        logging.error(f"Ingestion failed: {str(e)}")

        await log_internal_history(
            file.filename,
            table_name,
            0,
            "failed",
            db_host,
            str(e)
        )

        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if user_engine:
            await user_engine.dispose()
