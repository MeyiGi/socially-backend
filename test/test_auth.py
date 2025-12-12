# backend/tests/test_auth.py
import uuid

def test_health_check(client):
    # FIXED: Changed URL from /api/v1/health to /health
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "db": "oracle"}

def test_register_duplicate_fail(client, random_user):
    """Try to register the same user created in conftest.py"""
    response = client.post("/api/v1/auth/register", json={
        "name": "Clone",
        "username": random_user["username"], 
        "email": f"unique_{uuid.uuid4()}@test.com",
        "password": "pw"
    })
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_get_current_user_profile(client, random_user):
    """Use the token to fetch /me"""
    response = client.get("/api/v1/auth/me", headers=random_user["headers"])
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == random_user["email"]
    assert data["username"] == random_user["username"]

def test_unauthorized_access(client):
    """Try to access /me without a token"""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401