def test_create_game(client):
    response = client.post("/games/")
    assert response.status_code == 201
    data = response.json()
    assert "game_id" in data
    assert len(data["game_id"]) > 0
    assert "message" in data


def test_submit_guess_returns_feedback(client):
    create_resp = client.post("/games/")
    game_id = create_resp.json()["game_id"]

    guess_resp = client.post(
        f"/games/{game_id}/guesses",
        json={"colors": ["Red", "Blue", "Green", "Yellow"]},
    )
    assert guess_resp.status_code == 201

    data = guess_resp.json()
    assert data["attempt_number"] == 1
    assert "feedback" in data
    assert "black_pegs" in data["feedback"]
    assert "white_pegs" in data["feedback"]
    assert data["status"] in ("in_progress", "won")
    assert data["attempts_left"] == 9


def test_submit_invalid_guess_wrong_count(client):
    create_resp = client.post("/games/")
    game_id = create_resp.json()["game_id"]

    resp = client.post(
        f"/games/{game_id}/guesses",
        json={"colors": ["Red", "Blue"]},
    )
    assert resp.status_code == 422


def test_submit_invalid_color(client):
    create_resp = client.post("/games/")
    game_id = create_resp.json()["game_id"]

    resp = client.post(
        f"/games/{game_id}/guesses",
        json={"colors": ["Red", "Blue", "Pink", "Yellow"]},
    )
    assert resp.status_code == 422


def test_game_not_found(client):
    resp = client.get("/games/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


def test_get_game_state(client):
    create_resp = client.post("/games/")
    game_id = create_resp.json()["game_id"]

    client.post(
        f"/games/{game_id}/guesses",
        json={"colors": ["Red", "Blue", "Green", "Yellow"]},
    )

    state_resp = client.get(f"/games/{game_id}")
    assert state_resp.status_code == 200

    data = state_resp.json()
    assert data["status"] in ("in_progress", "won")
    assert len(data["guesses"]) == 1
    assert data["attempts_left"] == 9
    assert data["max_attempts"] == 10


def test_cannot_guess_after_game_over(client):
    create_resp = client.post("/games/")
    game_id = create_resp.json()["game_id"]

    for _ in range(10):
        resp = client.post(
            f"/games/{game_id}/guesses",
            json={"colors": ["Red", "Red", "Red", "Red"]},
        )
        if resp.json()["status"] != "in_progress":
            break

    resp = client.post(
        f"/games/{game_id}/guesses",
        json={"colors": ["Red", "Red", "Red", "Red"]},
    )
    assert resp.status_code == 400


def test_secret_code_hidden_during_game(client):
    create_resp = client.post("/games/")
    game_id = create_resp.json()["game_id"]

    state_resp = client.get(f"/games/{game_id}")
    data = state_resp.json()
    assert data["secret_code"] is None


def test_health_check(unauthenticated_client):
    resp = unauthenticated_client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_create_game_unauthenticated(unauthenticated_client):
    response = unauthenticated_client.post("/games/")
    assert response.status_code == 401


def test_ranking_empty(unauthenticated_client):
    resp = unauthenticated_client.get("/games/ranking/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_ranking_after_game(client):
    create_resp = client.post("/games/")
    game_id = create_resp.json()["game_id"]

    for _ in range(10):
        resp = client.post(
            f"/games/{game_id}/guesses",
            json={"colors": ["Red", "Red", "Red", "Red"]},
        )
        if resp.json()["status"] != "in_progress":
            break

    ranking_resp = client.get("/games/ranking/")
    assert ranking_resp.status_code == 200
    data = ranking_resp.json()
    assert len(data) >= 1
    entry = data[0]
    assert entry["game_id"] == game_id
    assert entry["username"] == "testplayer"
    assert entry["status"] in ("won", "lost")
    assert "score" in entry
    assert "duration_seconds" in entry


def test_game_loss_after_max_attempts(client):
    create_resp = client.post("/games/")
    game_id = create_resp.json()["game_id"]

    last_resp = None
    for _ in range(10):
        last_resp = client.post(
            f"/games/{game_id}/guesses",
            json={"colors": ["Purple", "Purple", "Purple", "Purple"]},
        )
        if last_resp.json()["status"] != "in_progress":
            break

    data = last_resp.json()
    if data["status"] == "lost":
        assert data["score"] == 0
        assert data["secret_code"] is not None
        assert len(data["secret_code"]) == 4


def test_game_state_has_timestamps(client):
    create_resp = client.post("/games/")
    game_id = create_resp.json()["game_id"]

    state_resp = client.get(f"/games/{game_id}")
    data = state_resp.json()
    assert data["started_at"] is not None
    assert "duration_seconds" in data


def test_my_games_empty(client):
    resp = client.get("/games/my-games/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_my_games_lists_user_games(client):
    # Criar dois jogos
    client.post("/games/")
    client.post("/games/")

    resp = client.get("/games/my-games/")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    # Verificar ordenação: mais recente primeiro
    assert data[0]["started_at"] >= data[1]["started_at"]


def test_my_games_has_correct_fields(client):
    create_resp = client.post("/games/")
    game_id = create_resp.json()["game_id"]

    # Submeter uma tentativa
    client.post(
        f"/games/{game_id}/guesses",
        json={"colors": ["Red", "Blue", "Green", "Yellow"]},
    )

    resp = client.get("/games/my-games/")
    data = resp.json()
    assert len(data) == 1
    entry = data[0]
    assert entry["game_id"] == game_id
    assert entry["status"] in ("in_progress", "won")
    assert entry["attempts_used"] == 1
    assert entry["max_attempts"] == 10
    assert entry["started_at"] is not None
    assert "duration_seconds" in entry


def test_my_games_unauthenticated(unauthenticated_client):
    resp = unauthenticated_client.get("/games/my-games/")
    assert resp.status_code == 401


def test_my_games_shows_finished_game_score(client):
    create_resp = client.post("/games/")
    game_id = create_resp.json()["game_id"]

    for _ in range(10):
        resp = client.post(
            f"/games/{game_id}/guesses",
            json={"colors": ["Purple", "Purple", "Purple", "Purple"]},
        )
        if resp.json()["status"] != "in_progress":
            break

    resp = client.get("/games/my-games/")
    data = resp.json()
    finished = [g for g in data if g["status"] != "in_progress"]
    assert len(finished) >= 1
    assert finished[0]["score"] is not None
    assert finished[0]["finished_at"] is not None
