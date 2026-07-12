import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_todo():
    response = client.post("/todos/", json={"title": "Buy milk"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Buy milk"
    assert "id" in data


def test_read_todos():
    client.post("/todos/", json={"title": "Test item"})
    response = client.get("/todos/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


def test_update_todo():
    create_resp = client.post("/todos/", json={"title": "Original"})
    todo_id = create_resp.json()["id"]

    response = client.put(f"/todos/{todo_id}", json={"title": "Updated", "completed": True})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"
    assert response.json()["completed"] is True


def test_update_nonexistent_todo_returns_404():
    response = client.put("/todos/99999", json={"title": "Nope", "completed": False})
    assert response.status_code == 404


def test_delete_todo():
    create_resp = client.post("/todos/", json={"title": "To be deleted"})
    todo_id = create_resp.json()["id"]

    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 200

    get_resp = client.get("/todos/")
    ids = [t["id"] for t in get_resp.json()]
    assert todo_id not in ids


def test_delete_nonexistent_todo_returns_404():
    response = client.delete("/todos/99999")
    assert response.status_code == 404