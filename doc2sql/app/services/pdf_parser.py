# app/services/pdf_parser.py

import pdfplumber
import pandas as pd


def parse_pdf(file_path: str) -> pd.DataFrame:
    """
    Parses structured (text-based) PDFs only.
    OCR is disabled in deploy-lite version.
    """

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()

            if tables:
                table = tables[0]
                headers = table[0]
                rows = table[1:]
                return pd.DataFrame(rows, columns=headers)

    raise ValueError(
        "No extractable tables found. "
        "Scanned PDFs (image-based) are not supported in deploy-lite version."
    )
