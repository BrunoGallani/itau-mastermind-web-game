from pydantic import BaseModel, field_validator
from app.game_logic import VALID_COLORS, CODE_LENGTH


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
    guesses: list[GuessResponse]
    secret_code: list[str] | None = None


class GuessSubmitResponse(BaseModel):
    attempt_number: int
    feedback: FeedbackResponse
    status: str
    attempts_left: int
    secret_code: list[str] | None = None


class RankingEntryResponse(BaseModel):
    game_id: str
    status: str
    attempts_used: int
    max_attempts: int
