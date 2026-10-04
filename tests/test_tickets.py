from fastapi.testclient import TestClient

from api import api


client = TestClient(api)


def get_admin_token():

    response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "Admin@123"
        }
    )

    assert response.status_code == 200

    return response.json()[
        "access_token"
    ]


def test_list_tickets():

    token = get_admin_token()

    response = client.get(
        "/tickets",
        headers={
            "Authorization":
                f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list
    )


def test_create_ticket():

    token = get_admin_token()

    response = client.post(
        "/tickets",
        headers={
            "Authorization":
                f"Bearer {token}"
        },
        json={
            "title":
                "Automated test ticket",
            "description":
                "Ticket created during automated testing.",
            "category":
                "OTHER"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "ticket_id" in data
    assert "message" in data

    assert isinstance(
        data["ticket_id"],
        int
    )


def test_get_nonexistent_ticket():

    token = get_admin_token()

    response = client.get(
        "/tickets/999999999",
        headers={
            "Authorization":
                f"Bearer {token}"
        }
    )

    assert response.status_code == 404