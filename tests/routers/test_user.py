import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from tests.utils import clean_table_after_test
from app.models.user import User
from app.main import app
from app.database import get_db


@pytest.fixture
def client():
    return TestClient(app)


def __create_test_user(usernum: int = 1):
    """Function to create a test user inside a unit test."""
    db: Session = next(get_db())

    try:
        user = User(username=f"testuser{usernum}", email=f"test{usernum}@example.com")
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


@clean_table_after_test(User.__tablename__)
def test_create_user(client: TestClient):
    """Test creating a new user"""
    response = client.post(
        "/users/",
        json={"username": "testuser", "email": "test@example.com"},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


@clean_table_after_test(User.__tablename__)
def test_create_duplicate_user(client: TestClient):
    """Test creating a duplicate user should fail"""
    existing_user = __create_test_user()

    response = client.post(
        "/users/",
        json={"username": existing_user.username, "email": existing_user.email},
    )
    data = response.json()

    assert response.status_code == 400
    assert data["detail"] == "Username/Email already exists"


@clean_table_after_test(User.__tablename__)
def test_read_users(client: TestClient):
    """Test retrieving users"""
    __create_test_user(1)
    __create_test_user(2)

    response = client.get("/users/")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2


@clean_table_after_test(User.__tablename__)
def test_read_user(client: TestClient):
    """Test retrieving a specific user by ID"""
    existing_user = __create_test_user()
    user_id = existing_user.id

    response = client.get(f"/users/{user_id}")
    data = response.json()

    assert response.status_code == 200
    assert data["username"] == existing_user.username


def test_read_user_not_found(client: TestClient):
    """Test retrieving a non-existent user should return 404"""
    response = client.get("/users/9999")
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == "User not found"


@clean_table_after_test(User.__tablename__)
def test_search_user_by_username(client: TestClient):
    """Test searching for a user by username"""
    existing_user = __create_test_user()

    response = client.get(f"/users/search?username={existing_user.username}")
    data = response.json()

    assert response.status_code == 200
    assert data["username"] == existing_user.username


@clean_table_after_test(User.__tablename__)
def test_search_user_by_email(client: TestClient):
    """Test searching for a user by username"""
    existing_user = __create_test_user()

    response = client.get(f"/users/search?email={existing_user.email}")
    data = response.json()

    assert response.status_code == 200
    assert data["email"] == existing_user.email


def test_search_user_without_queries(client: TestClient):
    """Test searching for a user but not providing any queries"""
    response = client.get("/users/search")
    data = response.json()

    assert response.status_code == 400
    assert data["detail"] == "Provide either 'username' or 'email' as a query parameter"


def test_search_user_not_found(client: TestClient):
    """Test searching for a user that does not exist"""
    response = client.get("/users/search?username=unknownuser")
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == "User not found"


@clean_table_after_test(User.__tablename__)
def test_partial_update_user(client: TestClient):
    """Test partially updating a user"""
    existing_user = __create_test_user()
    user_id = existing_user.id
    new_username = "newuser"

    response = client.patch(f"/users/{user_id}", json={"username": new_username})
    data = response.json()

    assert response.status_code == 200
    assert data["username"] == new_username
    assert data["email"] == existing_user.email


@clean_table_after_test(User.__tablename__)
def test_update_user(client: TestClient):
    """Test fully updating a user"""
    existing_user = __create_test_user()
    new_username = "updateduser"
    new_email = "updated@example.com"
    user_id = existing_user.id

    response = client.put(
        f"/users/{user_id}", json={"username": new_username, "email": new_email}
    )
    data = response.json()

    assert response.status_code == 200
    assert data["username"] == "updateduser"
    assert data["email"] == "updated@example.com"


def test_update_user_not_found(client: TestClient):
    """Test updating a non-existent user"""
    response = client.put(
        "/users/9999", json={"username": "updateduser", "email": "updated@example.com"}
    )
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == "User not found"


@clean_table_after_test(User.__tablename__)
def test_delete_user(client: TestClient):
    """Test deleting a user"""
    existing_user = __create_test_user()
    user_id = existing_user.id

    response = client.delete(f"/users/{user_id}")
    data = response.json()

    assert response.status_code == 200
    assert data["message"] == "User deleted successfully"

    # Verify user is actually deleted
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 404


@clean_table_after_test(User.__tablename__)
def test_delete_user_not_found(client: TestClient):
    """Test deleting a non-existent user"""
    response = client.delete("/users/9999")
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == "User not found"
