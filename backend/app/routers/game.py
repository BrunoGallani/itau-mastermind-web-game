from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Game, Guess
from app.schemas import (
    GuessCreate,
    GameCreateResponse,
    GameStateResponse,
    GuessSubmitResponse,
    GuessResponse,
    FeedbackResponse,
    RankingEntryResponse,
)
from app.game_logic import generate_secret_code, evaluate_guess, MAX_ATTEMPTS

router = APIRouter(prefix="/games", tags=["games"])


@router.post("/", response_model=GameCreateResponse, status_code=status.HTTP_201_CREATED)
def create_game(db: Session = Depends(get_db)):
    secret = generate_secret_code()
    game = Game(secret_code=secret, status="in_progress", max_attempts=MAX_ATTEMPTS)
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
def submit_guess(game_id: UUID, guess_data: GuessCreate, db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.id == game_id).first()
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
    if feedback["black_pegs"] == 4:
        game.status = "won"
        secret_code_to_reveal = game.secret_code
    elif current_attempt >= game.max_attempts:
        game.status = "lost"
        secret_code_to_reveal = game.secret_code

    db.commit()

    return GuessSubmitResponse(
        attempt_number=current_attempt,
        feedback=FeedbackResponse(**feedback),
        status=game.status,
        attempts_left=game.max_attempts - current_attempt,
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
        db.query(Game, attempts_subq.c.attempts_used)
        .outerjoin(attempts_subq, Game.id == attempts_subq.c.game_id)
        .filter(Game.status.in_(["won", "lost"]))
        .order_by(Game.status.desc(), attempts_subq.c.attempts_used.asc())
        .all()
    )

    return [
        RankingEntryResponse(
            game_id=str(game.id),
            status=game.status,
            attempts_used=attempts_used or 0,
            max_attempts=game.max_attempts,
        )
        for game, attempts_used in results
    ]


@router.get("/{game_id}", response_model=GameStateResponse)
def get_game_state(game_id: UUID, db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.id == game_id).first()
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

    return GameStateResponse(
        game_id=str(game.id),
        status=game.status,
        attempts_left=game.max_attempts - len(game.guesses),
        max_attempts=game.max_attempts,
        guesses=guesses,
        secret_code=secret_code_to_reveal,
    )
