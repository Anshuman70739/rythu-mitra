"""SQLite persistence and non-destructive schema initialization for Rythu Mitra."""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator
from flask import current_app, g

SCHEMA_VERSION = 3

# These are separate domain tables. Each stores its own payload and its own
# owner/source/freshness envelope; private entities are never mixed in a single
# public generic `records` table.
RESOURCE_TABLES = {
    "farms": "farms",
    "farm-plots": "farm_plots",
    "crop-plans": "crop_plans",
    "crop-tasks": "crop_tasks",
    "farm-diary": "farm_diary",
    "soil-records": "soil_records",
    "input-purchases": "input_purchases",
    "seed-lots": "seed_lots",
    "seed-scans": "seed_scans",
    "seed-test-results": "seed_test_results",
    "seed-complaints": "seed_complaints",
    "seed-complaint-events": "seed_complaint_events",
    "disease-knowledge": "disease_knowledge",
    "disease-reviews": "disease_reviews",
    "market-prices": "market_prices",
    "market-sources": "market_sources",
    "schemes": "government_schemes",
    "scheme-documents": "scheme_documents",
    "scheme-tracking": "scheme_tracking",
    "expenses": "farm_expenses",
    "income": "farm_income",
    "loans": "loans",
    "water-sources": "water_sources",
    "irrigation-records": "irrigation_records",
    "irrigation-plans": "irrigation_plans",
    "rainwater-plans": "rainwater_plans",
    "inventory-items": "inventory_items",
    "labour-plans": "labour_plans",
    "crop-rotation-plans": "crop_rotation_plans",
    "intercropping-plans": "intercropping_plans",
    "livestock": "livestock",
    "livestock-health": "livestock_health_records",
    "dairy-records": "dairy_records",
    "fish-ponds": "fish_ponds",
    "harvest-records": "harvest_records",
    "produce-quality": "produce_quality_records",
    "drying-records": "drying_records",
    "storage-facilities": "storage_facilities",
    "storage-bookings": "storage_bookings",
    "equipment-listings": "equipment_listings",
    "equipment-bookings": "equipment_bookings",
    "farmer-listings": "farmer_listings",
    "buyer-requests": "buyer_requests",
    "expert-questions": "expert_questions",
    "expert-answers": "expert_answers",
    "expert-votes": "expert_votes",
    "crop-damage-reports": "crop_damage_reports",
    "complaints": "grievance_reports",
    "insurance-records": "insurance_records",
    "community-posts": "community_posts",
    "market-feedback": "market_feedback",
    "fpo-directory": "fpo_directory",
    "fpo-groups": "fpo_groups",
    "pest-reports": "pest_reports",
    "notices": "notices",
    "family-helpers": "family_helpers",
    "service-directory": "service_directory",
    "livestock-fish-records": "livestock_fish_records",
    "crop-risk-reports": "crop_risk_reports",
    "input-products": "input_products",
    "harvest-plans": "harvest_plans",
    "offline-drafts": "offline_drafts",
    "farm-observations": "farm_observations",
    "insurance-claims": "insurance_claims",
    "benefit-tracking": "benefit_tracking",
    "local-alerts": "local_alerts",
    "source-records": "source_records",
    "content-reports": "content_reports",
}

BASE_SCHEMA = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL,
    description TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL CHECK(role IN ('farmer','expert','admin','buyer','provider')),
    password_hash TEXT NOT NULL,
    language TEXT NOT NULL DEFAULT 'en' CHECK(language IN ('en','te')),
    district TEXT, mandal TEXT, village TEXT,
    land_area REAL, soil_type TEXT, irrigation TEXT,
    current_crop TEXT, crop_stage TEXT, previous_crop TEXT, season TEXT,
    experience INTEGER, budget REAL,
    is_active INTEGER NOT NULL DEFAULT 1,
    suspended_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    target TEXT,
    details_json TEXT NOT NULL DEFAULT '{}',
    request_id TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_logs(created_at DESC);
CREATE TABLE IF NOT EXISTS notifications (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'info',
    read_at TEXT,
    source_name TEXT NOT NULL DEFAULT 'Rythu Mitra',
    source_url TEXT,
    data_type TEXT NOT NULL DEFAULT 'SYSTEM',
    created_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_notifications_owner ON notifications(user_id, created_at DESC);
CREATE TABLE IF NOT EXISTS uploads (
    id TEXT PRIMARY KEY,
    owner_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    stored_name TEXT NOT NULL UNIQUE,
    media_type TEXT NOT NULL,
    byte_size INTEGER NOT NULL,
    sha256 TEXT NOT NULL,
    original_name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(owner_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_upload_owner ON uploads(owner_id, created_at DESC);
CREATE TABLE IF NOT EXISTS offline_sync_operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id INTEGER NOT NULL,
    operation_id TEXT NOT NULL,
    resource TEXT NOT NULL,
    result_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(owner_id, operation_id),
    FOREIGN KEY(owner_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS legacy_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT NOT NULL,
    owner_id INTEGER,
    title TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    source_name TEXT NOT NULL DEFAULT 'Unknown',
    source_url TEXT,
    data_type TEXT NOT NULL DEFAULT 'DEMO',
    last_updated TEXT NOT NULL,
    last_verified TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(owner_id) REFERENCES users(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_legacy_kind ON legacy_records(kind, created_at DESC);
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def database_path() -> Path:
    return Path(current_app.config["DATABASE_PATH"]).expanduser().resolve()


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    """Connection context that commits on success, rolls back on failure, and closes."""
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 15000")
    conn.execute("PRAGMA journal_mode = WAL")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_db() -> sqlite3.Connection:
    """Request-scoped connection for callers that need manual transaction control."""
    if "db_conn" not in g:
        path = database_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(path, timeout=15)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA busy_timeout = 15000")
        g.db_conn = conn
    return g.db_conn


def close_db(_error: BaseException | None = None) -> None:
    conn = g.pop("db_conn", None)
    if conn is not None:
        conn.close()


def _upgrade_users_role_constraint(conn: sqlite3.Connection) -> None:
    """Rebuild only the users table when upgrading an old CHECK that lacks provider.

    A same-directory SQLite backup is created before this destructive DDL step.
    Other tables keep their `REFERENCES users(id)` definitions because the old
    table is dropped and the replacement receives the same final name.
    """
    row = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'").fetchone()
    ddl = str(row[0] or "").casefold() if row else ""
    if not ddl or "provider" in ddl:
        return
    path = database_path()
    if path.exists() and path.stat().st_size:
        backup = path.with_name(path.stem + ".pre-provider-migration" + path.suffix)
        if not backup.exists():
            backup_conn = None
            try:
                backup_conn = sqlite3.connect(str(backup))
                conn.backup(backup_conn)
            except Exception:
                current_app.logger.exception("Could not create a pre-migration database backup")
                try: backup.unlink(missing_ok=True)
                except OSError: pass
                raise RuntimeError("Database role migration was stopped because a backup could not be created.")
            finally:
                if backup_conn is not None: backup_conn.close()
    columns = {r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()}
    def col(name: str, fallback: str = "NULL") -> str:
        return name if name in columns else fallback
    conn.execute("PRAGMA foreign_keys=OFF")
    try:
        conn.execute("DROP TABLE IF EXISTS users_v3")
        conn.execute("""CREATE TABLE users_v3 (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, phone TEXT NOT NULL UNIQUE,
            role TEXT NOT NULL CHECK(role IN ('farmer','expert','admin','buyer','provider')),
            password_hash TEXT NOT NULL, language TEXT NOT NULL DEFAULT 'en' CHECK(language IN ('en','te')),
            district TEXT, mandal TEXT, village TEXT, land_area REAL, soil_type TEXT, irrigation TEXT,
            current_crop TEXT, crop_stage TEXT, previous_crop TEXT, season TEXT, experience INTEGER,
            budget REAL, is_active INTEGER NOT NULL DEFAULT 1, suspended_at TEXT,
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL)""")
        stamp = "'" + utc_now().replace("'", "''") + "'"
        sources = [
            col("id"), col("name", "'Farmer'"), col("phone", "''"), col("role", "'farmer'"),
            col("password_hash", "''"), col("language", "'en'"), col("district"), col("mandal"),
            col("village"), col("land_area"), col("soil_type"), col("irrigation"), col("current_crop"),
            col("crop_stage"), col("previous_crop"), col("season"), col("experience"), col("budget"),
            col("is_active", "1"), col("suspended_at"), col("created_at", stamp), col("updated_at", stamp),
        ]
        conn.execute("INSERT INTO users_v3(" + "id,name,phone,role,password_hash,language,district,mandal,village,land_area,soil_type,irrigation,current_crop,crop_stage,previous_crop,season,experience,budget,is_active,suspended_at,created_at,updated_at" + ") SELECT " + ",".join(sources) + " FROM users")
        conn.execute("DROP TABLE users")
        conn.execute("ALTER TABLE users_v3 RENAME TO users")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)")
    finally:
        conn.execute("PRAGMA foreign_keys=ON")


def init_db() -> None:
    """Apply additive schema initialization; never drop application/user data."""
    with connect() as conn:
        conn.executescript(BASE_SCHEMA)
        _upgrade_users_role_constraint(conn)
        # Build farms first; the remaining domain tables have their own ownership scope.
        def create_resource(table: str) -> None:
            # Table identifiers originate only from RESOURCE_TABLES constants.
            conn.execute(f"""CREATE TABLE IF NOT EXISTS {table} (
                id TEXT PRIMARY KEY,
                owner_id INTEGER,
                farm_id TEXT,
                payload_json TEXT NOT NULL DEFAULT '{{}}',
                status TEXT NOT NULL DEFAULT 'SUBMITTED',
                source_name TEXT NOT NULL DEFAULT 'User submitted',
                source_url TEXT,
                data_type TEXT NOT NULL DEFAULT 'USER_SUBMITTED'
                    CHECK(data_type IN ('LIVE','CACHED','CURATED','USER_SUBMITTED','MODEL_OUTPUT','DEMO','UNAVAILABLE','SYSTEM','USER_ENTERED_CALCULATION')),
                confidence REAL,
                last_updated TEXT NOT NULL,
                last_verified TEXT,
                expires_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(owner_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(farm_id) REFERENCES farms(id) ON DELETE SET NULL
            )""")
            conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_owner_created ON {table}(owner_id, created_at DESC)")
            conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_farm_created ON {table}(farm_id, created_at DESC)")
            conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_status ON {table}(status)")

        create_resource("farms")
        for slug, table in RESOURCE_TABLES.items():
            if table != "farms":
                create_resource(table)
        conn.execute("""CREATE TABLE IF NOT EXISTS disease_scan_history (
            id TEXT PRIMARY KEY, owner_id INTEGER, session_ref TEXT NOT NULL,
            upload_id TEXT, result TEXT NOT NULL, class_index INTEGER, confidence REAL,
            label_verified INTEGER NOT NULL DEFAULT 0, low_confidence INTEGER NOT NULL DEFAULT 1,
            model_version TEXT, guidance TEXT NOT NULL, created_at TEXT NOT NULL, saved_at TEXT,
            FOREIGN KEY(owner_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(upload_id) REFERENCES uploads(id) ON DELETE SET NULL)""")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_disease_history_owner ON disease_scan_history(owner_id, created_at DESC)")
        # Safe one-time compatibility migration from the originally supplied backend's table.
        # The legacy table is retained; this copies rows to the renamed compatibility table.
        legacy_exists = conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='records'").fetchone()
        if legacy_exists:
            columns = {r[1] for r in conn.execute("PRAGMA table_info(records)").fetchall()}
            if {"id","kind","owner_id","title","payload","status","source","source_url","data_type","last_updated","created_at"}.issubset(columns):
                conn.execute("""INSERT OR IGNORE INTO legacy_records(id,kind,owner_id,title,payload_json,status,source_name,source_url,data_type,last_updated,created_at)
                    SELECT id,kind,owner_id,title,payload,status,source,source_url,
                    CASE lower(data_type) WHEN 'demo' THEN 'DEMO' WHEN 'live' THEN 'LIVE' WHEN 'cached' THEN 'CACHED' WHEN 'user' THEN 'USER_SUBMITTED' ELSE 'CURATED' END,
                    last_updated,created_at FROM records""")
        # Additive migration for databases created by the original single-file backend.
        user_columns = {r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()}
        if "is_active" not in user_columns:
            conn.execute("ALTER TABLE users ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1")
        if "suspended_at" not in user_columns:
            conn.execute("ALTER TABLE users ADD COLUMN suspended_at TEXT")
        current = conn.execute("SELECT MAX(version) FROM schema_migrations").fetchone()[0]
        if not current or current < SCHEMA_VERSION:
            conn.execute("INSERT OR REPLACE INTO schema_migrations(version,applied_at,description) VALUES(?,?,?)",
                         (SCHEMA_VERSION, utc_now(), "Version 3: modular domain tables, account-state fields and provider-role compatibility"))
        conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
    if current_app.config.get("DEMO_MODE"):
        seed_demo_data()


def seed_demo_data() -> None:
    """Create openly labelled local-demo fixtures only when DEMO_MODE=true."""
    from werkzeug.security import generate_password_hash
    import secrets
    stamp = utc_now()
    demo_users = [
        ("Demo Farmer", "9999999999", "farmer", "demo-farmer", "Warangal", "Cotton", "Flowering"),
        ("Demo Expert", "8888888888", "expert", "demo-expert", "Warangal", None, None),
        ("Demo Admin", "7777777777", "admin", "demo-admin", "Warangal", None, None),
        ("Demo Buyer", "6666666666", "buyer", "demo-buyer", "Warangal", None, None),
    ]
    with connect() as conn:
        for name, phone, role, password, district, crop, stage in demo_users:
            if not conn.execute("SELECT 1 FROM users WHERE phone=?", (phone,)).fetchone():
                conn.execute("""INSERT INTO users(name,phone,role,password_hash,district,current_crop,crop_stage,soil_type,irrigation,land_area,season,created_at,updated_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""", (name,phone,role,generate_password_hash(password),district,crop,stage,"Black soil" if role=="farmer" else None,"Borewell" if role=="farmer" else None,2.0 if role=="farmer" else None,"Kharif" if role=="farmer" else None,stamp,stamp))
        # Market numbers intentionally retain their old date so the API can mark them stale.
        demo_prices = [
            {"commodity":"Cotton","market":"Warangal","district":"Warangal","minimum_price":6500,"modal_price":7100,"maximum_price":7350,"arrival_quantity":"120 q","price_date":"2026-08-15","unit":"₹/quintal","notes":"Historical demo fixture; not a current market quote."},
            {"commodity":"Chilli","market":"Khammam","district":"Khammam","minimum_price":9800,"modal_price":11200,"maximum_price":12400,"arrival_quantity":"75 q","price_date":"2026-08-15","unit":"₹/quintal","notes":"Historical demo fixture; not a current market quote."},
            {"commodity":"Maize","market":"Nizamabad","district":"Nizamabad","minimum_price":1900,"modal_price":2120,"maximum_price":2250,"arrival_quantity":"190 q","price_date":"2026-08-15","unit":"₹/quintal","notes":"Historical demo fixture; not a current market quote."},
        ]
        for payload in demo_prices:
            if not conn.execute("SELECT 1 FROM market_prices WHERE json_extract(payload_json,'$.commodity')=? AND json_extract(payload_json,'$.market')=? AND data_type='DEMO'",(payload["commodity"],payload["market"])).fetchone():
                conn.execute("INSERT INTO market_prices(id,owner_id,farm_id,payload_json,status,source_name,source_url,data_type,last_updated,last_verified,created_at,updated_at) VALUES(?,NULL,NULL,?,?,?,?,?,?,?,?,?)",
                    (secrets.token_urlsafe(16),json_dump(payload),"ACTIVE","DEMO FIXTURE — NOT LIVE",None,"DEMO",stamp,None,stamp,stamp))
        demo_schemes = [
            {"name":"PM-KISAN","description":"Income-support scheme; verify current terms and enrolment directly with the official programme.","benefit":"See official site","eligibility":"Verify officially; this app does not determine eligibility.","documents":["Identity","bank details","land details as required by current rules"],"steps":["Read current official guidance","Confirm eligibility with the authority","Use the official application route"],"official_url":"https://pmkisan.gov.in/","state":"India","districts":["All districts—check current applicability"]},
            {"name":"Soil Health Card","description":"Soil-test and nutrient-management service; check local availability.","benefit":"Soil health information and official recommendations","eligibility":"Check with the official portal/local agriculture office.","documents":["Land details","soil sample as instructed"],"steps":["Check official service information","Ask the local agriculture office how to submit a soil sample"],"official_url":"https://soilhealth.dac.gov.in/","state":"India","districts":["All districts—check current applicability"]},
            {"name":"Kisan Credit Card","description":"Credit facility through participating institutions; terms vary.","benefit":"Subject to participating lender and current scheme terms","eligibility":"Verify with a participating bank and the official programme.","documents":["Identity","land/cultivation documents as required by lender"],"steps":["Contact a participating lender","Confirm current documents, rates and terms","Submit through the official lender route"],"official_url":"https://www.myscheme.gov.in/","state":"India","districts":["Check current applicability"]},
        ]
        for payload in demo_schemes:
            if not conn.execute("SELECT 1 FROM government_schemes WHERE json_extract(payload_json,'$.name')=? AND data_type='DEMO'",(payload["name"],)).fetchone():
                conn.execute("INSERT INTO government_schemes(id,owner_id,farm_id,payload_json,status,source_name,source_url,data_type,last_updated,last_verified,created_at,updated_at) VALUES(?,NULL,NULL,?,?,?,?,?,?,?,?,?)",
                    (secrets.token_urlsafe(16),json_dump(payload),"ACTIVE","DEMO FIXTURE — VERIFY OFFICIALLY",payload["official_url"],"DEMO",stamp,None,stamp,stamp))


def json_dump(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def json_load(value: str | None, fallback=None):
    if not value:
        return {} if fallback is None else fallback
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return {} if fallback is None else fallback
