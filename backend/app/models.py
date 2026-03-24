import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, JSON, DateTime, TypeDecorator
from sqlalchemy.orm import relationship
from app.config import utc_now
from app.database import Base
from app.game_logic import GameStatus


class UUIDString(TypeDecorator):
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return uuid.UUID(value)
        return value


class User(Base):
    __tablename__ = "users"

    id = Column(UUIDString(), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=utc_now)

    games = relationship("Game", back_populates="user")
    sessions = relationship("Session", back_populates="user")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUIDString(), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUIDString(), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=utc_now)
    expires_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="sessions")


class Game(Base):
    __tablename__ = "games"

    id = Column(UUIDString(), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUIDString(), ForeignKey("users.id"), nullable=False)
    secret_code = Column(JSON, nullable=False)
    status = Column(String, nullable=False, default=GameStatus.IN_PROGRESS)
    max_attempts = Column(Integer, nullable=False, default=10)
    started_at = Column(DateTime, default=utc_now)
    finished_at = Column(DateTime, nullable=True)
    score = Column(Integer, nullable=True)

    user = relationship("User", back_populates="games")
    guesses = relationship("Guess", back_populates="game", order_by="Guess.attempt_number")


class Guess(Base):
    __tablename__ = "guesses"

    id = Column(UUIDString(), primary_key=True, default=uuid.uuid4)
    game_id = Column(UUIDString(), ForeignKey("games.id"), nullable=False)
    attempt_number = Column(Integer, nullable=False)
    colors = Column(JSON, nullable=False)
    black_pegs = Column(Integer, nullable=False)
    white_pegs = Column(Integer, nullable=False)

    game = relationship("Game", back_populates="guesses")
