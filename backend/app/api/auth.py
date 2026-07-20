from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.config import settings
from app.core.oauth_state import consume_state, create_state
from app.core.security import create_access_token
from app.database.database import get_db
from app.database.models import User
from app.schemas.auth import TokenResponse
from app.schemas.user import UserResponse
from app.services.github.oauth import GitHubOAuthError, GitHubOAuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_github_oauth_service() -> GitHubOAuthService:
    return GitHubOAuthService()


@router.get("/login", summary="Initiate GitHub OAuth login flow")
async def login(
    state: str | None = Query(None, description="Optional security state parameter"),
    oauth_service: GitHubOAuthService = Depends(get_github_oauth_service),
):
    """Redirects client to GitHub OAuth authorization endpoint."""
    try:
        auth_url = oauth_service.get_authorization_url(state=state or create_state())
        return RedirectResponse(url=auth_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    except GitHubOAuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.get(
    "/callback",
    response_model=None,
    summary="GitHub OAuth callback endpoint",
)
async def callback(
    request: Request,
    code: str | None = Query(None, description="Authorization code from GitHub"),
    state: str | None = Query(None, description="Returned state parameter"),
    error: str | None = Query(None, description="OAuth error parameter"),
    error_description: str | None = Query(None, description="OAuth error description"),
    db: Session = Depends(get_db),
    oauth_service: GitHubOAuthService = Depends(get_github_oauth_service),
):
    """Exchanges authorization code, retrieves GitHub user profile, upserts User in DB, and returns JWT token."""
    if error:
        detail_msg = error_description or error or "OAuth authorization failed"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail_msg)

    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code parameter 'code' is required.",
        )

    try:
        github_token = await oauth_service.exchange_code_for_token(code)
        github_user = await oauth_service.fetch_user_profile(github_token)
    except GitHubOAuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    db_user = db.query(User).filter(User.github_id == github_user.id).first()
    if db_user:
        db_user.username = github_user.username
        db_user.email = github_user.email
        db_user.avatar_url = github_user.avatar_url
        db_user.access_token = github_token
    else:
        db_user = User(
            github_id=github_user.id,
            username=github_user.username,
            email=github_user.email,
            avatar_url=github_user.avatar_url,
            access_token=github_token,
        )
        db.add(db_user)

    db.commit()
    db.refresh(db_user)

    jwt_payload = {
        "sub": str(db_user.id),
        "github_id": db_user.github_id,
        "username": db_user.username,
    }
    jwt_token = create_access_token(data=jwt_payload)

    response = TokenResponse(
        access_token=jwt_token,
        token_type="bearer",
        user=UserResponse.model_validate(db_user),
    )
    if "text/html" in request.headers.get("accept", ""):
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL.rstrip('/')}/login#access_token={jwt_token}",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    if not consume_state(state):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OAuth state. Please restart GitHub login.",
        )
    return response


@router.post("/logout", summary="Logout authenticated user")
def logout(current_user: User = Depends(get_current_user)):
    """Invalidate local user session."""
    return {"message": f"Successfully logged out user {current_user.username}"}


@router.get("/me", response_model=UserResponse, summary="Get current authenticated user details")
def get_me(current_user: User = Depends(get_current_user)):
    """Return profile info of currently authenticated user."""
    return UserResponse.model_validate(current_user)


@router.post("/refresh", response_model=TokenResponse, summary="Refresh session token")
def refresh_token(current_user: User = Depends(get_current_user)):
    """Issue a fresh JWT access token for current user."""
    jwt_payload = {
        "sub": str(current_user.id),
        "github_id": current_user.github_id,
        "username": current_user.username,
    }
    new_jwt = create_access_token(data=jwt_payload)

    return TokenResponse(
        access_token=new_jwt,
        token_type="bearer",
        user=UserResponse.model_validate(current_user),
    )
