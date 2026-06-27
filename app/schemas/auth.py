from pydantic import BaseModel


class GoogleAuth(BaseModel):
    credential: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
