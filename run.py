"""Recommended local development entry point: `python run.py`."""
import os
from backend import app

if __name__ == "__main__":
    app.run(host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", "5000")), debug=False)
