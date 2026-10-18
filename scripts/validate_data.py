"""Static database/resource registry checks plus live schema checks."""
from __future__ import annotations
import sys
from pathlib import Path as _BootstrapPath
sys.path.insert(0, str(_BootstrapPath(__file__).resolve().parents[1]))
import json
from pathlib import Path
from rythu_mitra_backend import create_app
from rythu_mitra_backend.db import connect, RESOURCE_TABLES
from rythu_mitra_backend.resources import RESOURCE_SPECS


def main() -> int:
    problems=[]
    for slug,spec in RESOURCE_SPECS.items():
        if slug not in RESOURCE_TABLES: problems.append(f"{slug}: no database table mapping")
        if len(spec.fields)!=len(set(spec.fields)): problems.append(f"{slug}: duplicate field allowlist")
        missing=set(spec.required)-set(spec.fields)
        if missing: problems.append(f"{slug}: required fields missing from allowlist: {sorted(missing)}")
        if any(f in {"owner_id","status","password_hash","api_key","secret_key","csrf_token"} for f in spec.fields):
            problems.append(f"{slug}: protected field unexpectedly writable")
    for slug,table in RESOURCE_TABLES.items():
        if slug not in RESOURCE_SPECS: problems.append(f"{slug}: DB table mapping has no resource spec")
    app=create_app()
    with app.app_context():
        with connect() as conn:
            missing_tables=[]
            for slug,table in RESOURCE_TABLES.items():
                if not conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",(table,)).fetchone():
                    missing_tables.append(table)
            if missing_tables: problems.append(f"Missing domain tables: {missing_tables}")
            if conn.execute("PRAGMA foreign_key_check").fetchall(): problems.append("SQLite foreign_key_check reports violations")
            version=conn.execute("SELECT MAX(version) FROM schema_migrations").fetchone()[0]
    report={"resource_specs":len(RESOURCE_SPECS),"resource_tables":len(RESOURCE_TABLES),"schema_version":version,"problems":problems}
    print(json.dumps(report,indent=2))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
