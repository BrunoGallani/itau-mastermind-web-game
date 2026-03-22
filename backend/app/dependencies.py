from fastapi import Depends, HTTPException, Cookie
from sqlalchemy.orm import Session
from app.config import utc_now
from app.database import get_db
from app.models import User, Session as SessionModel


def get_current_user(
    session_id: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not session_id:
        raise HTTPException(status_code=401, detail="Não autenticado.")

    session = (
        db.query(SessionModel)
        .filter(SessionModel.id == session_id)
        .filter(SessionModel.expires_at > utc_now())
        .first()
    )

    if not session:
        raise HTTPException(status_code=401, detail="Sessão inválida ou expirada.")

    return session.user


def get_optional_user(
    session_id: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User | None:
    if not session_id:
        return None

    session = (
        db.query(SessionModel)
        .filter(SessionModel.id == session_id)
        .filter(SessionModel.expires_at > utc_now())
        .first()
    )

    if not session:
        return None

    return session.user
