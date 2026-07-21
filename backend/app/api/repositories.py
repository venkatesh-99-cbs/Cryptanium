from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.database.models import User
from app.schemas.repository import RepositoryResponse, RepositorySyncResponse
from app.schemas.scan import ScanResponse
from app.services.github.repositories import GitHubRepositoryError, GitHubRepositoryService
from app.services.github.repository_service import RepositoryService
from app.services.scan_service import ScanService

router = APIRouter(prefix="/repositories", tags=["Repositories"])


def get_repository_service() -> RepositoryService:
    return RepositoryService()


def get_scan_service() -> ScanService:
    return ScanService()


def extract_optional_token(
    authorization: str | None = Header(None, alias="Authorization"),
    x_github_token: str | None = Header(None, alias="x-github-token"),
) -> str | None:
    token: str | None = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    elif x_github_token:
        token = x_github_token.strip()
    elif authorization:
        token = authorization.strip()
    return token


@router.get(
    "",
    response_model=list[RepositoryResponse],
    summary="List repositories belonging to user",
)
async def list_repositories(
    authorization: str | None = Header(None, alias="Authorization"),
    x_github_token: str | None = Header(None, alias="x-github-token"),
    db: Session = Depends(get_db),
    repo_service: RepositoryService = Depends(get_repository_service),
):
    """Retrieve all repositories belonging to the authenticated user or stored in system."""
    raw_token = extract_optional_token(authorization, x_github_token)

    # The frontend sends the Cryptanium JWT. Never forward that JWT to GitHub;
    # resolve the user's stored GitHub access token first.
    if authorization and authorization.lower().startswith("bearer ") and not x_github_token:
        try:
            current_user = get_current_user(
                credentials=HTTPAuthorizationCredentials(
                    scheme="Bearer", credentials=authorization[7:].strip()
                ),
                db=db,
            )
            raw_token = current_user.access_token
        except Exception:
            raw_token = None

    if raw_token:
        gh_service = GitHubRepositoryService()
        try:
            return await gh_service.fetch_user_repositories(access_token=raw_token)
        except GitHubRepositoryError as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.message)

    db_repos = repo_service.list_repositories(db=db)
    if not db_repos and not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="GitHub access token is required.",
        )

    return db_repos


@router.get(
    "/{id}",
    response_model=RepositoryResponse,
    summary="Get repository details by ID",
)
def get_repository_by_id(
    id: int,
    db: Session = Depends(get_db),
    repo_service: RepositoryService = Depends(get_repository_service),
):
    """Fetch details for a specific repository by its database ID."""
    return repo_service.get_repository_by_id(db=db, repo_id=id)


@router.post(
    "",
    response_model=RepositoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a repository for scanning",
)
def add_repository(
    repository: RepositoryResponse,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    repo_service: RepositoryService = Depends(get_repository_service),
):
    """Persist a repository entry for later scanning and reporting."""
    return repo_service.add_repository(db=db, user=current_user, repository=repository)


@router.post(
    "/sync",
    response_model=RepositorySyncResponse,
    summary="Synchronize GitHub repositories",
)
async def sync_repositories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    repo_service: RepositoryService = Depends(get_repository_service),
):
    """Fetch user repositories from GitHub REST API and sync into the database."""
    return await repo_service.sync_user_repositories(db=db, user=current_user)


@router.post(
    "/{id}/scan",
    response_model=ScanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a scan job for repository",
)
def create_repository_scan_job(
    id: int,
    db: Session = Depends(get_db),
    scan_service: ScanService = Depends(get_scan_service),
):
    """Create a new security scan job for the target repository."""
    return scan_service.create_scan_job(db=db, repository_id=id)


@router.delete(
    "/{id}",
    summary="Remove a repository",
)
def delete_repository(
    id: int,
    db: Session = Depends(get_db),
    repo_service: RepositoryService = Depends(get_repository_service),
):
    """Remove repository entry from system."""
    repo_service.delete_repository(db=db, repo_id=id)
    return {"success": True, "message": f"Repository {id} successfully deleted."}
