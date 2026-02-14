from pydantic import BaseModel
from typing import Dict, List


class IngestResponse(BaseModel):
    table_created: str
    rows_inserted: int
    columns: Dict[str, str]
    potential_foreign_keys: List[dict]
