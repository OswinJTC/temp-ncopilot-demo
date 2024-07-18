from typing import List, Dict, Union
from pydantic import BaseModel

class HeHeDbOutput(BaseModel):
    DbOutput: List[Dict[str, Union[str, float]]]

class RequestBody(BaseModel):
    input_text: str
    dboutput: HeHeDbOutput
    link: str
