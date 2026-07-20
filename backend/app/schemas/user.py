from datetime import datetime
from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    github_id: str
    username: str
    email: str | None = None
    avatar_url: str | None = None


class UserCreate(UserBase):
    access_token: str | None = None


class UserResponse(UserBase):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    email: str | None = None
    avatar_url: str | None = None
