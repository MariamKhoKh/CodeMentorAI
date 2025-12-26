import pytest
import asyncio
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_register_and_login():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register a new user
        register_data = {
            "email": "testuser@example.com",
            "username": "testuser",
            "password": "testpassword123"
        }
        response = await client.post("/api/auth/register", json=register_data)
        assert response.status_code == 201
        user = response.json()
        assert user["email"] == register_data["email"]
        assert user["username"] == register_data["username"]
        assert user["is_active"] is True

        # Login with the new user
        login_data = {
            "username": register_data["email"],
            "password": register_data["password"]
        }
        response = await client.post("/api/auth/login", data=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        assert token

        # Get current user info
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/api/auth/me", headers=headers)
        assert response.status_code == 200
        user_info = response.json()
        assert user_info["email"] == register_data["email"]
        assert user_info["username"] == register_data["username"]
