"""
test_app.py — pytest test suite for the Flask application

Run: pytest tests/ -v --cov=src --cov-report=term-missing
"""

import sys
import os

# Allow importing from src/ without installing as a package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

from app import create_app


@pytest.fixture()
def app():
    """Create a test Flask application instance."""
    application = create_app()
    application.config["TESTING"] = True
    yield application


@pytest.fixture()
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


# ─── /health endpoint ────────────────────────────────────────────────────────

class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_json(self, client):
        response = client.get("/health")
        data = response.get_json()
        assert data is not None

    def test_health_status_is_ok(self, client):
        response = client.get("/health")
        data = response.get_json()
        assert data["status"] == "ok"

    def test_health_returns_version(self, client):
        response = client.get("/health")
        data = response.get_json()
        assert "version" in data

    def test_health_version_uses_env_var(self, client, monkeypatch):
        monkeypatch.setenv("APP_VERSION", "2.5.0")
        # Recreate app to pick up new env var
        new_app = create_app()
        new_app.config["TESTING"] = True
        new_client = new_app.test_client()
        response = new_client.get("/health")
        data = response.get_json()
        assert data["version"] == "2.5.0"


# ─── /hello endpoint ─────────────────────────────────────────────────────────

class TestHelloEndpoint:
    def test_hello_returns_200(self, client):
        response = client.get("/hello")
        assert response.status_code == 200

    def test_hello_default_greeting(self, client):
        response = client.get("/hello")
        data = response.get_json()
        assert data["message"] == "Hello, World!"

    def test_hello_custom_name(self, client):
        response = client.get("/hello?name=Alice")
        data = response.get_json()
        assert data["message"] == "Hello, Alice!"

    def test_hello_name_with_spaces(self, client):
        response = client.get("/hello?name=GitHub+Actions")
        data = response.get_json()
        assert data["message"] == "Hello, GitHub Actions!"


# ─── /add endpoint ───────────────────────────────────────────────────────────

class TestAddEndpoint:
    def test_add_two_integers(self, client):
        response = client.get("/add?a=3&b=4")
        assert response.status_code == 200
        data = response.get_json()
        assert data["result"] == 7

    def test_add_two_floats(self, client):
        response = client.get("/add?a=1.5&b=2.5")
        assert response.status_code == 200
        data = response.get_json()
        assert data["result"] == 4

    def test_add_negative_numbers(self, client):
        response = client.get("/add?a=-5&b=3")
        data = response.get_json()
        assert data["result"] == -2

    def test_add_with_zero(self, client):
        response = client.get("/add?a=10&b=0")
        data = response.get_json()
        assert data["result"] == 10

    def test_add_missing_param_a(self, client):
        response = client.get("/add?b=5")
        assert response.status_code == 400

    def test_add_missing_param_b(self, client):
        response = client.get("/add?a=5")
        assert response.status_code == 400

    def test_add_missing_both_params(self, client):
        response = client.get("/add")
        assert response.status_code == 400

    def test_add_non_numeric_a(self, client):
        response = client.get("/add?a=hello&b=5")
        assert response.status_code == 400

    def test_add_non_numeric_b(self, client):
        response = client.get("/add?a=5&b=world")
        assert response.status_code == 400

    def test_add_error_message(self, client):
        response = client.get("/add?a=x&b=y")
        data = response.get_json()
        assert "error" in data


# ─── 404 handler ─────────────────────────────────────────────────────────────

class TestNotFound:
    def test_unknown_route_returns_404(self, client):
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_unknown_route_returns_error_json(self, client):
        response = client.get("/nonexistent")
        data = response.get_json()
        assert "error" in data

    def test_post_to_get_only_route(self, client):
        response = client.post("/hello")
        assert response.status_code == 405
