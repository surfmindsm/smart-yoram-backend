from typing import Optional
from pydantic import BaseModel
from app.schemas.user import User
from app.schemas.member import Member


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[int] = None


class TokenWithUser(Token):
    user: User
    member: Optional[Member] = None
