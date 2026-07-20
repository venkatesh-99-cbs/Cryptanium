from datetime import datetime
from pydantic import BaseModel, ConfigDict


class RepositoryBase(BaseModel):
    name: str
    full_name: str
    default_branch: str = "main"
    language: str | None = None
    visibility: str = "public"
    clone_url: str | None = None


class RepositoryCreate(RepositoryBase):
    github_repo_id: str
    user_id: int | None = None


class RepositoryResponse(BaseModel):
    id: int | None = None
    github_repo_id: str | None = None
    name: str
    owner: str = ""
    full_name: str | None = None
    private: bool = False
    language: str | None = None
    default_branch: str = "main"
    visibility: str = "public"
    clone_url: str | None = None
    last_scan: datetime | None = None
    updated_at: datetime | str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class RepositorySyncResponse(BaseModel):
    synced_count: int
    repositories: list[RepositoryResponse]
