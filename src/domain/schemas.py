from pydantic import BaseModel


class AccessToken(BaseModel):
    access_token: str
    token_type: str = "Bearer"

class RefreshToken(BaseModel):
    refresh_token: str

class Tokens(AccessToken, RefreshToken):
    pass
