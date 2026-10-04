from fastapi.testclient import TestClient

from api import api


client = TestClient(api)


def test_login_success():

    response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "Admin@123"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["username"] == "admin"
    assert data["role"] == "ADMIN"


def test_login_invalid_password():

    response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "wrong-password"
        }
    )

    assert response.status_code == 401


def test_protected_endpoint_without_token():

    response = client.get(
        "/auth/me"
    )

    assert response.status_code == 401


def test_auth_me():

    login_response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "Admin@123"
        }
    )

    token = login_response.json()[
        "access_token"
    ]

    response = client.get(
        "/auth/me",
        headers={
            "Authorization":
                f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "admin"
    assert data["role"] == "ADMIN"
    assert data["is_active"] is True