from __future__ import annotations

from rythu_mitra_backend import create_app


def test_global_api_write_guard_requires_csrf(tmp_path):
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key-that-is-long-enough-for-test-only",
        "APP_ENV": "test",
        "DATABASE_PATH": str(tmp_path / "csrf.db"),
        "UPLOAD_DIR": str(tmp_path / "uploads"),
        "MODEL_DIR": str(tmp_path / "models"),
    })
    # An endpoint without its own csrf_required decorator still receives the global API guard.
    app.add_url_rule("/api/test-write-guard", "test_write_guard", lambda: ({"success": True}, 200), methods=["POST"])
    client = app.test_client()
    response = client.post("/api/test-write-guard", json={"value": "no-token"})
    assert response.status_code == 403
    assert response.get_json()["success"] is False


def test_global_api_rate_limit_includes_retry_after(tmp_path):
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key-that-is-long-enough-for-test-only",
        "APP_ENV": "test",
        "API_READ_RATE_LIMIT": 2,
        "DATABASE_PATH": str(tmp_path / "rate.db"),
        "UPLOAD_DIR": str(tmp_path / "uploads"),
        "MODEL_DIR": str(tmp_path / "models"),
    })
    client = app.test_client()
    assert client.get("/api/session").status_code == 200
    assert client.get("/api/session").status_code == 200
    blocked = client.get("/api/session")
    assert blocked.status_code == 429
    assert int(blocked.headers["Retry-After"]) >= 1


def test_sensitive_response_headers_are_present(tmp_path):
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key-that-is-long-enough-for-test-only",
        "APP_ENV": "test",
        "DATABASE_PATH": str(tmp_path / "headers.db"),
        "UPLOAD_DIR": str(tmp_path / "uploads"),
        "MODEL_DIR": str(tmp_path / "models"),
    })
    response = app.test_client().get("/api/session")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert "object-src 'none'" in response.headers.get("Content-Security-Policy", "")
    assert response.headers.get("Cache-Control") == "no-store"


def test_global_api_guard_rejects_oversized_json_and_query(tmp_path):
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key-that-is-long-enough-for-test-only",
        "APP_ENV": "test",
        "MAX_JSON_BODY_BYTES": 1024,
        "MAX_QUERY_BYTES": 256,
        "DATABASE_PATH": str(tmp_path / "sizes.db"),
        "UPLOAD_DIR": str(tmp_path / "uploads"),
        "MODEL_DIR": str(tmp_path / "models"),
    })
    client = app.test_client()
    token = client.get("/api/session").get_json()["csrf_token"]
    too_large = client.post("/api/test-large-json", json={"value": "x" * 1500}, headers={"X-CSRF-Token": token})
    assert too_large.status_code == 413
    long_query = client.get("/api/session?x=" + ("a" * 300))
    assert long_query.status_code == 414


def test_in_memory_limiter_is_bounded_and_returns_retry_after():
    from rythu_mitra_backend.security import InMemoryRateLimiter

    limiter = InMemoryRateLimiter(max_keys=2)
    assert limiter.hit("ip:test", 2, 60) is None
    assert limiter.hit("ip:test", 2, 60) is None
    retry = limiter.hit("ip:test", 2, 60)
    assert retry is not None and retry >= 1
    limiter.hit("ip:another", 1, 60)
    limiter.hit("ip:third", 1, 60)
    assert len(limiter.buckets) <= 2


def test_production_requires_shared_rate_limit_store(tmp_path):
    import pytest

    with pytest.raises(RuntimeError, match="REDIS_URL"):
        create_app({
            "TESTING": True,
            "APP_ENV": "production",
            "SECRET_KEY": "test-production-key-that-is-long-enough-for-testing",
            "SECRET_KEY_CONFIGURED": True,
            "REDIS_URL": "",
            "DATABASE_PATH": str(tmp_path / "production.db"),
            "UPLOAD_DIR": str(tmp_path / "uploads"),
            "MODEL_DIR": str(tmp_path / "models"),
        })
