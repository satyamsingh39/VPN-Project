"""
Flask entry point for the VPN Traffic Classifier web application.

Usage:
    python flask_app.py
"""
from src.web import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
