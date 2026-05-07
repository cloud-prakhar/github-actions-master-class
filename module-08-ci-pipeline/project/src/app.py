"""
app.py — Flask application factory

Creates and configures the Flask app. Does NOT start the server here —
that happens in server.py. This separation allows tests to import the
app without binding to a real port.
"""

import os

from flask import Flask, jsonify, request


def create_app() -> Flask:
    """Application factory — returns a configured Flask app instance."""
    app = Flask(__name__)

    # ─── Health Check ────────────────────────────────────────────────────────
    # GET /health
    # Used by load balancers, CI pipelines, and monitoring systems to check
    # whether the application is running and responding correctly.
    @app.get("/health")
    def health():
        return jsonify({
            "status": "ok",
            "version": os.environ.get("APP_VERSION", "1.0.0"),
        }), 200

    # ─── Hello Endpoint ──────────────────────────────────────────────────────
    # GET /hello?name=<optional name>
    # Returns a greeting. Accepts an optional "name" query parameter.
    @app.get("/hello")
    def hello():
        name = request.args.get("name", "World")
        return jsonify({"message": f"Hello, {name}!"}), 200

    # ─── Addition Endpoint ───────────────────────────────────────────────────
    # GET /add?a=<number>&b=<number>
    # Adds two numbers provided as query parameters.
    # Returns 400 if parameters are missing or not valid numbers.
    @app.get("/add")
    def add():
        a_raw = request.args.get("a")
        b_raw = request.args.get("b")

        if a_raw is None or b_raw is None:
            return jsonify({
                "error": "Parameters 'a' and 'b' are required and must be numbers"
            }), 400

        try:
            a = float(a_raw)
            b = float(b_raw)
        except ValueError:
            return jsonify({
                "error": "Parameters 'a' and 'b' are required and must be numbers"
            }), 400

        result = a + b
        # Return integer if the result is a whole number
        if result == int(result):
            result = int(result)

        return jsonify({"result": result}), 200

    # ─── 404 Handler ─────────────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": f"Route {request.method} {request.path} not found"
        }), 404

    # ─── 500 Handler ─────────────────────────────────────────────────────────
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500

    return app
