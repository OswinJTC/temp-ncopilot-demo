from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    name: str
    password: str

class User(BaseModel):
    id: int
    email: str
    name: str

    class Config:
        orm_mode = True
