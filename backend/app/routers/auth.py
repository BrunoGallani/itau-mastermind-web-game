from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, UserResponse, AuthResponse, UserStatsResponse
from app.dependencies import get_current_user
from app.services.auth_service import (
    register_user,
    authenticate_user,
    logout_user,
    get_user_stats,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_session_cookie(response: Response, session_id: UUID) -> None:
    response.set_cookie(
        key="session_id",
        value=str(session_id),
        httponly=settings.cookie_httponly,
        max_age=settings.session_duration_hours * 3600,
        samesite=settings.cookie_samesite,
    )


def _build_user_response(user: User) -> UserResponse:
    return UserResponse(id=str(user.id), username=user.username, created_at=user.created_at)


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, response: Response, db: Session = Depends(get_db)) -> AuthResponse:
    user, session = register_user(user_data.username, user_data.password, db)
    _set_session_cookie(response, session.id)
    return AuthResponse(message="Usuário registrado com sucesso!", user=_build_user_response(user))


@router.post("/login", response_model=AuthResponse)
def login(user_data: UserLogin, response: Response, db: Session = Depends(get_db)) -> AuthResponse:
    user, session = authenticate_user(user_data.username, user_data.password, db)
    _set_session_cookie(response, session.id)
    return AuthResponse(message="Login realizado com sucesso!", user=_build_user_response(user))


@router.post("/logout")
def logout(
    response: Response,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    logout_user(user, db)
    response.delete_cookie(key="session_id")
    return {"message": "Logout realizado com sucesso!"}


@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)) -> UserResponse:
    return _build_user_response(user)


@router.get("/me/stats", response_model=UserStatsResponse)
def get_me_stats(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserStatsResponse:
    stats = get_user_stats(user, db)
    return UserStatsResponse(
        username=user.username,
        total_games=stats.total_games,
        wins=stats.wins,
        losses=stats.losses,
        in_progress=stats.in_progress,
        abandoned=stats.abandoned,
        best_score=stats.best_score,
    )
