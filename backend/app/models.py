import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, JSON, TypeDecorator
from sqlalchemy.orm import relationship
from app.database import Base


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


class Game(Base):
    __tablename__ = "games"

    id = Column(UUIDString(), primary_key=True, default=uuid.uuid4)
    secret_code = Column(JSON, nullable=False)
    status = Column(String, nullable=False, default="in_progress")
    max_attempts = Column(Integer, nullable=False, default=10)
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
