# backend/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid

@pytest.fixture(scope="module")
def client():
    # TestClient allows us to make requests to the FastAPI app without running the server
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def random_user(client):
    """
    Registers a random user and returns the credentials + token.
    This runs once per module.
    """
    unique_id = str(uuid.uuid4())[:8]
    username = f"user_{unique_id}"
    email = f"user_{unique_id}@test.com"
    password = "testpassword123"
    name = "Test User"

    # 1. Register
    reg_response = client.post("/api/v1/auth/register", json={
        "name": name,
        "username": username,
        "email": email,
        "password": password
    })
    assert reg_response.status_code == 201

    # 2. Login to get Token
    login_response = client.post("/api/v1/auth/token", data={
        "username": email, # OAuth2 form sends email as 'username' field usually
        "password": password
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    return {
        "username": username,
        "email": email,
        "password": password,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"}
    }