from datetime import timedelta
from uuid import UUID

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import HTTPException

from app.config import utc_now, settings
from app.database import persist, save
from app.constants import AuthError
from app.models import User, Session as SessionModel, Game
from app.game_logic import GameStatus
from app.dto import UserStats

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def register_user(username: str, password: str, db: Session) -> tuple[User, SessionModel]:
    """Registra um novo usuário e cria uma sessão."""
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail=AuthError.USERNAME_EXISTS)

    password_hash = pwd_context.hash(password)
    user = User(username=username, password_hash=password_hash)
    persist(db, user)

    session = _create_session(user.id, db)
    return user, session


def authenticate_user(username: str, password: str, db: Session) -> tuple[User, SessionModel]:
    """Autentica um usuário e cria uma sessão."""
    user = db.query(User).filter(User.username == username).first()
    if not user or not pwd_context.verify(password, user.password_hash):
        raise HTTPException(status_code=401, detail=AuthError.INVALID_CREDENTIALS)

    session = _create_session(user.id, db)
    return user, session


def logout_user(user: User, db: Session) -> None:
    """Remove todas as sessões do usuário."""
    db.query(SessionModel).filter(SessionModel.user_id == user.id).delete()
    save(db)


def get_user_stats(user: User, db: Session) -> UserStats:
    """Retorna estatísticas do usuário: total de jogos, vitórias, melhor pontuação."""
    games = db.query(Game).filter(Game.user_id == user.id).all()

    wins = sum(1 for g in games if g.status == GameStatus.WON)
    losses = sum(1 for g in games if g.status == GameStatus.LOST)
    in_progress = sum(1 for g in games if g.status == GameStatus.IN_PROGRESS)
    abandoned = sum(1 for g in games if g.status == GameStatus.ABANDONED)

    best_score = None
    won_games = [g for g in games if g.status == GameStatus.WON and g.score is not None]
    if won_games:
        best_score = max(g.score for g in won_games)

    return UserStats(
        total_games=len(games),
        wins=wins,
        losses=losses,
        in_progress=in_progress,
        abandoned=abandoned,
        best_score=best_score,
    )


def _create_session(user_id: UUID, db: Session) -> SessionModel:
    """Cria uma nova sessão para o usuário."""
    session = SessionModel(
        user_id=user_id,
        expires_at=utc_now() + timedelta(hours=settings.session_duration_hours),
    )
    persist(db, session)
    return session
