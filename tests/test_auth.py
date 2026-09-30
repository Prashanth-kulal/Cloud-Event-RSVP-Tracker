"""
Integration tests for Authentication API endpoints.
Covers registration, login, role enforcement, and token validation.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_new_user(client: AsyncClient):
    payload = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "SecurePassword123!",
        "role": "ATTENDEE"
    }
    response = await client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["user"]["email"] == "jane@example.com"
    assert data["data"]["user"]["role"] == "ATTENDEE"


@pytest.mark.asyncio
async def test_duplicate_registration_fails(client: AsyncClient):
    payload = {
        "name": "Duplicate User",
        "email": "dupe@example.com",
        "password": "Password123!",
        "role": "ATTENDEE"
    }
    resp1 = await client.post("/api/auth/register", json=payload)
    assert resp1.status_code == 201

    resp2 = await client.post("/api/auth/register", json=payload)
    assert resp2.status_code == 409
    assert "already exists" in resp2.json()["message"].lower()


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    # Register first
    await client.post("/api/auth/register", json={
        "name": "Login User",
        "email": "login@example.com",
        "password": "Password123!",
        "role": "ORGANIZER"
    })

    # Login
    response = await client.post("/api/auth/login", json={
        "email": "login@example.com",
        "password": "Password123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data["data"]
    assert data["data"]["user"]["role"] == "ORGANIZER"


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient):
    await client.post("/api/auth/register", json={
        "name": "User Bad Pass",
        "email": "badpass@example.com",
        "password": "Password123!",
        "role": "ATTENDEE"
    })

    response = await client.post("/api/auth/login", json={
        "email": "badpass@example.com",
        "password": "WrongPassword!"
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_profile(client: AsyncClient, attendee_token: str, attendee_user):
    headers = {"Authorization": f"Bearer {attendee_token}"}
    response = await client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["email"] == attendee_user.email
    assert data["data"]["name"] == attendee_user.name
