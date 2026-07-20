from pydantic import BaseModel, Field
from app.schemas.user import UserResponse


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = Field(default="bearer")
    user: UserResponse


class GitHubUserData(BaseModel):
    id: str
    username: str
    email: str | None = None
    avatar_url: str | None = None
    access_token: str | None = None


class LoginResponse(BaseModel):
    authorization_url: str
