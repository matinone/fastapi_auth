from pydantic import BaseModel


class Token(BaseModel):
    token_type: str
    access_token: str
    refresh_token: str | None = None


class TokenPayload(BaseModel):
    sub: str | None = None


class RefreshToken(BaseModel):
    grant_type: str
    token: str
