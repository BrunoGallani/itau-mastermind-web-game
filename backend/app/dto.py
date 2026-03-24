"""Objetos de transferencia entre camadas (service -> router)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Feedback:
    black_pegs: int
    white_pegs: int


@dataclass(frozen=True)
class GuessResult:
    attempt_number: int
    feedback: Feedback
    status: str
    attempts_left: int
    score: int | None
    secret_code: list[str] | None


@dataclass(frozen=True)
class UserStats:
    total_games: int
    wins: int
    losses: int
    in_progress: int
    abandoned: int
    best_score: int | None


@dataclass(frozen=True)
class RankingEntry:
    game_id: str
    username: str
    status: str
    attempts_used: int
    max_attempts: int
    score: int | None
    duration_seconds: int | None
