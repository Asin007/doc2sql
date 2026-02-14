# detect file type
# app/services/file_router.py

from app.services.csv_parser import parse_csv
from app.services.docx_parser import parse_docx
from app.services.pdf_parser import parse_pdf

def route_file(file_path: str, extension: str):

    extension = extension.lower()

    if extension == "csv":
        return parse_csv(file_path)

    elif extension == "pdf":
        return parse_pdf(file_path)

    elif extension == "docx":
        return parse_docx(file_path)

    else:
        raise ValueError(f"Unsupported file type: {extension}")
