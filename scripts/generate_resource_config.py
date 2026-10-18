#!/usr/bin/env python3
"""Generate frontend field metadata from the backend's RESOURCE_SPECS allowlist."""
import ast, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "rythu_mitra_backend" / "resources.py"
tree = ast.parse(source.read_text(encoding="utf-8"))
assign = next(node for node in tree.body if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "RESOURCE_SPECS")
node = assign.value
NUMERIC = set("area_acres budget experience quantity cost price amount N P K ph organic_carbon electrical_conductivity germination_label_pct purity_pct net_weight mrp tested_count germinated_count minimum_price modal_price maximum_price arrival_quantity distance_km transport_per_km principal_amount interest_rate_apr amount_repaid installment_amount estimated_capacity duration_minutes estimated_volume_liters rainfall_mm low_stock_threshold purchase_price workers_required days wage_per_day actual_cost age_months pond_area_acres milk_liters price_per_liter feed_cost veterinary_cost moisture_pct damage_pct capacity cost_per_quintal_day quantity_quintals target_price asking_price risk_score affected_area_acres premium_amount pond_area fish_losses starting_moisture_pct final_moisture_pct land_area".split())
ARRAY = set("documents steps districts crops packet_upload_ids attachment_ids evidence_upload_ids image_ids documents_submitted scopes factors".split())
OBJECT = {"draft_payload"}
BOOLEAN = set("farmer_confirmed anonymous enabled verified available verified_by_official follow_up_required is_active".split())
DATE = set("test_date price_date purchase_date packing_date validity_date sowing_date application_date next_action_date expense_date income_date start_date end_date next_due_date event_date record_date harvest_date observation_date due_date reminder_at published_at expires_at target_harvest_date target_window_start target_window_end available_from available_to last_verified last_maintenance_date stocking_date date_observed created_at updated_at".split())
LONG = set("notes description body question answer symptoms safe_guidance eligibility verification_notes water_plan risk_notes assumptions location_notes privacy_note recommendation availability_note maintenance_note limitations experience_or_question message report review_notes recommended_next_step".split())
resources = {}
for key, val in zip(node.keys, node.values):
    slug = ast.literal_eval(key); fields = ast.literal_eval(val.args[0]); required = ast.literal_eval(val.args[1]) if len(val.args) > 1 else ()
    kw = {item.arg:item.value for item in val.keywords}
    def literal(name, default): return ast.literal_eval(kw[name]) if name in kw else default
    def meta(field):
        kind = "boolean" if field in BOOLEAN else "number" if field in NUMERIC else "array" if field in ARRAY else "object" if field in OBJECT else "date" if field in DATE else "textarea" if field in LONG else "text"
        return {"name":field,"type":kind,"required":field in required}
    resources[slug] = {"fields":[meta(f) for f in fields], "required":list(required), "create_roles":list(literal("create_roles",("farmer",))), "public_read":literal("public_read",False), "admin_managed":literal("admin_managed",False), "private":literal("private",True)}
out = ROOT / "static" / "data" / "resource-config.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(resources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Wrote {len(resources)} resource schemas to {out.relative_to(ROOT)}")
