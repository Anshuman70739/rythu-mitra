"""Authentication, CSRF, auditing, rate limiting, and public serializers."""
from __future__ import annotations
from functools import wraps
from collections import OrderedDict, deque
from threading import RLock
from hashlib import sha256
import hmac
import json
import secrets
import time
import math
from flask import current_app, jsonify, request, session
from werkzeug.security import generate_password_hash
from .db import connect, utc_now, json_dump

_PUBLIC_USER_FIELDS = ("id", "name", "role", "language", "district", "mandal", "village", "land_area", "soil_type", "irrigation", "current_crop", "crop_stage", "previous_crop", "season", "experience", "budget")
_MAX_RATE_KEYS = 20_000


class RateLimiterUnavailable(RuntimeError):
    """Raised when production's required shared limiter cannot be reached."""


class InMemoryRateLimiter:
    """Thread-safe sliding-window limiter for local development and tests only."""
    def __init__(self, max_keys: int = _MAX_RATE_KEYS):
        self.max_keys = max_keys
        self.buckets: OrderedDict[str, deque[float]] = OrderedDict()
        self.lock = RLock()
        self.calls = 0

    def hit(self, key: str, limit: int, window: int) -> int | None:
        now = time.monotonic()
        cutoff = now - window
        with self.lock:
            bucket = self.buckets.get(key)
            if bucket is None:
                bucket = deque()
                self.buckets[key] = bucket
            else:
                self.buckets.move_to_end(key)
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()
            if len(bucket) >= limit:
                return max(1, math.ceil(window - (now - bucket[0])))
            bucket.append(now)
            self.calls += 1
            if self.calls % 200 == 0:
                stale_keys = [k for k, q in self.buckets.items() if not q or q[-1] <= cutoff]
                for stale in stale_keys:
                    self.buckets.pop(stale, None)
            while len(self.buckets) > self.max_keys:
                self.buckets.popitem(last=False)
        return None


class RedisRateLimiter:
    """Shared sliding-window limiter for production and multi-worker hosting."""
    _SCRIPT = r"""
    local now = tonumber(ARGV[1])
    local window = tonumber(ARGV[2])
    local limit = tonumber(ARGV[3])
    local member = ARGV[4]
    redis.call('ZREMRANGEBYSCORE', KEYS[1], '-inf', now - window)
    local count = redis.call('ZCARD', KEYS[1])
    if count >= limit then
      local first = redis.call('ZRANGE', KEYS[1], 0, 0, 'WITHSCORES')
      local retry = math.max(1, math.ceil(window - (now - tonumber(first[2]))) )
      redis.call('PEXPIRE', KEYS[1], window * 1000)
      return {0, retry}
    end
    redis.call('ZADD', KEYS[1], now, member)
    redis.call('PEXPIRE', KEYS[1], window * 1000)
    return {1, 0}
    """

    def __init__(self, client):
        self.client = client

    def hit(self, key: str, limit: int, window: int) -> int | None:
        now = time.time()
        storage_key = "rm:rate:" + sha256(key.encode("utf-8", "replace")).hexdigest()
        member = f"{now:.6f}:{secrets.token_hex(8)}"
        try:
            allowed, retry = self.client.eval(self._SCRIPT, 1, storage_key, now, window, limit, member)
        except Exception as exc:
            raise RateLimiterUnavailable("Shared rate-limit storage is unavailable.") from exc
        return None if int(allowed) == 1 else max(1, int(retry))


def install_rate_limiter(app) -> None:
    """Use shared Redis in production; bound in-memory state in development/tests."""
    if app.config.get("IS_PRODUCTION"):
        redis_url = str(app.config.get("REDIS_URL", "")).strip()
        if not redis_url:
            raise RuntimeError("Production requires REDIS_URL for shared rate limiting. Configure Redis before launch.")
        try:
            import redis
            client = redis.Redis.from_url(redis_url, socket_connect_timeout=2, socket_timeout=2, health_check_interval=30)
            client.ping()
        except Exception as exc:
            raise RuntimeError("Production rate-limit Redis is not reachable. Refusing to start without shared rate limiting.") from exc
        app.extensions["rm_rate_limiter"] = RedisRateLimiter(client)
    else:
        app.extensions["rm_rate_limiter"] = InMemoryRateLimiter()


def _limiter_hit(key: str, limit: int, window: int) -> int | None:
    from flask import current_app
    limiter = current_app.extensions.get("rm_rate_limiter")
    if limiter is None:
        limiter = InMemoryRateLimiter()
        current_app.extensions["rm_rate_limiter"] = limiter
    return limiter.hit(key, limit, window)


def enforce_global_api_limit():
    """Apply size and coarse per-IP/account budgets to every API route."""
    if not request.path.startswith("/api/"):
        return None
    max_query = max(256, int(current_app.config.get("MAX_QUERY_BYTES", 4096)))
    if len(request.query_string or b"") > max_query:
        return api_error("The request query is too long.", 414)
    method = request.method.upper()
    if method in {"POST", "PUT", "PATCH", "DELETE"} and request.is_json:
        body_limit = max(1024, int(current_app.config.get("MAX_JSON_BODY_BYTES", 1_048_576)))
        if request.content_length is not None and request.content_length > body_limit:
            return api_error("JSON request body is too large.", 413)
        if len(request.get_data(cache=True, as_text=False)) > body_limit:
            return api_error("JSON request body is too large.", 413)
    write = method in {"POST", "PUT", "PATCH", "DELETE"}
    bucket_type = "write" if write else "read"
    limit_key = "API_WRITE_RATE_LIMIT" if write else "API_READ_RATE_LIMIT"
    default_limit = 60 if write else 180
    limit = max(1, int(current_app.config.get(limit_key, default_limit)))
    ip = request.remote_addr or "unknown"
    keys = [f"global:{bucket_type}:ip:{ip}"]
    uid = session.get("user_id")
    if uid:
        keys.append(f"global:{bucket_type}:user:{uid}")
    for key in keys:
        try:
            retry = _limiter_hit(key, limit, 60)
        except RateLimiterUnavailable:
            current_app.logger.error("Shared rate limiter unavailable; rejecting API request.")
            response = api_error("Request protection is temporarily unavailable. Please retry shortly.", 503)
            response[0].headers["Retry-After"] = "5"
            return response
        if retry is not None:
            response = api_error("Too many requests. Please try again shortly.", 429)
            response[0].headers["Retry-After"] = str(retry)
            return response
    return None


def api_error(message: str, status: int = 400, **extra):
    return jsonify(success=False, error=message, **extra), status


def get_user(user_id: int | None = None):
    uid = user_id if user_id is not None else session.get("user_id")
    if not uid:
        return None
    with connect() as conn:
        return conn.execute("SELECT * FROM users WHERE id=? AND is_active=1", (uid,)).fetchone()


def current_user():
    return get_user()


def public_user(row):
    if row is None:
        return None
    return {key: row[key] for key in _PUBLIC_USER_FIELDS if key in row.keys()}


def valid_csrf() -> bool:
    token = request.headers.get("X-CSRF-Token")
    if not token and request.is_json:
        token = (request.get_json(silent=True) or {}).get("csrf_token")
    if not token and request.form:
        token = request.form.get("csrf_token")
    expected = session.get("csrf_token", "")
    return bool(token and expected and hmac.compare_digest(str(token), str(expected)))


def csrf_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not valid_csrf():
            audit("csrf_rejected", request.path, user_id=session.get("user_id"), details={"method": request.method})
            return api_error("Invalid request token. Refresh the page and try again.", 403)
        return fn(*args, **kwargs)
    return wrapped


def require_auth(roles: tuple[str, ...] = ()):
    def deco(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            row = current_user()
            if row is None:
                return api_error("Please sign in to continue.", 401)
            if roles and row["role"] not in roles:
                audit("authorization_denied", request.path, user_id=row["id"], details={"required_roles": roles})
                return api_error("You are not authorized for this action.", 403)
            return fn(*args, **kwargs)
        return wrapped
    return deco


def rate_limit(limit: int, window: int = 60):
    """Per-route sliding-window budget, enforced by shared Redis in production."""
    def deco(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            ip = request.remote_addr or "unknown"
            identity_keys = [f"route:{fn.__module__}.{fn.__name__}:ip:{ip}"]
            uid = session.get("user_id")
            if uid is not None:
                identity_keys.append(f"route:{fn.__module__}.{fn.__name__}:user:{uid}")
            for key in identity_keys:
                try:
                    retry = _limiter_hit(key, limit, window)
                except RateLimiterUnavailable:
                    current_app.logger.error("Shared rate limiter unavailable; rejecting request to %s", request.path)
                    response = api_error("Request protection is temporarily unavailable. Please retry shortly.", 503)
                    response[0].headers["Retry-After"] = "5"
                    return response
                if retry is not None:
                    response = api_error("Too many requests. Please try again shortly.", 429)
                    response[0].headers["Retry-After"] = str(retry)
                    return response
            return fn(*args, **kwargs)
        return wrapped
    return deco


def audit(action: str, target: str | None = None, user_id: int | None = None, details=None):
    # Do not pass passwords, tokens, API keys, or image contents to this function.
    try:
        with connect() as conn:
            conn.execute("INSERT INTO audit_logs(user_id, action, target, details_json, created_at) VALUES(?,?,?,?,?)",
                         (user_id if user_id is not None else session.get("user_id"), action[:100], str(target or "")[:240], json_dump(details or {}), utc_now()))
    except Exception:
        current_app.logger.exception("Audit log write failed for action %s", action)


def json_body(max_bytes: int = 32_768):
    if not request.is_json:
        return None, (api_error("Content-Type must be application/json.", 415))
    raw = request.get_data(cache=True)
    if len(raw) > max_bytes:
        return None, (api_error("Request body is too large.", 413))
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, (api_error("Send a JSON object.", 400))
    return data, None


def text_field(data: dict, key: str, *, required: bool = False, max_length: int = 250, default=None):
    val = data.get(key, default)
    if val is None:
        if required:
            raise ValueError(f"{key} is required.")
        return None
    if not isinstance(val, (str, int, float)) or isinstance(val, bool):
        raise ValueError(f"{key} must be text.")
    val = str(val).strip()
    if required and not val:
        raise ValueError(f"{key} is required.")
    if len(val) > max_length:
        raise ValueError(f"{key} must be at most {max_length} characters.")
    return val


def number_field(data: dict, key: str, *, required: bool = False, minimum: float | None = None, maximum: float | None = None):
    import math
    value = data.get(key)
    if value is None:
        if required:
            raise ValueError(f"{key} is required.")
        return None
    if isinstance(value, bool):
        raise ValueError(f"{key} must be a number.")
    try:
        out = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{key} must be a number.")
    if not math.isfinite(out):
        raise ValueError(f"{key} must be finite.")
    if minimum is not None and out < minimum:
        raise ValueError(f"{key} must be at least {minimum}.")
    if maximum is not None and out > maximum:
        raise ValueError(f"{key} must be at most {maximum}.")
    return out
