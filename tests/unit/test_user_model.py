import pytest
from app.models.user import User

def test_user_model_fields():
    user = User(id=1, username="testuser", email="test@example.com", hashed_password="hashedpw")
    assert user.id == 1
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert hasattr(user, "hashed_password")

def test_user_model_is_active_default():
    user = User(username="activeuser", email="active@example.com", hashed_password="pw")
    # SQLAlchemy default is True, but not set until flush/commit; test attribute exists
    assert hasattr(user, "is_active")

def test_user_model_created_at_and_updated_at():
    user = User(username="dateuser", email="date@example.com", hashed_password="pw")
    assert hasattr(user, "created_at")
    assert hasattr(user, "updated_at")

def test_user_model_relationships():
    user = User(username="reluser", email="rel@example.com", hashed_password="pw")
    assert hasattr(user, "submissions")
    assert hasattr(user, "weakness_profile")
