"""Rythu Mitra: a secure, demonstrable farmer decision-support prototype."""
from __future__ import annotations

import hmac
import io
import json
import os
import pickle
import secrets
import sqlite3
import time
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any

import numpy as np
import requests
from flask import Flask, Response, jsonify, render_template, request, session
from werkzeug.exceptions import HTTPException
from PIL import Image, UnidentifiedImageError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

ROOT = Path(__file__).resolve().parent
DATA_DIR, UPLOAD_DIR = ROOT / "data", ROOT / "uploads"
DB_PATH = DATA_DIR / "rythu_mitra.db"
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
RATE_BUCKETS: dict[str, list[float]] = {}
WEATHER_CACHE: dict[str, tuple[float, dict[str, Any]]] = {}
MODEL: Any | None = None
DISEASE_MODEL: Any | None = None

CROP_CATALOG = {
    "paddy": {"water_requirement": "High; maintain field water only as locally advised.", "duration_days": "110–150", "risk": "Water availability and pest pressure", "estimated_cost": "Demo reference: ₹35,000–₹55,000/acre"},
    "cotton": {"water_requirement": "Moderate; avoid waterlogging.", "duration_days": "150–180", "risk": "Pest pressure and rain during flowering", "estimated_cost": "Demo reference: ₹28,000–₹45,000/acre"},
    "maize": {"water_requirement": "Moderate; critical around flowering.", "duration_days": "90–120", "risk": "Moisture stress and fall armyworm", "estimated_cost": "Demo reference: ₹20,000–₹32,000/acre"},
    "chilli": {"water_requirement": "Regular, well-drained irrigation.", "duration_days": "150–210", "risk": "Disease and price volatility", "estimated_cost": "Demo reference: ₹55,000–₹95,000/acre"},
    "tomato": {"water_requirement": "Regular irrigation; avoid standing water.", "duration_days": "90–140", "risk": "Disease and price volatility", "estimated_cost": "Demo reference: ₹45,000–₹80,000/acre"},
}


def load_dotenv() -> None:
    """Small dependency-free .env loader; environment values always win."""
    path = ROOT / ".env"
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw and not raw.lstrip().startswith("#") and "=" in raw:
            key, value = raw.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_dotenv()
app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.getenv("SECRET_KEY") or secrets.token_urlsafe(32),
    MAX_CONTENT_LENGTH=MAX_UPLOAD_BYTES,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=True,
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def db() -> sqlite3.Connection:
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, phone TEXT UNIQUE,
 role TEXT NOT NULL CHECK(role IN ('farmer','expert','admin','buyer')), password_hash TEXT NOT NULL,
 language TEXT NOT NULL DEFAULT 'en', district TEXT, mandal TEXT, village TEXT, land_area REAL,
 soil_type TEXT, irrigation TEXT, current_crop TEXT, crop_stage TEXT, previous_crop TEXT, season TEXT,
 experience INTEGER, budget REAL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY, kind TEXT NOT NULL, owner_id INTEGER,
 title TEXT NOT NULL, payload TEXT NOT NULL, status TEXT DEFAULT 'Active', source TEXT DEFAULT 'Demo data',
 source_url TEXT, data_type TEXT DEFAULT 'demo', last_updated TEXT NOT NULL, created_at TEXT NOT NULL,
 FOREIGN KEY(owner_id) REFERENCES users(id));
CREATE TABLE IF NOT EXISTS notifications (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, title TEXT NOT NULL,
 body TEXT NOT NULL, severity TEXT DEFAULT 'info', read_at TEXT, created_at TEXT NOT NULL,
 FOREIGN KEY(user_id) REFERENCES users(id));
CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, user_id INTEGER, action TEXT NOT NULL,
 target TEXT, created_at TEXT NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id));
"""

DEMO_RECORDS = {
    "market": [
        ("Warangal Cotton Market", {"crop": "Cotton", "market": "Warangal", "min_price": 6500, "modal_price": 7100, "max_price": 7350, "arrival_qty": "120 q", "distance_km": 18, "transport_per_km": 8, "date": "2026-08-15"}),
        ("Khammam Chilli Market", {"crop": "Chilli", "market": "Khammam", "min_price": 9800, "modal_price": 11200, "max_price": 12400, "arrival_qty": "75 q", "distance_km": 42, "transport_per_km": 8, "date": "2026-08-15"}),
        ("Nizamabad Maize Market", {"crop": "Maize", "market": "Nizamabad", "min_price": 1900, "modal_price": 2120, "max_price": 2250, "arrival_qty": "190 q", "distance_km": 34, "transport_per_km": 7, "date": "2026-08-15"}),
    ],
    "scheme": [
        ("PM-KISAN", {"description": "Income-support scheme; verify current eligibility and enrolment.", "eligibility": "Eligible landholding farmer families, subject to official rules.", "documents": ["Aadhaar", "bank details", "land details"], "url": "https://pmkisan.gov.in/"}),
        ("Soil Health Card", {"description": "Soil-testing and nutrient-management service.", "eligibility": "Check with local agriculture office.", "documents": ["Land details", "soil sample"], "url": "https://soilhealth.dac.gov.in/"}),
        ("Kisan Credit Card", {"description": "Credit facility through participating financial institutions.", "eligibility": "Check bank and official programme requirements.", "documents": ["Identity", "land/cultivation documents"], "url": "https://www.myscheme.gov.in/"}),
    ],
    "equipment": [("Tractor with rotavator", {"type": "tractor", "provider": "Warangal Agri Services", "location": "Warangal", "price": 1400, "unit": "day", "available": True, "verified": False}), ("Battery sprayer", {"type": "sprayer", "provider": "Green Field Rentals", "location": "Hanamkonda", "price": 350, "unit": "day", "available": True, "verified": False})],
    "storage": [("Warangal Dry Warehouse", {"type": "warehouse", "location": "Warangal", "capacity": "500 MT", "cost_per_quintal_day": 2.5, "crops": ["Paddy", "Maize", "Cotton"], "availability": "Demo availability"}), ("Khammam Cold Storage", {"type": "cold storage", "location": "Khammam", "capacity": "120 MT", "cost_per_quintal_day": 5, "crops": ["Tomato", "Chilli"], "availability": "Demo availability"})],
    "buyer": [("Telangana Cotton FPO request", {"crop": "Cotton", "quantity": 50, "quality": "FAQ grade", "target_price": 7050, "location": "Warangal", "contact_method": "Request through platform", "verified": False})],
    "expert_question": [("Leaf spots in cotton after rain", {"crop": "Cotton", "category": "Disease", "question": "What should I inspect after continuous rain?", "answer": "Check leaf undersides and affected area. Use a local expert for diagnosis before treatment.", "expert": "Demo Agriculture Advisor", "verified": False, "helpful": 0})],
    "disease_knowledge": [("General leaf-spot guidance", {"symptoms": "Spots, yellowing, wilting, or unusual growth.", "guidance": "Isolate observations, photograph symptoms, and confirm locally before applying any treatment."})],
}


def init_db() -> None:
    with db() as conn:
        conn.executescript(SCHEMA)
        if not conn.execute("SELECT 1 FROM users WHERE phone='9999999999'").fetchone():
            stamp = now()
            conn.executemany("INSERT INTO users(name,phone,role,password_hash,district,current_crop,crop_stage,soil_type,irrigation,land_area,season,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", [
                ("Demo Farmer", "9999999999", "farmer", generate_password_hash("demo-farmer"), "Warangal", "Cotton", "Flowering", "Black soil", "Borewell", 2.0, "Kharif", stamp, stamp),
                ("Demo Expert", "8888888888", "expert", generate_password_hash("demo-expert"), "Warangal", None, None, None, None, None, None, stamp, stamp),
                ("Demo Admin", "7777777777", "admin", generate_password_hash("demo-admin"), "Warangal", None, None, None, None, None, None, stamp, stamp),
            ])
        if not conn.execute("SELECT 1 FROM users WHERE phone='6666666666'").fetchone():
            stamp = now()
            conn.execute("INSERT INTO users(name,phone,role,password_hash,district,created_at,updated_at) VALUES(?,?,?,?,?,?,?)", ("Demo Buyer", "6666666666", "buyer", generate_password_hash("demo-buyer"), "Warangal", stamp, stamp))
        if not conn.execute("SELECT 1 FROM records").fetchone():
            stamp = now()
            for kind, entries in DEMO_RECORDS.items():
                for title, payload in entries:
                    conn.execute("INSERT INTO records(kind,title,payload,source,source_url,data_type,last_updated,created_at) VALUES(?,?,?,?,?,?,?,?)", (kind, title, json.dumps(payload), "Curated demo data", None, "demo", stamp, stamp))


def row_record(row: sqlite3.Row) -> dict[str, Any]:
    d = dict(row); d["payload"] = json.loads(d["payload"]); return d


def safe_record(row: sqlite3.Row, viewer: sqlite3.Row | None) -> dict[str, Any]:
    record = row_record(row)
    private_kinds = {"booking", "disaster", "feedback", "expert_question"}
    is_owner = viewer is not None and record["owner_id"] == viewer["id"]
    is_admin = viewer is not None and viewer["role"] == "admin"
    if record["kind"] in private_kinds and record["data_type"] == "user" and not (is_owner or is_admin or (record["kind"] == "expert_question" and viewer and viewer["role"] == "expert")):
        return {}
    record.pop("owner_id", None)
    return record


def current_user() -> sqlite3.Row | None:
    uid = session.get("user_id")
    if not uid: return None
    with db() as conn: return conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()


def api_error(message: str, status: int = 400) -> tuple[Response, int]:
    return jsonify(success=False, error=message), status


def require_auth(roles: tuple[str, ...] = ()):
    def deco(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            user = current_user()
            if not user: return api_error("Please sign in to continue.", 401)
            if roles and user["role"] not in roles: return api_error("You are not authorized for this action.", 403)
            return fn(*args, **kwargs)
        return wrapped
    return deco


def csrf_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        token = request.headers.get("X-CSRF-Token") or (request.get_json(silent=True) or {}).get("csrf_token")
        expected = session.get("csrf_token", "")
        if not token or not expected or not hmac.compare_digest(str(token), str(expected)):
            return api_error("Invalid request token.", 403)
        return fn(*args, **kwargs)
    return wrapped


def rate_limit(limit: int, window: int = 60):
    def deco(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            key = f"{request.remote_addr}:{fn.__name__}"; cutoff = time.monotonic() - window
            bucket = [t for t in RATE_BUCKETS.get(key, []) if t > cutoff]
            if len(bucket) >= limit: return api_error("Too many requests. Please try again shortly.", 429)
            bucket.append(time.monotonic()); RATE_BUCKETS[key] = bucket
            return fn(*args, **kwargs)
        return wrapped
    return deco


def payload(required: dict[str, tuple[type, float, float]]) -> dict[str, Any]:
    data = request.get_json(silent=True)
    if not isinstance(data, dict): raise ValueError("Send a JSON object.")
    clean = {}
    for field, (kind, low, high) in required.items():
        value = data.get(field)
        if value is None or isinstance(value, bool): raise ValueError(f"{field} is required.")
        try: value = kind(value)
        except (TypeError, ValueError): raise ValueError(f"{field} must be a valid number.")
        if not low <= value <= high: raise ValueError(f"{field} must be between {low} and {high}.")
        clean[field] = value
    return clean


def fertilizer_advice(n: float, p: float, k: float) -> list[str]:
    tips = []
    if n < 50: tips.append("Nitrogen is low. Discuss compost or a suitable nitrogen plan with a local advisor.")
    elif n > 100: tips.append("Nitrogen is high. Avoid adding extra nitrogen without local advice.")
    if p < 40: tips.append("Phosphorus is low. Consult your Soil Health Card before choosing a phosphorus source.")
    if k < 40: tips.append("Potassium is low. Consult a local advisor before selecting a potassium source.")
    return tips or ["Nutrients appear balanced for this simple reference check. Maintain soil organic matter and verify with a Soil Health Card."]


def crop_model() -> Any:
    global MODEL
    if MODEL is None:
        with (ROOT / "crop_model.pkl").open("rb") as f: MODEL = pickle.load(f)
    return MODEL


def disease_model() -> Any:
    global DISEASE_MODEL
    if DISEASE_MODEL is None:
        from tensorflow.keras.models import load_model
        DISEASE_MODEL = load_model(ROOT / "plant_disease_model.h5", compile=False)
    return DISEASE_MODEL


def disease_label(index: int) -> str:
    """Only use a label file supplied from a verified model source; never infer one."""
    mapping_file = DATA_DIR / "disease_labels.json"
    if mapping_file.exists():
        try:
            labels = json.loads(mapping_file.read_text(encoding="utf-8"))
            if isinstance(labels, list) and len(labels) > index and isinstance(labels[index], str) and labels[index].strip():
                return labels[index].strip()
        except (OSError, ValueError):
            pass
    return f"Model class {index + 1}"


def cached_weather(city: str) -> dict[str, Any] | None:
    entry = WEATHER_CACHE.get(city.lower())
    if entry and time.monotonic() - entry[0] < 600:
        result = dict(entry[1]); result["status"] = "CACHED"; result["is_current"] = False
        result["source"] = f"{result['source']} (cached)"; result["reason"] = "Last successful weather response; refresh when online."
        return result
    return None


def weather_for(city: str) -> dict[str, Any]:
    key = os.getenv("OPENWEATHER_API_KEY", "").strip()
    if not key:
        return {"success": True, "status": "DEMO", "source": "Demo weather — replace with live source", "last_updated": now(), "temperature": 28, "humidity": 72, "rainfall": 12, "rain_probability": 55, "wind": 14, "advisories": ["Demo forecast: rain may occur. Consider delaying spraying.", "Humidity is elevated; inspect leaves for fungal symptoms."], "reason": "No OpenWeather key is configured."}
    cached = cached_weather(city)
    if cached:
        return cached
    try:
        response = requests.get("https://api.openweathermap.org/data/2.5/weather", params={"q": city, "appid": key, "units": "metric"}, timeout=8)
        if response.status_code == 401: return {"success": False, "error": "Weather service is not configured."}
        if response.status_code == 404: return {"success": False, "error": "Location not found."}
        if response.status_code == 429: return {"success": False, "error": "Weather service is temporarily rate-limited."}
        response.raise_for_status(); data = response.json(); main = data.get("main") or {}
        if "temp" not in main or "humidity" not in main: raise ValueError("Missing weather fields")
        wind = round((data.get("wind") or {}).get("speed", 0) * 3.6); rain = round((data.get("rain") or {}).get("1h", 0), 1)
        forecast: list[dict[str, Any]] = []
        rain_probability = None
        try:
            forecast_response = requests.get("https://api.openweathermap.org/data/2.5/forecast", params={"q": city, "appid": key, "units": "metric", "cnt": 8}, timeout=8)
            if forecast_response.status_code == 200:
                for item in (forecast_response.json().get("list") or [])[:8]:
                    item_main = item.get("main") or {}; pop = item.get("pop")
                    if not isinstance(pop, (int, float)) or "temp" not in item_main: continue
                    forecast.append({"time": item.get("dt_txt", "Forecast"), "temperature": item_main["temp"], "rain_probability": round(pop * 100), "rainfall": (item.get("rain") or {}).get("3h", 0)})
                if forecast: rain_probability = max(item["rain_probability"] for item in forecast)
        except (requests.RequestException, ValueError, TypeError):
            pass
        advises = []
        if wind > 25: advises.append("Strong wind: avoid spraying until wind eases.")
        if main["humidity"] >= 80: advises.append("High humidity: inspect your crop for fungal symptoms.")
        if rain > 5: advises.append("Recent rain: check drainage and consider delaying spraying.")
        if rain_probability and rain_probability >= 60: advises.append("Rain is likely in the next 24 hours: consider delaying spraying.")
        result = {"success": True, "status": "LIVE", "is_current": True, "source": "OpenWeather", "last_updated": now(), "temperature": main["temp"], "humidity": main["humidity"], "rainfall": rain, "rain_probability": rain_probability, "wind": wind, "forecast": forecast, "advisories": advises or ["No urgent weather advisory from current conditions."], "reason": "Current weather conditions."}
        WEATHER_CACHE[city.lower()] = (time.monotonic(), result)
        return result
    except requests.Timeout: return {"success": False, "error": "Weather service timed out. Please retry."}
    except (requests.RequestException, ValueError, TypeError): return {"success": False, "error": "Weather service is unavailable. Please retry later."}


@app.before_request
def ensure_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    session.permanent = True


@app.after_request
def security_headers(response: Response) -> Response:
    response.headers["X-Content-Type-Options"] = "nosniff"; response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; img-src 'self' data:; connect-src 'self'; base-uri 'self'; frame-ancestors 'none'"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(self), camera=(self)"
    return response


@app.errorhandler(413)
def too_large(_): return api_error("Image exceeds the 5 MB limit.", 413)


@app.errorhandler(Exception)
def unexpected(error):
    if isinstance(error, HTTPException):
        return error
    app.logger.exception("Unhandled request error: %s", type(error).__name__)
    return api_error("Something went wrong. Please try again.", 500)


@app.get("/")
def home():
    return render_template("index.html", csrf_token=session["csrf_token"])


@app.get("/api/session")
def api_session():
    user = current_user()
    return jsonify(success=True, user=dict(user) if user else None, csrf_token=session.get("csrf_token"))


@app.post("/api/login")
@csrf_required
@rate_limit(8)
def login():
    data = request.get_json(silent=True) or {}; phone = str(data.get("phone", "")).strip(); password = str(data.get("password", ""))
    if not phone.isdigit() or not 8 <= len(phone) <= 15 or not password: return api_error("Enter a valid phone number and password.")
    with db() as conn: user = conn.execute("SELECT * FROM users WHERE phone=?", (phone,)).fetchone()
    if not user or not check_password_hash(user["password_hash"], password): return api_error("Invalid sign-in details.", 401)
    session.clear(); session["user_id"] = user["id"]; session["csrf_token"] = secrets.token_urlsafe(32)
    return jsonify(success=True, user=dict(user), csrf_token=session["csrf_token"])


@app.post("/api/logout")
@csrf_required
def logout():
    session.clear()
    session["csrf_token"] = secrets.token_urlsafe(32)
    return jsonify(success=True, csrf_token=session["csrf_token"])


@app.get("/api/weather")
@rate_limit(30)
def weather():
    city = request.args.get("city", "Hyderabad").strip()
    if not city or len(city) > 80 or any(c in city for c in "<>;{}"): return api_error("Enter a valid location.")
    result = weather_for(city); return jsonify(result), (200 if result.get("success") else 503)


@app.post("/api/recommendations")
@csrf_required
@rate_limit(20)
def recommend():
    try: x = payload({"N":(float,0,300),"P":(float,0,300),"K":(float,0,300),"temperature":(float,-5,60),"humidity":(float,0,100),"ph":(float,0,14),"rainfall":(float,0,1000)})
    except ValueError as e: return api_error(str(e))
    try: crop = str(crop_model().predict(np.array([[x[k] for k in ("N","P","K","temperature","humidity","ph","rainfall")]]))[0])
    except Exception: return api_error("Crop recommendation model is unavailable.", 503)
    score = max(35, min(95, round(80 - abs(x["ph"]-6.5)*7 - max(0, x["temperature"]-35)*2)))
    plan = CROP_CATALOG.get(crop.lower(), {"water_requirement": "Confirm water need with a local agriculture professional.", "duration_days": "Varies by local variety", "risk": "Weather, pest, and market conditions", "estimated_cost": "No verified estimate available."})
    return jsonify(success=True, crop=crop.title(), suitability_score=score, fertilizer_advice=fertilizer_advice(x["N"],x["P"],x["K"]), plan=plan, reasoning="Suitability combines the supplied crop-model result with a transparent pH/temperature reference score.", disclaimer="Model-based recommendation; costs and duration are curated demo references. Confirm suitability, costs, water, and local conditions before planting.")


@app.post("/api/yield-estimate")
@csrf_required
def yield_estimate():
    try: x = payload({"rainfall":(float,0,1000),"ph":(float,0,14),"temperature":(float,-5,60)})
    except ValueError as e: return api_error(str(e))
    score = 100 - (15 if not 5.5 <= x["ph"] <= 7.5 else 0) - (15 if not 20 <= x["temperature"] <= 30 else 0) - (20 if x["rainfall"] < 50 else 10 if x["rainfall"] > 250 else 0)
    return jsonify(success=True, estimated_yield_percent=max(score,40), note="Reference favorability score only; this is not a trained yield or profit model.")


@app.post("/api/disease-scan")
@csrf_required
@rate_limit(10)
def disease_scan():
    file = request.files.get("image")
    if not file or not file.filename: return api_error("Choose a crop image.")
    if file.mimetype not in ALLOWED_IMAGE_TYPES: return api_error("Use a JPEG, PNG, or WebP image.")
    raw = file.read(MAX_UPLOAD_BYTES + 1)
    if len(raw) > MAX_UPLOAD_BYTES: return api_error("Image exceeds the 5 MB limit.", 413)
    try:
        image = Image.open(io.BytesIO(raw)); image.verify(); image = Image.open(io.BytesIO(raw)).convert("RGB")
    except (UnidentifiedImageError, OSError): return api_error("The uploaded file is not a valid image.")
    try:
        size = disease_model().input_shape[1:3]; resized = image.resize((size[1], size[0])); pred = np.asarray(disease_model().predict(np.expand_dims(np.asarray(resized, dtype=np.float32)/255.0, 0), verbose=0))[0]
        idx, confidence = int(np.argmax(pred)), float(np.max(pred))
    except Exception: return api_error("Disease model is currently unavailable.", 503)
    UPLOAD_DIR.mkdir(exist_ok=True); filename = f"{secrets.token_hex(12)}_{secure_filename(file.filename)}"; Image.open(io.BytesIO(raw)).convert("RGB").save(UPLOAD_DIR / filename, "JPEG", quality=85)
    label = disease_label(idx)
    return jsonify(success=True, result=label, label_verified=not label.startswith("Model class "), confidence=round(confidence*100,1), low_confidence=confidence < .65, image_id=filename, guidance="AI/model-based preliminary result. Confirm with an agriculture professional before applying treatments.", symptoms="Compare visible symptoms with a verified local diagnosis; no disease name is shown until a verified model class-label mapping is supplied.")


@app.get("/api/records/<kind>")
def list_records(kind: str):
    allowed = set(DEMO_RECORDS) | {"booking", "listing", "buyer_request", "disaster", "feedback"}
    if kind not in allowed: return api_error("Unknown resource.", 404)
    term = request.args.get("q", "").strip().lower()
    viewer = current_user()
    with db() as conn: rows = [safe_record(r, viewer) for r in conn.execute("SELECT * FROM records WHERE kind=? ORDER BY id DESC", (kind,))]
    rows = [r for r in rows if r]
    if term: rows = [r for r in rows if term in (r["title"] + json.dumps(r["payload"])).lower()]
    if kind == "market" and request.args.get("sort") in {"modal_price", "distance_km"}:
        key = request.args["sort"]; rows.sort(key=lambda r: float(r["payload"].get(key, float("inf"))))
    return jsonify(success=True, records=rows, status="DEMO" if all(r["data_type"] == "demo" for r in rows) else "MIXED")


@app.post("/api/records/<kind>")
@csrf_required
@require_auth()
@rate_limit(12)
def create_record(kind: str):
    permissions = {"listing": ("farmer",), "buyer_request": ("buyer",), "booking": ("farmer",), "disaster": ("farmer",), "expert_question": ("farmer",), "feedback": ("farmer","expert","buyer")}
    user = current_user()
    if kind not in permissions or user["role"] not in permissions[kind]: return api_error("You are not authorized for this submission.", 403)
    data = request.get_json(silent=True) or {}; title = str(data.get("title", "")).strip()
    if not 3 <= len(title) <= 120: return api_error("Title must be 3–120 characters.")
    clean = {str(k)[:40]: str(v)[:500] for k,v in data.items() if k not in {"csrf_token", "title"}}
    stamp = now()
    with db() as conn:
        conn.execute("INSERT INTO records(kind,owner_id,title,payload,status,source,data_type,last_updated,created_at) VALUES(?,?,?,?,?,?,?,?,?)", (kind,user["id"],title,json.dumps(clean),"Submitted","User submission","user",stamp,stamp)); conn.execute("INSERT INTO audit_logs(user_id,action,target,created_at) VALUES(?,?,?,?)", (user["id"],"create",kind,stamp))
    return jsonify(success=True, message="Submitted for review; no external notification was sent."), 201


@app.patch("/api/records/<int:record_id>")
@csrf_required
@require_auth()
def update_own_record(record_id: int):
    user = current_user(); data = request.get_json(silent=True) or {}; requested = str(data.get("status", "")).strip()
    allowed = {"booking": {"Submitted", "Cancelled"}, "listing": {"Submitted", "Closed"}, "buyer_request": {"Submitted", "Closed"}, "disaster": {"Draft", "Submitted"}}
    with db() as conn:
        record = conn.execute("SELECT * FROM records WHERE id=?", (record_id,)).fetchone()
        if not record: return api_error("Record not found.", 404)
        if record["owner_id"] != user["id"]: return api_error("You cannot change this record.", 403)
        if requested not in allowed.get(record["kind"], set()): return api_error("Invalid status change.")
        conn.execute("UPDATE records SET status=?, last_updated=? WHERE id=?", (requested, now(), record_id))
    return jsonify(success=True, message="Status updated.")


@app.patch("/api/admin/records/<int:record_id>")
@csrf_required
@require_auth(("admin",))
def moderate_record(record_id: int):
    data = request.get_json(silent=True) or {}; status = str(data.get("status", "")).strip()
    if status not in {"Under Review", "Approved", "Suspended", "Blocked", "Closed"}: return api_error("Invalid moderation status.")
    with db() as conn:
        if not conn.execute("SELECT 1 FROM records WHERE id=?", (record_id,)).fetchone(): return api_error("Record not found.", 404)
        conn.execute("UPDATE records SET status=?, last_updated=? WHERE id=?", (status, now(), record_id)); conn.execute("INSERT INTO audit_logs(user_id,action,target,created_at) VALUES(?,?,?,?)", (current_user()["id"], "moderate", str(record_id), now()))
    return jsonify(success=True, message="Record moderated.")


@app.post("/api/market-net-income")
@csrf_required
def market_income():
    try: x = payload({"quantity":(float,.1,100000),"price":(float,1,100000),"transport":(float,0,100000),"charges":(float,0,100000)})
    except ValueError as e: return api_error(str(e))
    return jsonify(success=True, expected_selling_value=round(x["quantity"]*x["price"],2), estimated_net_income=round(x["quantity"]*x["price"]-x["transport"]-x["charges"],2), disclaimer="Estimate only; prices, quality, charges, and transport may change.")


@app.post("/api/storage-calculation")
@csrf_required
def storage_calculation():
    try: x = payload({"quantity": (float, .1, 100000), "days": (float, 1, 365), "cost_per_quintal_day": (float, 0, 10000), "sell_now_price": (float, 1, 100000), "future_price": (float, 1, 100000), "transport": (float, 0, 100000)})
    except ValueError as e: return api_error(str(e))
    storage_cost = round(x["quantity"] * x["days"] * x["cost_per_quintal_day"], 2)
    sell_now = round(x["quantity"] * x["sell_now_price"] - x["transport"], 2)
    store_then_sell = round(x["quantity"] * x["future_price"] - x["transport"] - storage_cost, 2)
    return jsonify(success=True, storage_cost=storage_cost, sell_now= sell_now, store_then_sell=store_then_sell, difference=round(store_then_sell-sell_now,2), disclaimer="Reference calculation only. It does not predict prices or guarantee a benefit from storage.")


@app.get("/api/schemes/matches")
@require_auth()
def scheme_matches():
    user = current_user(); profile_complete = bool(user["district"] and user["land_area"] and user["current_crop"])
    with db() as conn: rows = conn.execute("SELECT * FROM records WHERE kind='scheme' ORDER BY title").fetchall()
    matches = []
    for row in rows:
        item = safe_record(row, user); item["match_status"] = "Likely eligible" if profile_complete and item["title"] in {"PM-KISAN", "Soil Health Card"} else "Needs more information"
        item["eligibility_note"] = "Check official eligibility; this prototype does not determine eligibility."
        matches.append(item)
    return jsonify(success=True, profile_complete=profile_complete, matches=matches)


@app.get("/api/dashboard")
@require_auth()
def dashboard():
    user = current_user(); weather = weather_for(user["district"] or "Hyderabad")
    with db() as conn:
        notices = [dict(r) for r in conn.execute("SELECT * FROM notifications WHERE user_id=? ORDER BY id DESC LIMIT 5", (user["id"],))]
        market = conn.execute("SELECT * FROM records WHERE kind='market' LIMIT 1").fetchone()
    stage = (user["crop_stage"] or "growing").lower()
    actions = [f"Inspect leaves and pests during {stage}.", "Review the next crop-calendar task."] + (weather.get("advisories", [])[:1] if weather.get("success") else [])
    tasks = [{"task":"Pest inspection","due":"Today","status":"Due","reason":"Crop stage monitoring"}, {"task":"Irrigation check","due":"Tomorrow","status":"Upcoming","reason":"Water planning"}, {"task":"Record field observation","due":"Overdue","status":"Overdue","reason":"Farm record"}, {"task":"Review storage plan","due":"After harvest","status":"Completed","reason":"Reference task"}]
    return jsonify(success=True, profile={k:user[k] for k in ("name","district","current_crop","crop_stage","language","land_area")}, weather=weather, actions=actions, crop_health_status="No verified diagnosis recorded", market=row_record(market) if market else None, notifications=notices, crop_calendar=tasks, schemes=2)


@app.post("/api/profile")
@csrf_required
@require_auth()
def profile():
    data = request.get_json(silent=True) or {}; allowed = {"name":120,"language":5,"district":80,"mandal":80,"village":80,"soil_type":80,"irrigation":80,"current_crop":80,"crop_stage":80,"previous_crop":80,"season":30}
    vals = {k:str(data[k]).strip()[:limit] for k,limit in allowed.items() if k in data}
    for key, low, high in (("land_area", .01, 100000), ("budget", 0, 100000000), ("experience", 0, 100)):
        if key in data:
            try: value = float(data[key])
            except (TypeError, ValueError): return api_error(f"{key} must be a valid number.")
            if not low <= value <= high: return api_error(f"{key} is outside the allowed range.")
            vals[key] = int(value) if key == "experience" else value
    if "language" in vals and vals["language"] not in {"en","te"}: return api_error("Unsupported language.")
    if not vals: return api_error("No profile updates provided.")
    vals["updated_at"] = now(); cols = ", ".join(f"{k}=?" for k in vals)
    with db() as conn: conn.execute(f"UPDATE users SET {cols} WHERE id=?", (*vals.values(), current_user()["id"]))
    return jsonify(success=True)


@app.get("/api/admin/summary")
@require_auth(("admin",))
def admin_summary():
    with db() as conn:
        counts = {kind: conn.execute("SELECT COUNT(*) FROM records WHERE kind=?", (kind,)).fetchone()[0] for kind in ("listing","booking","disaster","expert_question")}
        counts["farmers"] = conn.execute("SELECT COUNT(*) FROM users WHERE role='farmer'").fetchone()[0]
    return jsonify(success=True, counts=counts, system_status={"database":"healthy", "crop_model":"available", "disease_model":"lazy-loaded", "weather":"live" if os.getenv("OPENWEATHER_API_KEY") else "demo/unconfigured"})


@app.get("/health")
def health(): return jsonify(status="ok", database=DB_PATH.exists(), weather_configured=bool(os.getenv("OPENWEATHER_API_KEY")))


init_db()

if __name__ == "__main__": app.run(host="127.0.0.1", port=5000, debug=False)
