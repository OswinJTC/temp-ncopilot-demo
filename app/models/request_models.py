from pydantic import BaseModel
from typing import List, Optional

class QueryParams(BaseModel):
    interface_type: str
    lastName: Optional[str] = None
    firstName: Optional[str] = None
    variables: List[str]
    timeframe: Optional[int] = None
    sort_field: Optional[str] = None
    limit: Optional[int] = None

class RequestParams(BaseModel):
    queries: List[QueryParams]
