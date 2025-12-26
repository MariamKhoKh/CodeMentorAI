import pytest
import asyncio
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_problem_crud_flow():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register and login
        register_data = {
            "email": "probuser@example.com",
            "username": "probuser",
            "password": "probpass123"
        }
        await client.post("/api/auth/register", json=register_data)
        login_data = {"username": register_data["email"], "password": register_data["password"]}
        login_resp = await client.post("/api/auth/login", data=login_data)
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create a problem
        problem_data = {
            "title": "Sum Two Numbers",
            "slug": "sum-two-numbers",
            "description": "Add two numbers.",
            "difficulty": "EASY",
            "constraints": {"input": "int, int", "output": "int"},
            "tags": ["Math"],
            "test_cases": [
                {"input": [1, 2], "expected_output": 3, "is_hidden": False}
            ],
            "starter_code": {"python": "def sum_two(a, b):\n    pass"},
            "reference_solution": {"python": "def sum_two(a, b):\n    return a + b"}
        }
        resp = await client.post("/api/problems/", json=problem_data, headers=headers)
        assert resp.status_code == 201
        problem = resp.json()
        assert problem["title"] == problem_data["title"]
        problem_id = problem["id"]

        # Get problem by id
        resp = await client.get(f"/api/problems/{problem_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["slug"] == problem_data["slug"]

        # Update problem
        update_data = {"description": "Add two integers."}
        resp = await client.put(f"/api/problems/{problem_id}", json=update_data, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["description"] == "Add two integers."

        # Delete problem
        resp = await client.delete(f"/api/problems/{problem_id}", headers=headers)
        assert resp.status_code == 204
        # Confirm deletion
        resp = await client.get(f"/api/problems/{problem_id}", headers=headers)
        assert resp.status_code == 404
