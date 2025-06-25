# drafts/schemas.py
from pydantic import BaseModel


class DraftCreate(BaseModel):
    name: str
    date: str
    url: str
    user_token: str


class DraftResponse(BaseModel):
    name: str
    date: str
    url: str

    class Config:
        orm_mode = True
