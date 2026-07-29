"""Run entrypoint for RentSathi Flask app.

This file adjusts PYTHONPATH so imports like `from config import Config` work
when running from the project root.
"""

import os
import sys

# Ensure project root (the directory containing config.py and app/) is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import create_app, socketio

app = create_app()

if __name__ == "__main__":
    socketio.run(app, debug=True)