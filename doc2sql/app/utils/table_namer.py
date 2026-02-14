import re
from datetime import datetime


def generate_table_name(filename: str) -> str:
    """
    Generate safe SQL table name from filename.
    """

    base = filename.split(".")[0]

    base = re.sub(r"[^a-zA-Z0-9_]", "_", base)
    base = base.lower()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    return f"{base}_{timestamp}"


def normalize_columns(columns):
    """
    Clean and normalize column names.
    """

    cleaned = []
    seen = {}

    for col in columns:
        col = col.strip().lower()
        col = re.sub(r'\s+', '_', col)
        col = re.sub(r'[^a-z0-9_]', '', col)

        if col in seen:
            seen[col] += 1
            col = f"{col}_{seen[col]}"
        else:
            seen[col] = 0

        cleaned.append(col)

    return cleaned
