from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.config import utc_now
from app.database import get_db
from app.models import User, Session as SessionModel
from app.schemas import UserCreate, UserLogin, UserResponse, AuthResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SESSION_DURATION_HOURS = 24


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, response: Response, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username já existe.")

    password_hash = pwd_context.hash(user_data.password)
    user = User(username=user_data.username, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)

    session = SessionModel(
        user_id=user.id,
        expires_at=utc_now() + timedelta(hours=SESSION_DURATION_HOURS),
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    response.set_cookie(
        key="session_id",
        value=str(session.id),
        httponly=True,
        max_age=SESSION_DURATION_HOURS * 3600,
        samesite="lax",
    )

    return AuthResponse(
        message="Usuário registrado com sucesso!",
        user=UserResponse(
            id=str(user.id),
            username=user.username,
            created_at=user.created_at,
        ),
    )


@router.post("/login", response_model=AuthResponse)
def login(user_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user or not pwd_context.verify(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")

    session = SessionModel(
        user_id=user.id,
        expires_at=utc_now() + timedelta(hours=SESSION_DURATION_HOURS),
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    response.set_cookie(
        key="session_id",
        value=str(session.id),
        httponly=True,
        max_age=SESSION_DURATION_HOURS * 3600,
        samesite="lax",
    )

    return AuthResponse(
        message="Login realizado com sucesso!",
        user=UserResponse(
            id=str(user.id),
            username=user.username,
            created_at=user.created_at,
        ),
    )


@router.post("/logout")
def logout(
    response: Response,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.query(SessionModel).filter(SessionModel.user_id == user.id).delete()
    db.commit()

    response.delete_cookie(key="session_id")
    return {"message": "Logout realizado com sucesso!"}


@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    return UserResponse(
        id=str(user.id),
        username=user.username,
        created_at=user.created_at,
    )
