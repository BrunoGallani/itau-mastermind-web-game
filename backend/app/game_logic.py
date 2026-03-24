import random

VALID_COLORS = ["Red", "Blue", "Green", "Yellow", "Orange", "Purple"]
CODE_LENGTH = 4
MAX_ATTEMPTS = 10

BASE_SCORE = 1000
ATTEMPT_PENALTY = 100
TIME_DIVISOR = 10


class GameStatus:
    IN_PROGRESS = "in_progress"
    WON = "won"
    LOST = "lost"
    ABANDONED = "abandoned"


def generate_secret_code() -> list[str]:
    return [random.choice(VALID_COLORS) for _ in range(CODE_LENGTH)]


def evaluate_guess(secret: list[str], guess: list[str]) -> dict:
    black_pegs = 0
    secret_remaining = []
    guess_remaining = []

    for i in range(CODE_LENGTH):
        if guess[i] == secret[i]:
            black_pegs += 1
        else:
            secret_remaining.append(secret[i])
            guess_remaining.append(guess[i])

    white_pegs = 0
    for color in guess_remaining:
        if color in secret_remaining:
            white_pegs += 1
            secret_remaining.remove(color)

    return {"black_pegs": black_pegs, "white_pegs": white_pegs}


def calculate_score(attempts_used: int, duration_seconds: int) -> int:
    attempt_penalty = (attempts_used - 1) * ATTEMPT_PENALTY
    time_penalty = duration_seconds // TIME_DIVISOR
    return max(0, BASE_SCORE - attempt_penalty - time_penalty)
