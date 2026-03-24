from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import (
    GuessCreate,
    GameCreateResponse,
    GameStateResponse,
    GameSummaryResponse,
    GuessSubmitResponse,
    GuessResponse,
    FeedbackResponse,
    RankingEntryResponse,
    AbandonResponse,
)
from app.dependencies import get_current_user
from app.game_logic import GameStatus
from app.services.game_service import (
    create_game,
    submit_guess,
    abandon_game,
    get_game_state,
    get_user_games,
    get_ranking,
    calculate_duration,
)

router = APIRouter(prefix="/games", tags=["games"])


@router.post("/", response_model=GameCreateResponse, status_code=status.HTTP_201_CREATED)
def create_game_endpoint(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    game = create_game(user, db)
    return GameCreateResponse(
        game_id=str(game.id),
        message="Jogo criado! Você tem 10 tentativas. Boa sorte!",
    )


@router.post(
    "/{game_id}/guesses",
    response_model=GuessSubmitResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_guess_endpoint(
    game_id: UUID,
    guess_data: GuessCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = submit_guess(game_id, guess_data.colors, user, db)
    return GuessSubmitResponse(
        attempt_number=result["attempt_number"],
        feedback=FeedbackResponse(**result["feedback"]),
        status=result["status"],
        attempts_left=result["attempts_left"],
        score=result["score"],
        secret_code=result["secret_code"],
    )


@router.get("/ranking/", response_model=list[RankingEntryResponse])
def get_ranking_endpoint(db: Session = Depends(get_db)):
    ranking = get_ranking(db)
    return [RankingEntryResponse(**entry) for entry in ranking]


@router.get("/my-games/", response_model=list[GameSummaryResponse])
def get_my_games(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    games = get_user_games(user, db)
    return [
        GameSummaryResponse(
            game_id=str(game.id),
            status=game.status,
            attempts_used=len(game.guesses),
            max_attempts=game.max_attempts,
            score=game.score,
            started_at=game.started_at,
            finished_at=game.finished_at,
            duration_seconds=calculate_duration(game),
        )
        for game in games
    ]


@router.post("/{game_id}/abandon", response_model=AbandonResponse)
def abandon_game_endpoint(
    game_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    game = abandon_game(game_id, user, db)
    return AbandonResponse(
        game_id=str(game.id),
        status=game.status,
        message="Jogo abandonado.",
        duration_seconds=calculate_duration(game),
        secret_code=game.secret_code,
    )


@router.get("/{game_id}", response_model=GameStateResponse)
def get_game_state_endpoint(
    game_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    game = get_game_state(game_id, user, db)

    guesses = [
        GuessResponse(
            attempt_number=g.attempt_number,
            colors=g.colors,
            feedback=FeedbackResponse(black_pegs=g.black_pegs, white_pegs=g.white_pegs),
        )
        for g in game.guesses
    ]

    secret_code_to_reveal = None
    if game.status != GameStatus.IN_PROGRESS:
        secret_code_to_reveal = game.secret_code

    return GameStateResponse(
        game_id=str(game.id),
        status=game.status,
        attempts_left=game.max_attempts - len(game.guesses),
        max_attempts=game.max_attempts,
        started_at=game.started_at,
        finished_at=game.finished_at,
        duration_seconds=calculate_duration(game),
        score=game.score,
        guesses=guesses,
        secret_code=secret_code_to_reveal,
    )
