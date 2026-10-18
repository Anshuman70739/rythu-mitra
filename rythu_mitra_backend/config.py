"""Environment-based configuration. No secrets are committed to source control."""
from __future__ import annotations
import os
import secrets
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_dotenv() -> None:
    path = PROJECT_ROOT / ".env"
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _truthy(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def _database_path() -> str:
    explicit = os.getenv("DATABASE_PATH", "").strip()
    if explicit:
        return str(Path(explicit).expanduser().resolve())
    url = os.getenv("DATABASE_URL", "sqlite:///data/rythu_mitra.db").strip()
    if url.startswith("sqlite:///"):
        path = url[len("sqlite:///"):]
        resolved = Path(path)
        if not resolved.is_absolute():
            resolved = PROJECT_ROOT / resolved
        return str(resolved.resolve())
    raise RuntimeError("This backend build supports SQLite only. Set DATABASE_URL=sqlite:///data/rythu_mitra.db.")


class Config:
    load_dotenv()
    APP_ENV = os.getenv("APP_ENV", os.getenv("FLASK_ENV", "development")).strip().lower()
    IS_PRODUCTION = APP_ENV == "production"
    DEMO_MODE = _truthy("DEMO_MODE", False) and not IS_PRODUCTION
    SECRET_KEY_CONFIGURED = bool(os.getenv("SECRET_KEY", "").strip())
    SECRET_KEY = os.getenv("SECRET_KEY", "").strip()
    if not SECRET_KEY:
        SECRET_KEY = secrets.token_urlsafe(48)
    DATABASE_PATH = _database_path()
    UPLOAD_DIR = str(Path(os.getenv("UPLOAD_DIR", str(PROJECT_ROOT / "uploads"))).expanduser().resolve())
    MODEL_DIR = str(Path(os.getenv("MODEL_DIR", str(PROJECT_ROOT / "models"))).expanduser().resolve())
    MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", "5242880"))
    if MAX_UPLOAD_BYTES < 1024:
        raise RuntimeError("MAX_UPLOAD_BYTES must be at least 1024 bytes.")
    # A packet-scan form may carry up to five separately limited images.
    MAX_REQUEST_BYTES = int(os.getenv("MAX_REQUEST_BYTES", str(MAX_UPLOAD_BYTES * 5 + 1024 * 1024)))
    if MAX_REQUEST_BYTES < MAX_UPLOAD_BYTES:
        raise RuntimeError("MAX_REQUEST_BYTES must be at least MAX_UPLOAD_BYTES.")
    MAX_CONTENT_LENGTH = MAX_REQUEST_BYTES
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = True if IS_PRODUCTION else _truthy("SESSION_COOKIE_SECURE", False)
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 12
    JSON_SORT_KEYS = False
    # Every API route has a coarse IP/account budget in addition to route-specific limits.
    API_READ_RATE_LIMIT = max(1, int(os.getenv("API_READ_RATE_LIMIT", "180")))
    API_WRITE_RATE_LIMIT = max(1, int(os.getenv("API_WRITE_RATE_LIMIT", "60")))
    MAX_JSON_BODY_BYTES = max(1024, int(os.getenv("MAX_JSON_BODY_BYTES", "1048576")))
    MAX_QUERY_BYTES = max(256, int(os.getenv("MAX_QUERY_BYTES", "4096")))
    # Production must use Redis for a shared limiter across workers/restarts.
    REDIS_URL = os.getenv("REDIS_URL", "").strip()
    # Set to the exact trusted proxy hop count for the host. Do not trust X-Forwarded-* blindly.
    TRUSTED_PROXY_HOPS = max(0, min(int(os.getenv("TRUSTED_PROXY_HOPS", "0")), 5))
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()
    # Official data.gov.in API key stays on the server; never expose it in frontend JS.
    DATA_GOV_IN_API_KEY = os.getenv("DATA_GOV_IN_API_KEY", "").strip()
    MARKET_DEFAULT_STATE = os.getenv("MARKET_DEFAULT_STATE", "Telangana").strip() or "Telangana"
    MARKET_DATA_API_KEY = os.getenv("MARKET_DATA_API_KEY", "").strip()
    MARKET_DATA_BASE_URL = os.getenv("MARKET_DATA_BASE_URL", "").strip()
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    TRUSTED_QR_DOMAINS = {
        "pmkisan.gov.in", "soilhealth.dac.gov.in", "enam.gov.in", "www.enam.gov.in",
        "agmarknet.gov.in", "www.agmarknet.gov.in", "telangana.gov.in", "www.telangana.gov.in",
        "ossds.telangana.gov.in", "myscheme.gov.in", "www.myscheme.gov.in",
        "scadev.seedsgrowerp.com", "seedsgrowerp.com", "www.seedsgrowerp.com",
    }
