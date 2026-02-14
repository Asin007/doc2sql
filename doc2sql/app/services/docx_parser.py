# DOCX parser
# app/services/docx_parser.py

from docx import Document
import pandas as pd

def parse_docx(file_path: str) -> pd.DataFrame:
    doc = Document(file_path)

    tables = doc.tables

    if not tables:
        raise ValueError("No tables found in DOCX file")

    # For MVP: use first table
    table = tables[0]

    data = []
    for row in table.rows:
        data.append([cell.text.strip() for cell in row.cells])

    # First row as header
    headers = data[0]
    rows = data[1:]

    df = pd.DataFrame(rows, columns=headers)

    return df
