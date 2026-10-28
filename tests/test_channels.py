from __future__ import annotations


def _post(client, path, payload, *, csrf=True):
    token = client.get("/api/session").get_json()["csrf_token"]
    headers = {"X-CSRF-Token": token} if csrf else {}
    return client.post(path, json=payload, headers=headers)


def test_demo_chat_menu_is_bilingual_and_marked_demo(client):
    en = _post(client, "/api/channels/demo-chat", {"message": "hello", "language": "en"})
    te = _post(client, "/api/channels/demo-chat", {"message": "నమస్కారం", "language": "te"})
    assert en.status_code == 200
    assert en.get_json()["demo"] is True
    assert "DEMO" in en.get_json()["answer"]
    assert "వాతావరణం" in te.get_json()["answer"]


def test_crop_help_does_not_claim_unverified_disease_diagnosis(client):
    response = _post(client, "/api/channels/demo-chat", {"message": "2", "language": "en"})
    body = response.get_json()
    assert response.status_code == 200
    assert body["requires_human"] is True
    assert "verified class labels" in body["answer"]
    assert body["status"] == "DEMO"


def test_market_reply_never_invents_a_price(client):
    response = _post(client, "/api/channels/demo-chat", {"message": "3", "language": "en"})
    body = response.get_json()
    assert response.status_code == 200
    assert body["status"] == "UNAVAILABLE"
    assert "not invent prices" in body["answer"]


def test_ivr_demo_is_explicitly_simulated(client):
    response = _post(client, "/api/channels/ivr/demo", {"digits": "5", "language": "en"})
    body = response.get_json()
    assert response.status_code == 200
    assert body["channel"] == "ivr-demo"
    assert body["input_mode"] == "DTMF-demo"
    assert "no call was placed" in body["note"]
    assert body["requires_human"] is True


def test_channel_routes_validate_inputs_and_csrf(client):
    invalid_message = _post(client, "/api/channels/demo-chat", {"message": ""})
    invalid_language = _post(client, "/api/channels/demo-chat", {"message": "hello", "language": "hi"})
    missing_csrf = _post(client, "/api/channels/demo-chat", {"message": "hello"}, csrf=False)
    assert invalid_message.status_code == 400
    assert invalid_language.status_code == 400
    assert missing_csrf.status_code == 403


def test_weather_without_key_is_unavailable_not_fake_live_data(client):
    response = _post(client, "/api/channels/demo-chat", {"message": "weather Hyderabad", "language": "en"})
    body = response.get_json()
    assert response.status_code == 200
    assert body["status"] == "UNAVAILABLE"
    assert "not configured" in body["answer"]
