# app/services/schema_infer.py

import pandas as pd
from app.utils.type_mapper import map_dtype


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and normalize dataframe before schema inference.
    """

    # Strip whitespace only on object columns
    object_cols = df.select_dtypes(include=["object"]).columns
    for col in object_cols:
        df[col] = df[col].str.strip()

    # Try numeric conversion
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except Exception:
            pass

    # Try datetime conversion only on object columns
    for col in df.select_dtypes(include=["object"]).columns:
        try:
            converted = pd.to_datetime(df[col], errors="coerce", infer_datetime_format=True)
            # Only convert if majority of values are valid dates
            if converted.notna().sum() > len(df) * 0.6:
                df[col] = converted
        except Exception:
            pass

    return df


def detect_foreign_keys(df: pd.DataFrame):
    """
    Detect potential foreign key columns using:
    - naming heuristic (_id)
    - integer type
    - cardinality ratio
    """

    potential_fks = []
    total_rows = len(df)

    for col in df.columns:

        if not col.lower().endswith("_id"):
            continue

        if not pd.api.types.is_integer_dtype(df[col]):
            continue

        unique_count = df[col].nunique(dropna=True)
        ratio = unique_count / total_rows if total_rows > 0 else 0

        # Better heuristic thresholds
        if 0 < ratio < 0.5:
            confidence = "high"
        elif 0.5 <= ratio < 0.8:
            confidence = "medium"
        else:
            continue

        potential_fks.append({
            "column": col,
            "unique_values": int(unique_count),
            "cardinality_ratio": round(ratio, 3),
            "confidence": confidence
        })

    return potential_fks


def infer_schema(df: pd.DataFrame):
    """
    Main schema inference entrypoint.
    Returns:
    - SQL schema mapping
    - cleaned dataframe
    - foreign key candidates
    """

    df = clean_dataframe(df)

    schema = {
        column: map_dtype(df[column].dtype)
        for column in df.columns
    }

    foreign_keys = detect_foreign_keys(df)

    return schema, df, foreign_keys

def build_schema_preview(df: pd.DataFrame):
    """
    Build detailed schema preview metadata for UI rendering.
    """

    preview_columns = []
    total_rows = len(df)

    for col in df.columns:
        series = df[col]

        null_count = int(series.isna().sum())
        unique_count = int(series.nunique(dropna=True))

        sample_values = (
            series.dropna()
            .astype(str)
            .head(3)
            .tolist()
        )

        preview_columns.append({
            "column_name": col,
            "sql_type": map_dtype(series.dtype),
            "nullable": null_count > 0,
            "null_count": null_count,
            "unique_count": unique_count,
            "cardinality_ratio": round(unique_count / total_rows, 3) if total_rows else 0,
            "sample_values": sample_values,
            "detected_primary_key": unique_count == total_rows and null_count == 0
        })

    return {
        "row_count": total_rows,
        "columns": preview_columns
    }
