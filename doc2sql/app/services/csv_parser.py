# CSV parser
# app/services/csv_parser.py

import pandas as pd

def parse_csv(file_path: str) -> pd.DataFrame:
    return pd.read_csv(file_path)
