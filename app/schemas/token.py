from typing import Optional, Any
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[int] = None


class TokenWithUser(Token):
    user: Any
    member: Optional[Any] = None
