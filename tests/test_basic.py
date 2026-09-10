from fastapi.testclient import TestClient
from sqlalchemy import update

import db
from main import app
from models import User
from tests.conftest import TestingSessionLocal

client = TestClient(app)

def test_register(setup_database):
    response = client.post(
        "/register",
        json={
            "email": "pytest@example.com",
            "password": "test123",
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "pytest@example.com"
    assert data["role"] == "user"
    assert data["is_active"] is True
    assert "password" not in data
    assert "password_hash" not in data

def test_register_duplicate_email(setup_database):
    client.post(
        "/register",
        json={
            "email": "pytest@example.com",
            "password": "test123",
        }
    )

    response = client.post(
        "/register",
        json={
            "email": "pytest@example.com",
            "password": "test123",
        }
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "User with this email already exists"

def test_login(setup_database):
    client.post(
        "/register",
        json={
            "email": "pytest@example.com",
            "password": "test123",
        }
    )

    response = client.post(
        "/login",
        json={
            "email": "pytest@example.com",
            "password": "test123"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(setup_database):
    client.post(
        "/register",
        json={
            "email": "pytest@example.com",
            "password": "test123",
        }
    )

    response = client.post(
        "/login",
        json={
            "email": "pytest@example.com",
            "password": "test"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"

def test_login_unknown_email(setup_database):
    response = client.post(
        "/login",
        json={
            "email": "example@example.com",
            "password": "test123"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"

def test_me(setup_database):
    client.post(
        "/register",
        json={
            "email": "pytest@example.com",
            "password": "test123",
        }
    )

    login_response = client.post(
        "/login",
        json={
            "email": "pytest@example.com",
            "password": "test123"
        }
    )

    response = client.get(
        "/me",
        headers={
            "Authorization": f"Bearer {login_response.json()['access_token']}"
        }
    )

    assert response.status_code == 200
    assert response.json()["email"] == "pytest@example.com"

def test_user_cannot_create_room(setup_database):
    client.post(
        "/register",
        json={
            "email": "pytest@example.com",
            "password": "test123",
        }
    )

    login_response = client.post(
        "/login",
        json={
            "email": "pytest@example.com",
            "password": "test123"
        }
    )

    response = client.post(
        "/rooms",
        json={
            "name": "Test Room",
            "room_number": "A1",
            "capacity": 10,
            "floor": 1
        },
        headers={
            "Authorization": f"Bearer {login_response.json()['access_token']}"
        }
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden"

def test_admin_creating_room(setup_database):
    client.post(
        "/register",
        json={
            "email": "pytest@example.com",
            "password": "test123",
        }
    )

    db = TestingSessionLocal()

    stmt = update(User).where(User.email == "pytest@example.com").values(role="admin")
    db.execute(stmt)
    db.commit()
    db.close()

    login_response = client.post(
        "/login",
        json={
            "email": "pytest@example.com",
            "password": "test123"
        }
    )

    response = client.post(
        "/rooms",
        json={
            "name": "Test Room",
            "room_number": "A1",
            "capacity": 10,
            "floor": 1
        },
        headers={
            "Authorization": f"Bearer {login_response.json()['access_token']}"
        }
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Test Room"

def test_create_reservation(setup_database):
    client.post(
        "/register",
        json={
            "email": "pytest@example.com",
            "password": "test123",
        }
    )

    db = TestingSessionLocal()

    stmt = update(User).where(User.email == "pytest@example.com").values(role="admin")
    db.execute(stmt)
    db.commit()
    db.close()

    login_response = client.post(
        "/login",
        json={
            "email": "pytest@example.com",
            "password": "test123"
        }
    )

    client.post(
        "/rooms",
        json={
            "name": "Test Room",
            "room_number": "A1",
            "capacity": 10,
            "floor": 1
        },
        headers={
            "Authorization": f"Bearer {login_response.json()['access_token']}"
        }
    )

    response = client.post(
        "/reservations",
        json={
            "room_id": 1,
            "start_time": "2026-09-10T19:00:00",
            "end_time": "2026-09-10T20:00:00",
        },
        headers={
            "Authorization": f"Bearer {login_response.json()['access_token']}"
        }
    )

    print(response.json())

    assert response.status_code == 200
    assert response.json()["room_id"] == 1
    assert response.json()["start_time"].startswith("2026-09-10T19:00:00")
    assert response.json()["user_id"] == 1

def test_create_reservation_conflict(setup_database):
    client.post(
        "/register",
        json={
            "email": "pytest@example.com",
            "password": "test123",
        }
    )

    db = TestingSessionLocal()

    stmt = update(User).where(User.email == "pytest@example.com").values(role="admin")
    db.execute(stmt)
    db.commit()
    db.close()

    login_response = client.post(
        "/login",
        json={
            "email": "pytest@example.com",
            "password": "test123"
        }
    )

    client.post(
        "/rooms",
        json={
            "name": "Test Room",
            "room_number": "A1",
            "capacity": 10,
            "floor": 1
        },
        headers={
            "Authorization": f"Bearer {login_response.json()['access_token']}"
        }
    )

    client.post(
        "/reservations",
        json={
            "room_id": 1,
            "start_time": "2026-09-10T19:00:00",
            "end_time": "2026-09-10T20:00:00",
        },
        headers={
            "Authorization": f"Bearer {login_response.json()['access_token']}"
        }
    )

    response = client.post(
        "/reservations",
        json={
            "room_id": 1,
            "start_time": "2026-09-10T19:30:00",
            "end_time": "2026-09-10T20:30:00",
        },
        headers={
            "Authorization": f"Bearer {login_response.json()['access_token']}"
        }
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Room already reserved in this time range"





