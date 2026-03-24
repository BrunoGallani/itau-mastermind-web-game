from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from app.config import settings

connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def persist(db: Session, obj: Any) -> None:
    """Adiciona, salva e atualiza o objeto no banco."""
    db.add(obj)
    db.commit()
    db.refresh(obj)


def save(db: Session) -> None:
    """Salva as alterações pendentes no banco."""
    db.commit()


def save_and_refresh(db: Session, obj: Any) -> None:
    """Salva e atualiza o objeto no banco (sem add)."""
    db.commit()
    db.refresh(obj)
