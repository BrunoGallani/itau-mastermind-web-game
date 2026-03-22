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


def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
