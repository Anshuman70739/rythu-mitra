from __future__ import annotations
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_privacy_policy_page_is_available(client):
    response = client.get("/privacy-policy")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Privacy policy" in html
    assert "does not provide" in html.lower()
    assert "/terms-and-conditions" in html


def test_terms_page_is_available(client):
    response = client.get("/terms-and-conditions")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Terms and conditions" in html
    assert "does not guarantee" in html.lower()
    assert "/privacy-policy" in html


def test_favicon_is_served(client):
    response = client.get("/static/favicon.svg")
    assert response.status_code == 200
    assert "<svg" in response.get_data(as_text=True)


def test_frontend_brand_constraints_are_kept_in_source():
    template = (PROJECT_ROOT / "templates" / "rythu_mitra.html").read_text(encoding="utf-8")
    css = "\n".join((PROJECT_ROOT / "static" / "css" / name).read_text(encoding="utf-8") for name in ("rythu-mitra.css", "rythu-mitra-motion.css", "legal.css"))
    js = (PROJECT_ROOT / "static" / "js" / "rythu-mitra-app.js").read_text(encoding="utf-8")
    locales = "\n".join((PROJECT_ROOT / "static" / "locales" / name).read_text(encoding="utf-8") for name in ("en.json", "te.json"))
    assert "favicon.svg" in template
    assert 'href="/privacy-policy"' in template
    assert 'href="/terms-and-conditions"' in template
    assert "scroll-behavior: smooth" not in css.lower()
    assert "rm-rise" not in css
    assert "rm-sweep" not in css
    assert "Made with AI" not in template + css + js + locales
    assert "Made with Al" not in template + css + js + locales
    assert "—" not in template + css + js + locales
    assert "–" not in template + css + js + locales
