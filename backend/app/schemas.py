from datetime import datetime
from pydantic import BaseModel, field_validator
from app.game_logic import VALID_COLORS, CODE_LENGTH


# Auth Schemas
class UserCreate(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError("Username deve ter entre 3 e 50 caracteres.")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Senha deve ter pelo menos 6 caracteres.")
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    created_at: datetime
    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    message: str
    user: UserResponse


class UserStatsResponse(BaseModel):
    username: str
    total_games: int
    wins: int
    losses: int
    in_progress: int
    best_score: int | None = None


# Game Schemas
class GuessCreate(BaseModel):
    colors: list[str]

    @field_validator("colors")
    @classmethod
    def validate_colors(cls, v):
        if len(v) != CODE_LENGTH:
            raise ValueError(f"A tentativa deve conter exatamente {CODE_LENGTH} cores.")
        for color in v:
            if color not in VALID_COLORS:
                raise ValueError(f"Cor inválida: '{color}'. Cores válidas: {VALID_COLORS}")
        return v


class FeedbackResponse(BaseModel):
    black_pegs: int
    white_pegs: int


class GuessResponse(BaseModel):
    attempt_number: int
    colors: list[str]
    feedback: FeedbackResponse
    model_config = {"from_attributes": True}


class GameCreateResponse(BaseModel):
    game_id: str
    message: str


class GameStateResponse(BaseModel):
    game_id: str
    status: str
    attempts_left: int
    max_attempts: int
    started_at: datetime
    finished_at: datetime | None = None
    duration_seconds: int | None = None
    score: int | None = None
    guesses: list[GuessResponse]
    secret_code: list[str] | None = None


class GuessSubmitResponse(BaseModel):
    attempt_number: int
    feedback: FeedbackResponse
    status: str
    attempts_left: int
    score: int | None = None
    secret_code: list[str] | None = None


class GameSummaryResponse(BaseModel):
    game_id: str
    status: str
    attempts_used: int
    max_attempts: int
    score: int | None = None
    started_at: datetime
    finished_at: datetime | None = None
    duration_seconds: int | None = None


class RankingEntryResponse(BaseModel):
    game_id: str
    username: str
    status: str
    attempts_used: int
    max_attempts: int
    score: int | None = None
    duration_seconds: int | None = None
