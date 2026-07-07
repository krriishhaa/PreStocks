import pytest
from app.database.session import SessionLocal
from app.models.user import User
from app.core.security import hash_password


def test_database_connection():
    """Test that database connection works"""
    db = SessionLocal()
    try:
        # Test query
        result = db.query(User).first()
        assert result is None  # Should be empty initially
    finally:
        db.close()


def test_password_hashing():
    """Test password hashing"""
    password = "test_password_123"
    hashed = hash_password(password)
    assert hashed != password
    assert len(hashed) > len(password)


if __name__ == "__main__":
    test_database_connection()
    test_password_hashing()
    print("✓ All setup tests passed")
