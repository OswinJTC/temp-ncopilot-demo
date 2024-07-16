from typing import List, Dict
from pydantic import BaseModel

class HeHeDbOutput(BaseModel):
    DbOutput: List[Dict[str, float]]  # Adjusted structure

class RequestBody(BaseModel):
    input_text: str
    dboutput: HeHeDbOutput
    link: str
