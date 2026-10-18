from __future__ import annotations
import pytest
from rythu_mitra_backend import create_app


@pytest.fixture()
def app(tmp_path):
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key-that-is-long-enough-for-test-only",
        "APP_ENV": "test",
        "DEMO_MODE": False,
        "SESSION_COOKIE_SECURE": False,
        "DATABASE_PATH": str(tmp_path / "test.db"),
        "UPLOAD_DIR": str(tmp_path / "uploads"),
        "MODEL_DIR": str(tmp_path / "models"),
        "OPENWEATHER_API_KEY": "",
        "DATA_GOV_IN_API_KEY": "",
        "MARKET_DEFAULT_STATE": "Telangana",
        "MARKET_DATA_API_KEY": "",
        "MARKET_DATA_BASE_URL": "",
    })
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def register(client, phone="9000000001", role="farmer"):
    token = client.get("/api/session").get_json()["csrf_token"]
    response = client.post("/api/register", json={
        "name": "Test Farmer", "phone": phone, "password": "a-safe-test-password", "role": role, "language": "en"
    }, headers={"X-CSRF-Token": token})
    assert response.status_code == 201, response.get_data(as_text=True)
    body = response.get_json()
    assert "password_hash" not in body["user"]
    assert "phone" not in body["user"]
    return body["csrf_token"], body["user"]
