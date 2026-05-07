"""test_app.py — Test suite for the real-world CI/CD demo application."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from app import create_app


@pytest.fixture()
def app():
    application = create_app()
    application.config["TESTING"] = True
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()


class TestHealth:
    def test_returns_200(self, client):
        assert client.get("/health").status_code == 200

    def test_status_is_ok(self, client):
        assert client.get("/health").get_json()["status"] == "ok"

    def test_includes_version(self, client):
        assert "version" in client.get("/health").get_json()


class TestListUsers:
    def test_returns_200(self, client):
        assert client.get("/api/users").status_code == 200

    def test_returns_users_list(self, client):
        data = client.get("/api/users").get_json()
        assert "users" in data
        assert isinstance(data["users"], list)

    def test_returns_total_count(self, client):
        data = client.get("/api/users").get_json()
        assert "total" in data
        assert data["total"] == len(data["users"])

    def test_has_expected_fields(self, client):
        users = client.get("/api/users").get_json()["users"]
        for user in users:
            assert "id" in user
            assert "name" in user
            assert "email" in user


class TestGetUser:
    def test_get_existing_user(self, client):
        assert client.get("/api/users/1").status_code == 200

    def test_user_has_correct_id(self, client):
        data = client.get("/api/users/1").get_json()
        assert data["id"] == 1

    def test_get_nonexistent_user_returns_404(self, client):
        assert client.get("/api/users/9999").status_code == 404

    def test_404_includes_error(self, client):
        data = client.get("/api/users/9999").get_json()
        assert "error" in data


class TestCreateUser:
    def test_create_user_returns_201(self, client):
        response = client.post(
            "/api/users",
            json={"name": "Dave Brown", "email": "dave@example.com"}
        )
        assert response.status_code == 201

    def test_created_user_has_id(self, client):
        response = client.post(
            "/api/users",
            json={"name": "Eve Green", "email": "eve@example.com"}
        )
        assert "id" in response.get_json()

    def test_create_without_body_returns_400(self, client):
        assert client.post("/api/users").status_code == 400

    def test_create_missing_name_returns_400(self, client):
        response = client.post("/api/users", json={"email": "test@example.com"})
        assert response.status_code == 400

    def test_create_missing_email_returns_400(self, client):
        response = client.post("/api/users", json={"name": "Test User"})
        assert response.status_code == 400


class TestNotFound:
    def test_unknown_route_404(self, client):
        assert client.get("/api/nothing").status_code == 404
