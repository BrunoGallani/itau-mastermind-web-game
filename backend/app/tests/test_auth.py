def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={"username": "testuser", "password": "password123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Usuário registrado com sucesso!"
    assert data["user"]["username"] == "testuser"


def test_register_duplicate_username(client):
    client.post(
        "/auth/register",
        json={"username": "duplicate", "password": "password123"},
    )
    response = client.post(
        "/auth/register",
        json={"username": "duplicate", "password": "password456"},
    )
    assert response.status_code == 400
    assert "já existe" in response.json()["detail"]


def test_login_success(client):
    client.post(
        "/auth/register",
        json={"username": "loginuser", "password": "password123"},
    )
    response = client.post(
        "/auth/login",
        json={"username": "loginuser", "password": "password123"},
    )
    assert response.status_code == 200
    assert "session_id" in response.cookies


def test_login_invalid_credentials(client):
    response = client.post(
        "/auth/login",
        json={"username": "nonexistent", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_get_me_authenticated(client):
    client.post(
        "/auth/register",
        json={"username": "meuser", "password": "password123"},
    )
    response = client.get("/auth/me")
    assert response.status_code == 200
    assert response.json()["username"] == "meuser"


def test_get_me_unauthenticated(unauthenticated_client):
    response = unauthenticated_client.get("/auth/me")
    assert response.status_code == 401


def test_logout(client):
    client.post(
        "/auth/register",
        json={"username": "logoutuser", "password": "password123"},
    )
    response = client.post("/auth/logout")
    assert response.status_code == 200

    response = client.get("/auth/me")
    assert response.status_code == 401


def test_username_too_short(client):
    response = client.post(
        "/auth/register",
        json={"username": "ab", "password": "password123"},
    )
    assert response.status_code == 422


def test_password_too_short(client):
    response = client.post(
        "/auth/register",
        json={"username": "validuser", "password": "12345"},
    )
    assert response.status_code == 422
