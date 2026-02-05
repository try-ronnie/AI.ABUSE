# app/schemas/auth.py

from pydantic import BaseModel


class TokenRead(BaseModel):
    access_token: str
    refresh_token: str
