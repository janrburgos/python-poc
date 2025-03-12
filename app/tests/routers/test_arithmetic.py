from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/arithmetic")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Arithmetic API"}


def test_add():
    response = client.get("/arithmetic/add/1/2")
    assert response.status_code == 200
    assert response.json() == {"operation": "addition", "result": 3.0}


def test_subtract():
    response = client.get("/arithmetic/subtract/5/3")
    assert response.status_code == 200
    assert response.json() == {"operation": "subtraction", "result": 2.0}


def test_multiply():
    response = client.get("/arithmetic/multiply/2/3")
    assert response.status_code == 200
    assert response.json() == {"operation": "multiplication", "result": 6.0}


def test_divide():
    response = client.get("/arithmetic/divide/6/2")
    assert response.status_code == 200
    assert response.json() == {"operation": "division", "result": 3.0}


def test_divide_by_zero():
    response = client.get("/arithmetic/divide/6/0")
    assert response.status_code == 400
    assert response.json() == {"detail": "Cannot divide by zero"}
