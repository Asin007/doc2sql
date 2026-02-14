# PDF parser
# app/services/pdf_parser.py

import pdfplumber
import pandas as pd
from app.services.ocr_parser import parse_scanned_pdf


def parse_pdf(file_path: str) -> pd.DataFrame:

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            if tables:
                # Use first detected table
                table = tables[0]
                headers = table[0]
                rows = table[1:]
                return pd.DataFrame(rows, columns=headers)
            if not tables:
                return parse_scanned_pdf(file_path)


    raise ValueError("No tables found in PDF")
