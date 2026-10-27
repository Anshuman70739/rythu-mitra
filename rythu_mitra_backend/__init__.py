"""Rythu Mitra Flask application factory."""
from __future__ import annotations
import logging
from pathlib import Path
from flask import Flask, jsonify, request, session
from werkzeug.exceptions import HTTPException
from PIL import Image
from .config import Config, PROJECT_ROOT
from .db import init_db
from .security import api_error, audit, enforce_global_api_limit, install_rate_limiter, valid_csrf
from .routes.core import bp as core_bp
from .routes.domains import bp as domains_bp
from .routes.seeds import bp as seeds_bp
from .routes.disease import bp as disease_bp
from .routes.legacy import bp as legacy_bp
from .routes.admin import bp as admin_bp
from .routes.misc import bp as misc_bp
from .routes.channels import bp as channels_bp


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, template_folder=str(PROJECT_ROOT / "templates"), static_folder=str(PROJECT_ROOT / "static"), static_url_path="/static")
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    # Recompute environment-dependent security requirements after test/deployment overrides.
    is_production = str(app.config.get("APP_ENV", "development")).strip().lower() == "production"
    app.config["IS_PRODUCTION"] = is_production
    if is_production:
        secret = str(app.config.get("SECRET_KEY", "")).strip()
        explicitly_configured = bool(app.config.get("SECRET_KEY_CONFIGURED")) or bool(test_config and "SECRET_KEY" in test_config)
        if not explicitly_configured or len(secret) < 32:
            raise RuntimeError("Production requires a configured SECRET_KEY with at least 32 characters.")
        app.config["DEMO_MODE"] = False
        app.config["SESSION_COOKIE_SECURE"] = True
    # A forwarded client IP is trusted only when the hosting topology is explicitly configured.
    trusted_proxy_hops = int(app.config.get("TRUSTED_PROXY_HOPS", 0) or 0)
    if trusted_proxy_hops > 0:
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=trusted_proxy_hops, x_proto=trusted_proxy_hops, x_host=0, x_port=0, x_prefix=0)
    install_rate_limiter(app)
    Path(app.config["UPLOAD_DIR"]).mkdir(parents=True, exist_ok=True)
    Path(app.config["DATABASE_PATH"]).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
    Image.MAX_IMAGE_PIXELS = int(app.config.get("MAX_IMAGE_PIXELS", 20_000_000))
    logging.basicConfig(level=getattr(logging, str(app.config.get("LOG_LEVEL", "INFO")).upper(), logging.INFO))
    app.register_blueprint(core_bp)
    app.register_blueprint(domains_bp)
    app.register_blueprint(seeds_bp)
    app.register_blueprint(disease_bp)
    app.register_blueprint(legacy_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(misc_bp)
    app.register_blueprint(channels_bp)

    @app.before_request
    def ensure_session_tokens():
        if "csrf_token" not in session:
            import secrets
            session["csrf_token"] = secrets.token_urlsafe(32)
        if "scan_session_ref" not in session:
            import secrets
            session["scan_session_ref"] = secrets.token_urlsafe(32)
        session.permanent = True

    @app.before_request
    def protect_api_requests():
        limited = enforce_global_api_limit()
        if limited is not None:
            return limited
        if request.path.startswith("/api/") and request.method.upper() in {"POST", "PUT", "PATCH", "DELETE"}:
            if not valid_csrf():
                audit("csrf_rejected", request.path, user_id=session.get("user_id"), details={"method": request.method})
                return api_error("Invalid request token. Refresh the page and try again.", 403)
        return None

    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com data:; script-src 'self'; "
            "img-src 'self' data: blob:; connect-src 'self'; base-uri 'self'; frame-ancestors 'none'; "
            "object-src 'none'; form-action 'self'"
        )
        response.headers["Permissions-Policy"] = "geolocation=(self), microphone=(self), camera=(self)"
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        response.headers["Origin-Agent-Cluster"] = "?1"
        if app.config.get("IS_PRODUCTION") and request.is_secure:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        # Personalized HTML as well as APIs should not be cached by shared browser/proxy caches.
        if request.path.startswith("/api/") or request.path in {"/health", "/ready"} or request.endpoint != "static":
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.errorhandler(413)
    def request_too_large(_error):
        return api_error("Request is too large. Images must respect the configured upload limit.", 413)

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        if isinstance(error, HTTPException):
            if request.path.startswith("/api/"):
                return api_error(error.description or "Request failed.", error.code or 400)
            return error
        app.logger.exception("Unhandled request exception: %s", type(error).__name__)
        return api_error("Something went wrong. Please try again.", 500) if request.path.startswith("/api/") else ("Internal server error", 500)

    with app.app_context():
        init_db()
    return app


__all__ = ["create_app"]
