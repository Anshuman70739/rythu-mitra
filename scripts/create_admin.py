"""Create the first administrator securely; passwords are never echoed."""
from __future__ import annotations
import sys
from pathlib import Path as _BootstrapPath
sys.path.insert(0, str(_BootstrapPath(__file__).resolve().parents[1]))
import getpass
import re
import sys
from werkzeug.security import generate_password_hash
from rythu_mitra_backend import create_app
from rythu_mitra_backend.db import connect, utc_now
from rythu_mitra_backend.security import audit


def main() -> int:
    app = create_app()
    with app.app_context():
        with connect() as conn:
            if conn.execute("SELECT 1 FROM users WHERE role='admin' AND is_active=1 LIMIT 1").fetchone():
                print("An active administrator already exists. Sign in or use the authenticated admin management API.")
                return 2
        name = input("Administrator name: ").strip()
        phone = input("Phone number (8–15 digits): ").strip()
        password = getpass.getpass("New password (minimum 12 characters): ")
        confirm = getpass.getpass("Confirm password: ")
        if not name or len(name) > 120:
            print("Name must contain 1–120 characters."); return 2
        if not re.fullmatch(r"\d{8,15}", phone):
            print("Phone number must contain 8–15 digits."); return 2
        if len(password) < 12 or password != confirm:
            print("Passwords must match and contain at least 12 characters."); return 2
        stamp = utc_now()
        try:
            with connect() as conn:
                cur = conn.execute("INSERT INTO users(name,phone,role,password_hash,language,is_active,created_at,updated_at) VALUES(?,?, 'admin', ?, 'en', 1, ?, ?)",
                                   (name, phone, generate_password_hash(password), stamp, stamp))
                uid = cur.lastrowid
            audit("admin_bootstrap_created", "users", uid, {})
        except Exception as exc:
            print(f"Administrator account was not created ({type(exc).__name__}). Check whether the phone is already registered.")
            return 1
        print(f"Administrator created successfully (user id {uid}). Keep the password private.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
