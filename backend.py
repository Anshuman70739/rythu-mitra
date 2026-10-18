"""Compatibility entry point for existing `python backend.py` workflows."""
import os
from rythu_mitra_backend import create_app
app = create_app()

if __name__ == "__main__":
    app.run(host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", "5000")), debug=False)
