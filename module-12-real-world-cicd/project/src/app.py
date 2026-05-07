"""
app.py — Production Flask application for the real-world CI/CD demo.

Simulates a simple REST API with users, demonstrating the kind of
application that would flow through a production CI/CD pipeline.
"""

from __future__ import annotations

import os

from flask import Flask, jsonify, request

# In-memory user store (simulates a database for this demo)
_USERS: dict[int, dict] = {
    1: {"id": 1, "name": "Alice Smith", "email": "alice@example.com", "role": "admin"},
    2: {"id": 2, "name": "Bob Jones", "email": "bob@example.com", "role": "user"},
    3: {"id": 3, "name": "Carol White", "email": "carol@example.com", "role": "user"},
}


def create_app() -> Flask:
    """Application factory — returns a configured Flask app."""
    app = Flask(__name__)

    # ── Health Check ──────────────────────────────────────────────────────────
    @app.get("/health")
    def health():
        return jsonify({
            "status": "ok",
            "version": os.environ.get("APP_VERSION", "1.0.0"),
            "environment": os.environ.get("APP_ENV", "development"),
        }), 200

    # ── List Users ────────────────────────────────────────────────────────────
    @app.get("/api/users")
    def list_users():
        return jsonify({
            "users": list(_USERS.values()),
            "total": len(_USERS),
        }), 200

    # ── Get User ──────────────────────────────────────────────────────────────
    @app.get("/api/users/<int:user_id>")
    def get_user(user_id: int):
        user = _USERS.get(user_id)
        if user is None:
            return jsonify({"error": f"User {user_id} not found"}), 404
        return jsonify(user), 200

    # ── Create User ───────────────────────────────────────────────────────────
    @app.post("/api/users")
    def create_user():
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Request body must be valid JSON"}), 400

        name = data.get("name", "").strip()
        email = data.get("email", "").strip()

        if not name or not email:
            return jsonify({"error": "Fields 'name' and 'email' are required"}), 400

        new_id = max(_USERS.keys(), default=0) + 1
        user = {"id": new_id, "name": name, "email": email, "role": "user"}
        _USERS[new_id] = user
        return jsonify(user), 201

    # ── 404 Handler ───────────────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": f"Route {request.method} {request.path} not found"}), 404

    # ── 500 Handler ───────────────────────────────────────────────────────────
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500

    return app
