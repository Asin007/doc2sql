# app/routers/schema.py

import os
from fastapi import APIRouter, UploadFile, File, Form
from app.config import UPLOAD_DIR
from app.services.file_router import route_file
from app.utils.validators import validate_file
from app.services.schema_infer import infer_schema, build_schema_preview
from app.utils.table_namer import generate_table_name

router = APIRouter()


@router.post("/schema")
async def preview_schema(
    file: UploadFile = File(...),
    db_host: str = Form(...),
    db_name: str = Form(...),
    db_user: str = Form(...),
    db_password: str = Form(...)
):
    """
    Preview schema without inserting into user DB.
    DB credentials are accepted but not used here.
    """

    validate_file(file.filename)

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    extension = file.filename.split(".")[-1].lower()
    df = route_file(file_path, extension)

    schema, df, foreign_keys = infer_schema(df)
    preview = build_schema_preview(df)
    table_name = generate_table_name(file.filename)

    return {
        "suggested_table_name": table_name,
        "columns": schema,
        "row_count_preview": len(df),
        "potential_foreign_keys": foreign_keys
    }
