import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_create_problem():
    """Test creating a new problem."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        problem_data = {
            "title": "Test Problem",
            "slug": "test-problem",
            "description": "This is a test problem",
            "difficulty": "easy",
            "tags": ["Array", "Test"],
            "test_cases": [
                {
                    "input": {"nums": [1, 2, 3]},
                    "expected_output": 6,
                    "is_hidden": False
                }
            ],
            "optimal_patterns": {
                "time_complexity": "O(n)",
                "space_complexity": "O(1)",
                "key_patterns": ["Iteration"],
                "key_data_structures": ["Array"]
            }
        }
        
        response = await client.post("/api/problems/", json=problem_data)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Problem"
        assert data["slug"] == "test-problem"


@pytest.mark.asyncio
async def test_list_problems():
    """Test listing problems."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/problems/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_problem_by_id():
    """Test getting a problem by ID."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First create a problem
        problem_data = {
            "title": "Get Test",
            "slug": "get-test",
            "description": "Test",
            "difficulty": "easy",
            "tags": [],
            "test_cases": [
                {"input": {}, "expected_output": True, "is_hidden": False}
            ]
        }
        create_response = await client.post("/api/problems/", json=problem_data)
        problem_id = create_response.json()["id"]
        
        # Get the problem
        response = await client.get(f"/api/problems/{problem_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == problem_id


@pytest.mark.asyncio
async def test_get_problem_stats():
    """Test getting problem statistics."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/problems/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_problems" in data
        assert "by_difficulty" in data
        assert "by_tags" in data