#!/usr/bin/env python3
"""Static consistency checks; these do not replace integration/browser tests."""
from pathlib import Path
import json, re, ast
ROOT=Path(__file__).resolve().parents[1]
js=(ROOT/"static/js/rythu-mitra-app.js").read_text(encoding="utf-8")
html=(ROOT/"templates/rythu_mitra.html").read_text(encoding="utf-8")
config=json.loads((ROOT/"static/data/resource-config.json").read_text(encoding="utf-8"))
for lang in ("en","te"): json.loads((ROOT/f"static/locales/{lang}.json").read_text(encoding="utf-8"))
assert len(config)>=60, f"Expected the backend resource schema list, got {len(config)}"
for required in ("/api/session","/api/dashboard","/api/weather","/api/recommendations","/api/disease-scan","/api/scan-history","/api/seed/scans","/api/seed/complaints","/api/markets","/api/offline/sync"):
    assert required in js, f"Missing required API client route: {required}"
assert "X-CSRF-Token" in js and "credentials: 'same-origin'" in js
assert "dealer_refused_bill" in js, "Seed complaint enum must match backend allowlist"
assert "dealer_no_bill" not in js, "Unsupported seed complaint enum remains"
en_locale = json.loads((ROOT / "static/locales/en.json").read_text(encoding="utf-8"))
assert "status.LATEST_REPORTED" in en_locale, "Market latest-reported status label missing from English locale"
market_service = (ROOT / "rythu_mitra_backend/services/markets.py").read_text(encoding="utf-8")
assert "api.data.gov.in/resource" in market_service and "DATA_GOV_IN_API_KEY" in market_service, "Official market provider wiring missing"
assert "rythu-mitra-app.js" in html and "resource-config.json" in html
print(f"PASS: resource schemas={len(config)}, fields={sum(len(x['fields']) for x in config.values())}, locales=en/te, core API markers, CSRF and seed enum.")
