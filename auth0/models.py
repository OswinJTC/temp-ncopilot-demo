from typing import List
from pydantic import BaseModel

class TokenData(BaseModel):
    sub: str
    permissions: List[str] = []
    roles: List[str] = []
