from sqlalchemy.orm import Session

from app.database.models import Repository, User
from app.schemas.repository import RepositoryResponse, RepositorySyncResponse
from app.services.github.github_client import GitHubClient, GitHubClientError
from app.utils.exceptions import NotFoundException, ValidationException


class RepositoryService:
    """Service handling repository synchronisation, retrieval, and management."""

    def __init__(self, github_client: GitHubClient | None = None):
        self.github_client = github_client or GitHubClient()

    def list_repositories(
        self, db: Session, user_id: int | None = None
    ) -> list[RepositoryResponse]:
        """Fetch all repositories belonging to a user or all repositories in DB."""
        query = db.query(Repository)
        if user_id:
            query = query.filter(Repository.user_id == user_id)
        db_repos = query.order_by(Repository.updated_at.desc()).all()

        results = []
        for r in db_repos:
            owner_name = r.user.username if r.user else (r.full_name.split("/")[0] if "/" in r.full_name else "")
            results.append(
                RepositoryResponse(
                    id=r.id,
                    github_repo_id=r.github_repo_id,
                    name=r.name,
                    owner=owner_name,
                    full_name=r.full_name,
                    private=(r.visibility.lower() == "private"),
                    language=r.language,
                    default_branch=r.default_branch,
                    visibility=r.visibility,
                    clone_url=r.clone_url,
                    last_scan=r.last_scan,
                    updated_at=r.updated_at,
                    created_at=r.created_at,
                )
            )
        return results

    def get_repository_by_id(self, db: Session, repo_id: int) -> RepositoryResponse:
        """Fetch repository details by primary key ID."""
        r = db.query(Repository).filter(Repository.id == repo_id).first()
        if not r:
            raise NotFoundException(f"Repository with ID {repo_id} not found.")

        owner_name = r.user.username if r.user else (r.full_name.split("/")[0] if "/" in r.full_name else "")
        return RepositoryResponse(
            id=r.id,
            github_repo_id=r.github_repo_id,
            name=r.name,
            owner=owner_name,
            full_name=r.full_name,
            private=(r.visibility.lower() == "private"),
            language=r.language,
            default_branch=r.default_branch,
            visibility=r.visibility,
            clone_url=r.clone_url,
            last_scan=r.last_scan,
            updated_at=r.updated_at,
            created_at=r.created_at,
        )

    async def sync_user_repositories(
        self, db: Session, user: User
    ) -> RepositorySyncResponse:
        """Synchronize user repositories from GitHub REST API into the database."""
        if not user.access_token:
            raise ValidationException("User does not have an active GitHub access token.")

        try:
            github_repos = await self.github_client.get_user_repositories(user.access_token)
        except GitHubClientError as exc:
            raise ValidationException(exc.message)

        synced_repos: list[RepositoryResponse] = []

        for repo_data in github_repos:
            gh_id = str(repo_data["id"])
            full_name = repo_data.get("full_name", repo_data.get("name", ""))
            name = repo_data.get("name", "")
            is_private = bool(repo_data.get("private", False))
            visibility = "private" if is_private else "public"

            db_repo = db.query(Repository).filter(Repository.github_repo_id == gh_id).first()
            if db_repo:
                db_repo.user_id = user.id
                db_repo.name = name
                db_repo.full_name = full_name
                db_repo.default_branch = repo_data.get("default_branch", "main")
                db_repo.language = repo_data.get("language")
                db_repo.visibility = visibility
                db_repo.clone_url = repo_data.get("clone_url")
            else:
                db_repo = Repository(
                    github_repo_id=gh_id,
                    user_id=user.id,
                    name=name,
                    full_name=full_name,
                    default_branch=repo_data.get("default_branch", "main"),
                    language=repo_data.get("language"),
                    visibility=visibility,
                    clone_url=repo_data.get("clone_url"),
                )
                db.add(db_repo)

            db.commit()
            db.refresh(db_repo)

            synced_repos.append(
                RepositoryResponse(
                    id=db_repo.id,
                    github_repo_id=db_repo.github_repo_id,
                    name=db_repo.name,
                    owner=user.username,
                    full_name=db_repo.full_name,
                    private=is_private,
                    language=db_repo.language,
                    default_branch=db_repo.default_branch,
                    visibility=db_repo.visibility,
                    clone_url=db_repo.clone_url,
                    last_scan=db_repo.last_scan,
                    updated_at=db_repo.updated_at,
                    created_at=db_repo.created_at,
                )
            )

        return RepositorySyncResponse(
            synced_count=len(synced_repos),
            repositories=synced_repos,
        )

    def delete_repository(
        self, db: Session, repo_id: int, user_id: int | None = None
    ) -> bool:
        """Remove a repository from the database."""
        query = db.query(Repository).filter(Repository.id == repo_id)
        if user_id:
            query = query.filter(Repository.user_id == user_id)
        repo = query.first()

        if not repo:
            raise NotFoundException(f"Repository with ID {repo_id} not found.")

        db.delete(repo)
        db.commit()
        return True
