from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Game, Guess, User
from app.schemas import (
    GuessCreate,
    GameCreateResponse,
    GameStateResponse,
    GuessSubmitResponse,
    GuessResponse,
    FeedbackResponse,
    RankingEntryResponse,
)
from app.game_logic import generate_secret_code, evaluate_guess, calculate_score, MAX_ATTEMPTS
from app.dependencies import get_current_user

router = APIRouter(prefix="/games", tags=["games"])


@router.post("/", response_model=GameCreateResponse, status_code=status.HTTP_201_CREATED)
def create_game(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    secret = generate_secret_code()
    game = Game(
        user_id=user.id,
        secret_code=secret,
        status="in_progress",
        max_attempts=MAX_ATTEMPTS,
    )
    db.add(game)
    db.commit()
    db.refresh(game)
    return GameCreateResponse(
        game_id=str(game.id),
        message="Jogo criado! Você tem 10 tentativas. Boa sorte!",
    )


@router.post(
    "/{game_id}/guesses",
    response_model=GuessSubmitResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_guess(
    game_id: UUID,
    guess_data: GuessCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    game = db.query(Game).filter(Game.id == game_id, Game.user_id == user.id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Jogo não encontrado.")

    if game.status != "in_progress":
        raise HTTPException(
            status_code=400,
            detail=f"O jogo já terminou com status: {game.status}.",
        )

    current_attempt = len(game.guesses) + 1
    feedback = evaluate_guess(game.secret_code, guess_data.colors)

    guess = Guess(
        game_id=game.id,
        attempt_number=current_attempt,
        colors=guess_data.colors,
        black_pegs=feedback["black_pegs"],
        white_pegs=feedback["white_pegs"],
    )
    db.add(guess)

    secret_code_to_reveal = None
    score = None

    if feedback["black_pegs"] == 4:
        game.status = "won"
        game.finished_at = datetime.utcnow()
        duration = int((game.finished_at - game.started_at).total_seconds())
        game.score = calculate_score(current_attempt, duration)
        score = game.score
        secret_code_to_reveal = game.secret_code
    elif current_attempt >= game.max_attempts:
        game.status = "lost"
        game.finished_at = datetime.utcnow()
        game.score = 0
        score = 0
        secret_code_to_reveal = game.secret_code

    db.commit()

    return GuessSubmitResponse(
        attempt_number=current_attempt,
        feedback=FeedbackResponse(**feedback),
        status=game.status,
        attempts_left=game.max_attempts - current_attempt,
        score=score,
        secret_code=secret_code_to_reveal,
    )


@router.get("/ranking/", response_model=list[RankingEntryResponse])
def get_ranking(db: Session = Depends(get_db)):
    attempts_subq = (
        db.query(
            Guess.game_id,
            func.count(Guess.id).label("attempts_used"),
        )
        .group_by(Guess.game_id)
        .subquery()
    )

    results = (
        db.query(Game, User.username, attempts_subq.c.attempts_used)
        .join(User, Game.user_id == User.id)
        .outerjoin(attempts_subq, Game.id == attempts_subq.c.game_id)
        .filter(Game.status.in_(["won", "lost"]))
        .order_by(Game.score.desc().nullslast(), attempts_subq.c.attempts_used.asc())
        .all()
    )

    ranking = []
    for game, username, attempts_used in results:
        duration = None
        if game.finished_at and game.started_at:
            duration = int((game.finished_at - game.started_at).total_seconds())
        ranking.append(
            RankingEntryResponse(
                game_id=str(game.id),
                username=username,
                status=game.status,
                attempts_used=attempts_used or 0,
                max_attempts=game.max_attempts,
                score=game.score,
                duration_seconds=duration,
            )
        )
    return ranking


@router.get("/{game_id}", response_model=GameStateResponse)
def get_game_state(
    game_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    game = db.query(Game).filter(Game.id == game_id, Game.user_id == user.id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Jogo não encontrado.")

    guesses = [
        GuessResponse(
            attempt_number=g.attempt_number,
            colors=g.colors,
            feedback=FeedbackResponse(black_pegs=g.black_pegs, white_pegs=g.white_pegs),
        )
        for g in game.guesses
    ]

    secret_code_to_reveal = None
    if game.status != "in_progress":
        secret_code_to_reveal = game.secret_code

    duration = None
    if game.finished_at and game.started_at:
        duration = int((game.finished_at - game.started_at).total_seconds())
    elif game.started_at:
        duration = int((datetime.utcnow() - game.started_at).total_seconds())

    return GameStateResponse(
        game_id=str(game.id),
        status=game.status,
        attempts_left=game.max_attempts - len(game.guesses),
        max_attempts=game.max_attempts,
        started_at=game.started_at,
        finished_at=game.finished_at,
        duration_seconds=duration,
        score=game.score,
        guesses=guesses,
        secret_code=secret_code_to_reveal,
    )
