from app.game_logic import generate_secret_code, evaluate_guess, calculate_score, VALID_COLORS, CODE_LENGTH


class TestGenerateSecretCode:
    def test_returns_list_with_correct_length(self):
        code = generate_secret_code()
        assert len(code) == CODE_LENGTH

    def test_all_colors_are_valid(self):
        code = generate_secret_code()
        for color in code:
            assert color in VALID_COLORS

    def test_is_random(self):
        codes = [tuple(generate_secret_code()) for _ in range(50)]
        unique_codes = set(codes)
        assert len(unique_codes) > 1


class TestEvaluateGuess:
    def test_all_correct(self):
        secret = ["Red", "Blue", "Green", "Yellow"]
        result = evaluate_guess(secret, secret)
        assert result == {"black_pegs": 4, "white_pegs": 0}

    def test_all_wrong_color(self):
        secret = ["Red", "Red", "Red", "Red"]
        guess = ["Blue", "Blue", "Blue", "Blue"]
        result = evaluate_guess(secret, guess)
        assert result == {"black_pegs": 0, "white_pegs": 0}

    def test_all_right_color_wrong_position(self):
        secret = ["Red", "Blue", "Green", "Yellow"]
        guess = ["Yellow", "Green", "Blue", "Red"]
        result = evaluate_guess(secret, guess)
        assert result == {"black_pegs": 0, "white_pegs": 4}

    def test_mixed_black_and_white(self):
        secret = ["Red", "Blue", "Green", "Yellow"]
        guess = ["Red", "Green", "Blue", "Yellow"]
        result = evaluate_guess(secret, guess)
        assert result == {"black_pegs": 2, "white_pegs": 2}

    def test_duplicate_in_guess_but_not_in_secret(self):
        secret = ["Red", "Blue", "Green", "Yellow"]
        guess = ["Blue", "Red", "Red", "Green"]
        result = evaluate_guess(secret, guess)
        assert result == {"black_pegs": 0, "white_pegs": 3}

    def test_duplicates_in_both_secret_and_guess(self):
        secret = ["Red", "Red", "Blue", "Blue"]
        guess = ["Red", "Blue", "Red", "Blue"]
        result = evaluate_guess(secret, guess)
        assert result == {"black_pegs": 2, "white_pegs": 2}

    def test_all_same_color_partial_match(self):
        secret = ["Red", "Red", "Blue", "Green"]
        guess = ["Red", "Red", "Red", "Red"]
        result = evaluate_guess(secret, guess)
        assert result == {"black_pegs": 2, "white_pegs": 0}


class TestCalculateScore:
    def test_first_attempt_no_time(self):
        score = calculate_score(attempts_used=1, duration_seconds=0)
        assert score == 1000

    def test_penalty_per_attempt(self):
        score = calculate_score(attempts_used=5, duration_seconds=0)
        assert score == 600

    def test_penalty_per_time(self):
        score = calculate_score(attempts_used=1, duration_seconds=100)
        assert score == 990

    def test_max_attempts_high_time(self):
        score = calculate_score(attempts_used=10, duration_seconds=300)
        assert score == 70

    def test_never_negative(self):
        score = calculate_score(attempts_used=10, duration_seconds=9999)
        assert score == 0
