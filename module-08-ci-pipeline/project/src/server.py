"""
server.py — Application entry point

Imports the Flask app factory and starts the HTTP server.
Run this file directly: python src/server.py
"""

import os

from app import create_app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 3000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

    print(f"Starting server on port {port} (debug={debug})")
    app.run(host="0.0.0.0", port=port, debug=debug)
