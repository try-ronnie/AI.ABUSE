# app/schemas/auth.py

"""
Pydantic schemas for Authentication
"""

from pydantic import BaseModel


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Token payload schema"""
    sub: str
    roles: list[str] = []


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str
