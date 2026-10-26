from __future__ import annotations
import io
from conftest import register


def test_health_ready_and_session_contract(client):
    assert client.get("/health").status_code == 200
    ready = client.get("/ready")
    assert ready.status_code == 200
    session = client.get("/api/session").get_json()
    assert session["success"] is True
    assert isinstance(session["csrf_token"], str) and len(session["csrf_token"]) >= 20
    assert session["user"] is None


def test_csrf_required_for_registration(client):
    response = client.post("/api/register", json={"name":"Test","phone":"9000000001","password":"long-password"})
    assert response.status_code == 403


def test_registration_serialization_and_owner_isolation(app):
    first = app.test_client()
    csrf1, user1 = register(first, "9000000001")
    created = first.post("/api/v1/farms", json={"name":"Farm A","district":"Warangal","area_acres":2}, headers={"X-CSRF-Token":csrf1})
    assert created.status_code == 201, created.get_data(as_text=True)
    farm_id = created.get_json()["record"]["id"]
    assert "owner_id" not in created.get_json()["record"]
    second = app.test_client()
    register(second, "9000000002")
    denied = second.get(f"/api/v1/farms/{farm_id}")
    assert denied.status_code == 404
    assert first.get(f"/api/v1/farms/{farm_id}").status_code == 200


def test_client_cannot_set_owner_status_or_source(client):
    token, _ = register(client)
    response = client.post("/api/v1/farms", json={"name":"Farm A","owner_id":99}, headers={"X-CSRF-Token":token})
    assert response.status_code == 400
    assert "Protected field" in response.get_json()["error"]


def test_germination_math_and_filing_disclaimer(client):
    token, _ = register(client)
    response = client.post("/api/seed/germination", json={"tested_count":20,"germinated_count":15,"test_date":"2026-10-15"}, headers={"X-CSRF-Token":token})
    assert response.status_code == 201, response.get_data(as_text=True)
    record = response.get_json()["record"]
    assert record["germination_percentage"] == 75.0
    assert "not official laboratory certification" in record["screening_label"].lower()

    complaint = client.post("/api/seed/complaints", json={"complaint_type":"poor_germination","description":"Home germination test was below packet label."}, headers={"X-CSRF-Token":token})
    assert complaint.status_code == 201, complaint.get_data(as_text=True)
    data = complaint.get_json()
    assert data["record"]["official_filing_status"] == "NOT_FILED_BY_PLATFORM"
    assert data["official_submission"]["submitted"] is False


def test_seed_qr_is_preview_only_and_never_fetches_url(client):
    token, _ = register(client)
    response = client.post("/api/seed/qr-check", json={"qr_content":"https://example.invalid/?lot=ABC","lot_number":"XYZ"}, headers={"X-CSRF-Token":token})
    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "POSSIBLE_MISMATCH"
    assert body["trusted_official_domain"] is False
    assert "does not open/fetch" in body["warning"]


def test_net_income_calculation_is_user_entered_math(client):
    token = client.get("/api/session").get_json()["csrf_token"]
    response = client.post("/api/market-net-income", json={"quantity":100,"price":20,"transport":50,"charges":30}, headers={"X-CSRF-Token":token})
    assert response.status_code == 200
    body = response.get_json()
    assert body["estimated_net_income"] == 1920
    assert body["data_type"] == "USER_ENTERED_CALCULATION"


def test_missing_weather_key_is_unavailable_for_unmatched_location_not_fake_live_data(client, monkeypatch):
    from rythu_mitra_backend.services import weather

    class FakeResponse:
        status_code = 200
        def raise_for_status(self):
            return None
        def json(self):
            return {"results": []}

    weather._CACHE.clear()
    monkeypatch.setattr(weather.requests, "get", lambda *args, **kwargs: FakeResponse())
    response = client.get("/api/weather?city=Test-No-Key-City")
    assert response.status_code == 503
    body = response.get_json()
    assert body["status"] == "UNAVAILABLE"
    assert body["data_type"] == "UNAVAILABLE"
    assert "temperature" not in body


def test_weather_uses_open_meteo_without_a_provider_key(client, monkeypatch):
    from rythu_mitra_backend.services import weather

    class FakeResponse:
        status_code = 200
        def __init__(self, body):
            self.body = body
        def raise_for_status(self):
            return None
        def json(self):
            return self.body

    def fake_get(url, **kwargs):
        if "geocoding-api.open-meteo.com" in url:
            return FakeResponse({"results": [{
                "name": "Hyderabad", "admin1": "Telangana",
                "latitude": 17.385, "longitude": 78.4867,
            }]})
        return FakeResponse({
            "current": {
                "time": "2026-10-26T12:00", "temperature_2m": 29.2,
                "relative_humidity_2m": 50, "precipitation": 0.0, "wind_speed_10m": 5.2,
            },
            "hourly": {
                "time": ["2026-10-26T12:00", "2026-10-26T13:00"],
                "temperature_2m": [29.2, 30.0],
                "precipitation_probability": [5, 10],
                "precipitation": [0.0, 0.0],
            },
        })

    weather._CACHE.clear()
    monkeypatch.setattr(weather.requests, "get", fake_get)
    response = client.get("/api/weather?city=Hyderabad")
    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data_type"] == "MODEL_OUTPUT"
    assert body["source_name"] == "Open-Meteo (model-based weather)"
    assert body["temperature"] == 29.2
    assert body["forecast"]


def test_scheme_matches_include_official_curated_entries_for_a_new_database(client):
    register(client)
    response = client.get("/api/schemes/matches")
    assert response.status_code == 200, response.get_data(as_text=True)
    body = response.get_json()
    assert body["success"] is True
    schemes = {item["name"]: item for item in body["matches"]}
    assert "PM-KISAN Samman Nidhi" in schemes
    assert "Telangana Rythu Bharosa" in schemes
    assert "Pradhan Mantri Fasal Bima Yojana (PMFBY)" in schemes
    assert all(item["data_type"] == "CURATED" for item in schemes.values())
    assert all(item["official_url"].startswith("https://") for item in schemes.values())


def test_crop_model_missing_is_unavailable(client):
    token = client.get("/api/session").get_json()["csrf_token"]
    response = client.post("/api/recommendations", json={"N":30,"P":20,"K":20,"temperature":25,"humidity":60,"ph":6.5,"rainfall":100}, headers={"X-CSRF-Token":token})
    assert response.status_code == 503
    assert response.get_json()["status"] == "UNAVAILABLE"


def test_farmer_cannot_open_admin_endpoints(client):
    register(client)
    response = client.get("/api/admin/summary")
    assert response.status_code == 403


def test_invalid_image_is_rejected_before_model_inference(client):
    token = client.get("/api/session").get_json()["csrf_token"]
    response = client.post("/api/disease-scan", data={"image":(io.BytesIO(b"not-an-image"),"leaf.png")}, headers={"X-CSRF-Token":token}, content_type="multipart/form-data")
    assert response.status_code == 400
    assert "safe" in response.get_json()["error"].lower() or "readable" in response.get_json()["error"].lower()


def test_offline_sync_is_idempotent(client):
    token, _ = register(client)
    payload={"operations":[{"operation_id":"offline-op-0001","resource":"farm-diary","payload":{"entry_date":"2026-10-15","activity_type":"irrigation","description":"Test entry"}}]}
    first=client.post("/api/offline/sync",json=payload,headers={"X-CSRF-Token":token})
    second=client.post("/api/offline/sync",json=payload,headers={"X-CSRF-Token":token})
    assert first.status_code==200 and second.status_code==200
    assert first.get_json()["results"][0]["record"]["id"]==second.get_json()["results"][0]["record"]["id"]


class _FakeHTTPResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


def test_official_mandi_adapter_normalizes_daily_prices(app, client, monkeypatch):
    from datetime import date
    from rythu_mitra_backend.services import markets

    app.config["DATA_GOV_IN_API_KEY"] = "test-key-not-a-real-secret"
    observed = date.today().strftime("%d/%m/%Y")
    captured = {}

    def fake_get(url, params, timeout):
        captured["url"] = url
        captured["params"] = params
        captured["timeout"] = timeout
        return _FakeHTTPResponse({
            "total": "1",
            "records": [{
                "state": "Telangana", "district": "Warangal", "market": "Warangal",
                "commodity": "Paddy", "variety": "Common", "grade": "FAQ",
                "arrival_date": observed, "min_price": "2100", "modal_price": "2250", "max_price": "2400"
            }]
        })

    monkeypatch.setattr(markets.requests, "get", fake_get)
    response = client.get("/api/markets?provider=live&commodity=Paddy&district=Warangal")
    assert response.status_code == 200, response.get_data(as_text=True)
    body = response.get_json()
    assert body["success"] is True
    assert body["status"] == "LATEST_REPORTED"
    assert body["data_type"] == "LATEST_REPORTED"
    assert captured["url"].endswith(markets.DATA_GOV_IN_RESOURCE_ID)
    assert captured["params"]["api-key"] == "test-key-not-a-real-secret"
    assert captured["params"]["filters[State]"] == "Telangana"
    assert captured["params"]["filters[District]"] == "Warangal"
    assert captured["params"]["filters[Commodity]"] == "Paddy"
    record = body["records"][0]
    assert record["minimum_price"] == 2100.0
    assert record["modal_price"] == 2250.0
    assert record["maximum_price"] == 2400.0
    assert record["price_date"] == date.today().isoformat()
    assert record["is_stale"] is False
    assert "data.gov.in" in record["source_url"]
    assert "daily" in body["note"].lower()


def test_official_mandi_adapter_rejects_impossible_prices(app, client, monkeypatch):
    from datetime import date
    from rythu_mitra_backend.services import markets

    app.config["DATA_GOV_IN_API_KEY"] = "test-key-not-a-real-secret"
    observed = date.today().strftime("%d/%m/%Y")
    monkeypatch.setattr(markets.requests, "get", lambda *a, **k: _FakeHTTPResponse({"records": [{
        "state": "Telangana", "district": "Warangal", "market": "Warangal", "commodity": "Paddy",
        "arrival_date": observed, "min_price": "2500", "modal_price": "2000", "max_price": "2400"
    }]}))
    response = client.get("/api/markets?provider=live&commodity=Paddy")
    assert response.status_code == 503
    assert response.get_json()["status"] == "UNAVAILABLE"


def test_official_mandi_adapter_requires_server_side_key(app, client):
    app.config["DATA_GOV_IN_API_KEY"] = ""
    app.config["MARKET_DATA_BASE_URL"] = ""
    response = client.get("/api/markets?provider=live")
    assert response.status_code == 503
    body = response.get_json()
    assert body["status"] == "UNAVAILABLE"
    assert "DATA_GOV_IN_API_KEY" in body["error"]


def test_official_mandi_marks_old_observation_stale(app, client, monkeypatch):
    from datetime import date, timedelta
    from rythu_mitra_backend.services import markets

    app.config["DATA_GOV_IN_API_KEY"] = "test-key-not-a-real-secret"
    observed = (date.today() - timedelta(days=5)).strftime("%d/%m/%Y")
    monkeypatch.setattr(markets.requests, "get", lambda *a, **k: _FakeHTTPResponse({"records": [{
        "state": "Telangana", "district": "Warangal", "market": "Warangal", "commodity": "Paddy",
        "arrival_date": observed, "min_price": "2100", "modal_price": "2250", "max_price": "2400"
    }]}))
    response = client.get("/api/markets?provider=live&commodity=Paddy")
    assert response.status_code == 200
    record = response.get_json()["records"][0]
    assert record["is_stale"] is True
    assert record["freshness_status"] == "STALE"
    assert record["price_date"] == (date.today() - timedelta(days=5)).isoformat()


def test_official_mandi_provider_timeout_returns_unavailable(app, client, monkeypatch):
    import requests
    from rythu_mitra_backend.services import markets

    app.config["DATA_GOV_IN_API_KEY"] = "test-key-not-a-real-secret"

    def fail(*args, **kwargs):
        raise requests.Timeout("simulated provider timeout")

    monkeypatch.setattr(markets.requests, "get", fail)
    response = client.get("/api/markets?provider=live")
    assert response.status_code == 503
    body = response.get_json()
    assert body["status"] == "UNAVAILABLE"
    assert "simulated provider timeout" not in body["error"]


def test_official_mandi_malformed_rows_are_not_returned(app, client, monkeypatch):
    from datetime import date
    from rythu_mitra_backend.services import markets

    app.config["DATA_GOV_IN_API_KEY"] = "test-key-not-a-real-secret"
    monkeypatch.setattr(markets.requests, "get", lambda *a, **k: _FakeHTTPResponse({"records": [
        {"state": "Telangana", "district": "Warangal", "market": "Warangal", "commodity": "Paddy",
         "arrival_date": date.today().strftime("%d/%m/%Y"), "min_price": "not-a-number",
         "modal_price": "2250", "max_price": "2400"}
    ]}))
    response = client.get("/api/markets?provider=live&commodity=Paddy")
    assert response.status_code == 503
    assert response.get_json()["records"] == []
    assert response.get_json()["status"] == "UNAVAILABLE"
