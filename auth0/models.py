from typing import List, Dict
from pydantic import BaseModel

class TokenData(BaseModel):
    sub: str
    permissions: List[str] = []
    roles: List[str] = []
    app_metadata: Dict[str, str] = {}

