# Validators for input data
# app/utils/validators.py

from fastapi import HTTPException

ALLOWED_EXTENSIONS = ["csv", "docx", "pdf"]

def validate_file(filename: str):
    if "." not in filename:
        raise HTTPException(status_code=400, detail="Invalid file name")

    ext = filename.split(".")[-1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {ALLOWED_EXTENSIONS}"
        )
