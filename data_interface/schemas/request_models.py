# app/models/request_models.py
from pydantic import BaseModel
from typing import Dict, List, Optional

class Conditions(BaseModel):
    duration: Optional[int] = None
    sortby: Optional[Dict[str, str]] = None
    limit: Optional[int] = None

class QueryParams(BaseModel):
    interface_type: str
    patientName: str
    retrieve: List[str]
    conditions: Optional[Conditions] = None

class RequestParams(BaseModel):
    queries: List[QueryParams]