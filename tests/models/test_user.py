from app.models.user import User


def test_user_model_attributes():
    """Test that the User model has the correct attributes"""
    user = User(id=1, username="testuser", email="test@example.com")

    assert hasattr(user, "id")
    assert hasattr(user, "username")
    assert hasattr(user, "email")

    assert user.id == 1
    assert user.username == "testuser"
    assert user.email == "test@example.com"


def test_user_repr():
    """Test the string representation of the User model"""
    user = User(id=1, username="testuser", email="test@example.com")
    assert repr(user) == "User(id=1, username='testuser', email='test@example.com')"


def test_create_user_without_id():
    """Test creating a user without providing an ID (assumes autoincrement in DB)"""
    user = User(username="testuser", email="test@example.com")

    assert user.username == "testuser"
    assert user.email == "test@example.com"
