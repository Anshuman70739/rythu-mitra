"""Check Flask startup, SQLite readiness, folders, and configured integrations."""
from __future__ import annotations
import sys
from pathlib import Path as _BootstrapPath
sys.path.insert(0, str(_BootstrapPath(__file__).resolve().parents[1]))
import json
from pathlib import Path
from rythu_mitra_backend import create_app
from rythu_mitra_backend.services.models import has_model_asset, has_disease_model_bundle


def main() -> int:
    app = create_app()
    with app.test_client() as client:
        health = client.get("/health")
        ready = client.get("/ready")
    report = {
        "health_http": health.status_code,
        "health": health.get_json(silent=True),
        "ready_http": ready.status_code,
        "ready": ready.get_json(silent=True),
        "upload_dir_exists": Path(app.config["UPLOAD_DIR"]).is_dir(),
        "crop_model_exists": has_model_asset("crop_model.pkl"),
        "disease_model_exists": has_model_asset("plant_disease_model.h5"),
        "disease_model_bundle_usable": has_disease_model_bundle(),
        "disease_labels_exists": (Path(app.config["MODEL_DIR"]) / "disease_labels.json").is_file() or (Path(app.root_path).parent / "data" / "disease_labels.json").is_file(),
        "weather_configured": bool(app.config.get("OPENWEATHER_API_KEY")),
        "market_adapter_configured": bool(app.config.get("DATA_GOV_IN_API_KEY") or app.config.get("MARKET_DATA_BASE_URL")),
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if health.status_code == 200 and ready.status_code == 200 else 1


if __name__ == "__main__":
    raise SystemExit(main())
