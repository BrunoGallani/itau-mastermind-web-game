from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException

from app.config import utc_now
from app.database import persist, save, save_and_refresh
from app.constants import GameError
from app.models import Game, Guess, User
from app.dto import Feedback, GuessResult, RankingEntry
from app.game_logic import (
    generate_secret_code,
    evaluate_guess,
    calculate_score,
    CODE_LENGTH,
    MAX_ATTEMPTS,
    GameStatus,
)


def abandon_stale_games(db: Session) -> int:
    """Abandona jogos que ficaram em andamento após reinício do servidor."""
    stale = db.query(Game).filter(Game.status == GameStatus.IN_PROGRESS).all()
    for game in stale:
        game.status = GameStatus.ABANDONED
        game.score = 0
    save(db)
    return len(stale)


def _get_user_game(game_id: UUID, user: User, db: Session) -> Game:
    game = db.query(Game).filter(Game.id == game_id, Game.user_id == user.id).first()
    if not game:
        raise HTTPException(status_code=404, detail=GameError.NOT_FOUND)
    return game


def calculate_duration(game: Game) -> int | None:
    if game.finished_at and game.started_at:
        return int((game.finished_at - game.started_at).total_seconds())
    return None


def abandon_game(game_id: UUID, user: User, db: Session) -> Game:
    """Abandona um jogo em andamento."""
    game = _get_user_game(game_id, user, db)

    if game.status != GameStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=400,
            detail=GameError.NOT_IN_PROGRESS,
        )

    game.status = GameStatus.ABANDONED
    game.finished_at = utc_now()
    game.score = 0
    save_and_refresh(db, game)
    return game


def create_game(user: User, db: Session) -> Game:
    """Cria um novo jogo para o usuário."""
    secret = generate_secret_code()
    game = Game(
        user_id=user.id,
        secret_code=secret,
        status=GameStatus.IN_PROGRESS,
        max_attempts=MAX_ATTEMPTS,
    )
    persist(db, game)
    return game


def submit_guess(game_id: UUID, colors: list[str], user: User, db: Session) -> GuessResult:
    """Submete uma tentativa e retorna o resultado."""
    game = _get_user_game(game_id, user, db)

    if game.status != GameStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=400,
            detail=GameError.ALREADY_FINISHED.format(status=game.status),
        )

    current_attempt = len(game.guesses) + 1
    feedback = evaluate_guess(game.secret_code, colors)

    guess = Guess(
        game_id=game.id,
        attempt_number=current_attempt,
        colors=colors,
        black_pegs=feedback.black_pegs,
        white_pegs=feedback.white_pegs,
    )
    db.add(guess)

    secret_code_to_reveal = None
    score = None

    if feedback.black_pegs == CODE_LENGTH:
        game.status = GameStatus.WON
        game.finished_at = utc_now()
        duration = int((game.finished_at - game.started_at).total_seconds())
        game.score = calculate_score(current_attempt, duration)
        score = game.score
        secret_code_to_reveal = game.secret_code
    elif current_attempt >= game.max_attempts:
        game.status = GameStatus.LOST
        game.finished_at = utc_now()
        game.score = 0
        score = 0
        secret_code_to_reveal = game.secret_code

    save(db)

    return GuessResult(
        attempt_number=current_attempt,
        feedback=feedback,
        status=game.status,
        attempts_left=game.max_attempts - current_attempt,
        score=score,
        secret_code=secret_code_to_reveal,
    )


def get_game_state(game_id: UUID, user: User, db: Session) -> Game:
    """Retorna o estado completo de um jogo."""
    return _get_user_game(game_id, user, db)


def get_user_games(user: User, db: Session) -> list[Game]:
    """Retorna todos os jogos do usuário, ordenados do mais recente ao mais antigo."""
    return (
        db.query(Game)
        .filter(Game.user_id == user.id)
        .order_by(Game.started_at.desc())
        .all()
    )


def get_ranking(db: Session) -> list[RankingEntry]:
    """Retorna o ranking de jogos finalizados."""
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
        .filter(Game.status.in_([GameStatus.WON, GameStatus.LOST]))
        .order_by(Game.score.desc().nullslast(), attempts_subq.c.attempts_used.asc())
        .all()
    )

    return [
        RankingEntry(
            game_id=str(game.id),
            username=username,
            status=game.status,
            attempts_used=attempts_used or 0,
            max_attempts=game.max_attempts,
            score=game.score,
            duration_seconds=calculate_duration(game),
        )
        for game, username, attempts_used in results
    ]
