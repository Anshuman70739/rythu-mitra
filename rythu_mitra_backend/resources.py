"""Per-domain field allowlists and access rules for dedicated SQLite entity tables."""
from dataclasses import dataclass

@dataclass(frozen=True)
class ResourceSpec:
    fields: tuple[str, ...]
    required: tuple[str, ...] = ()
    create_roles: tuple[str, ...] = ("farmer",)
    public_read: bool = False
    admin_managed: bool = False
    private: bool = True
    has_farm: bool = False
    max_rows: int = 100

# Only fields listed here may be accepted from a client. Ownership, status,
# verification, source provenance and timestamps are controlled by the server.
S = ResourceSpec
RESOURCE_SPECS: dict[str, ResourceSpec] = {
    "farms": S(("name","district","mandal","village","area_acres","soil_type","irrigation","current_crop","crop_stage","previous_crop","season","budget","experience","notes"), ("name",), has_farm=False),
    "farm-plots": S(("name","farm_id","area_acres","soil_type","irrigation_source","current_crop","crop_stage","previous_crop","season","crop_variety","location_notes"), ("name","farm_id"), has_farm=True),
    "crop-plans": S(("farm_id","crop","variety","season","start_date","target_harvest_date","water_plan","risk_notes","assumptions"), ("crop",), has_farm=True),
    "crop-tasks": S(("farm_id","task","category","crop","stage","due_date","reminder_at","notes","completed_at","priority"), ("task",), has_farm=True),
    "farm-diary": S(("farm_id","entry_date","activity_type","crop","description","quantity","unit","cost","labour_count","image_ids","weather_note"), ("entry_date","activity_type"), has_farm=True),
    "soil-records": S(("farm_id","test_date","ph","N","P","K","organic_carbon","electrical_conductivity","laboratory","sample_location","report_upload_id","notes"), ("test_date",), has_farm=True),
    "input-purchases": S(("farm_id","product_name","category","brand","lot_number","dealer","quantity","unit","price","purchase_date","receipt_upload_id","crop","notes"), ("product_name","purchase_date"), has_farm=True),
    "seed-lots": S(("farm_id","crop","variety","brand","lot_number","batch_number","packing_date","validity_date","germination_label_pct","purity_pct","net_weight","mrp","dealer","dealer_district","certification_number","qr_content","purchase_date","receipt_upload_id","packet_upload_ids","farmer_confirmed"), ("crop",), has_farm=True),
    "seed-scans": S(("seed_lot_id","farm_id","crop","variety","brand","lot_number","batch_number","packing_date","validity_date","germination_label_pct","purity_pct","net_weight","mrp","dealer","certification_number","qr_content","packet_upload_ids","receipt_upload_id","ocr_text","ocr_status","farmer_confirmed"), (), has_farm=True),
    "seed-test-results": S(("seed_lot_id","farm_id","tested_count","germinated_count","test_date","test_method","label_germination_pct","notes"), ("tested_count","germinated_count","test_date"), has_farm=True),
    "seed-complaints": S(("seed_lot_id","farm_id","complaint_type","crop","variety","brand","lot_number","dealer","purchase_date","sowing_date","district","mandal","village","affected_area_acres","description","attachment_ids","germination_test_id","preferred_contact_method"), ("complaint_type","description"), has_farm=True),
    "seed-complaint-events": S(("complaint_id","event_type","description","created_by_role","official_reference","attachment_ids"), ("complaint_id","event_type"), create_roles=("farmer","expert","admin")),
    "disease-knowledge": S(("crop","condition_name","symptoms","safe_guidance","notes"), ("crop","condition_name","safe_guidance"), create_roles=("admin",), public_read=True, admin_managed=True, private=False),
    "disease-reviews": S(("scan_id","question_id","assessment","review_notes","recommended_next_step","follow_up_required"), ("scan_id","question_id","assessment","review_notes"), create_roles=("expert",)),
    "market-prices": S(("commodity","market","district","minimum_price","modal_price","maximum_price","arrival_quantity","arrival_unit","price_date","unit","distance_km","transport_per_km","notes"), ("commodity","market","price_date"), create_roles=("admin",), public_read=True, admin_managed=True, private=False),
    "market-sources": S(("name","provider_type","base_url","documentation_url","enabled","notes"), ("name","provider_type"), create_roles=("admin",), public_read=False, admin_managed=True),
    "schemes": S(("name","description","benefit","eligibility","documents","steps","official_url","districts","state","verification_notes"), ("name","official_url"), create_roles=("admin",), public_read=True, admin_managed=True, private=False),
    "scheme-documents": S(("scheme_id","document_name","notes","upload_id"), ("scheme_id","document_name")),
    "scheme-tracking": S(("scheme_id","application_date","application_reference","documents_submitted","current_status","next_action","next_action_date","official_contact","notes"), ("scheme_id",)),
    "expenses": S(("farm_id","category","amount","expense_date","crop","description","quantity","unit","receipt_upload_id","season"), ("category","amount","expense_date"), has_farm=True),
    "income": S(("farm_id","category","amount","income_date","crop","quantity","unit","buyer_reference","sale_slip_upload_id","notes"), ("category","amount","income_date"), has_farm=True),
    "loans": S(("farm_id","lender","loan_type","principal_amount","interest_rate_apr","amount_repaid","installment_amount","next_due_date","start_date","end_date","status_note","notes"), ("lender","principal_amount"), has_farm=True),
    "water-sources": S(("farm_id","source_type","name","estimated_capacity","capacity_unit","availability_note","last_maintenance_date","notes"), ("source_type",), has_farm=True),
    "irrigation-records": S(("farm_id","water_source_id","irrigation_date","duration_minutes","estimated_volume_liters","method","cost","rainfall_mm","crop","notes"), ("irrigation_date","method"), has_farm=True),
    "irrigation-plans": S(("farm_id","crop","crop_stage","soil_type","irrigation_method","recent_rainfall_mm","soil_moisture_observation","recommendation","assumptions"), ("crop",), has_farm=True),
    "rainwater-plans": S(("farm_id","practice","area_acres","soil_slope_note","estimated_capacity","maintenance_note"), ("practice",), has_farm=True),
    "inventory-items": S(("farm_id","item_name","category","brand","quantity","unit","low_stock_threshold","expiry_date","lot_number","purchase_price","dealer","receipt_upload_id"), ("item_name","quantity"), has_farm=True),
    "labour-plans": S(("farm_id","work_type","work_date","workers_required","days","wage_per_day","actual_cost","status_note","crop","notes"), ("work_type","work_date"), has_farm=True),
    "crop-rotation-plans": S(("farm_id","previous_crop","proposed_crop","season","soil_notes","water_availability","rotation_reason","limitations"), ("previous_crop","proposed_crop"), has_farm=True),
    "intercropping-plans": S(("farm_id","main_crop","companion_crop","season","row_pattern","water_notes","possible_benefits","limitations"), ("main_crop","companion_crop"), has_farm=True),
    "livestock": S(("farm_id","animal_type","name","animal_tag","breed","age_months","purchase_date","purchase_price","notes"), ("animal_type",), has_farm=True),
    "livestock-health": S(("farm_id","livestock_id","event_type","vaccine_or_treatment","event_date","next_due_date","veterinary_contact","cost","notes"), ("livestock_id","event_type","event_date"), has_farm=True),
    "dairy-records": S(("farm_id","livestock_id","record_date","milk_liters","price_per_liter","feed_cost","veterinary_cost","buyer_reference","notes"), ("record_date",), has_farm=True),
    "fish-ponds": S(("farm_id","pond_name","pond_area_acres","species","stocking_date","feed_notes","water_quality","fish_losses","harvest_date","notes"), ("species",), has_farm=True),
    "harvest-records": S(("farm_id","crop","harvest_date","quantity","unit","moisture_pct","grade","quality_notes","labour_required","machinery_required","storage_needed","transport_cost","sale_price"), ("crop","harvest_date","quantity"), has_farm=True),
    "produce-quality": S(("farm_id","harvest_id","test_date","moisture_pct","grade","size","damage_pct","colour","certificate_id","buyer_feedback"), ("harvest_id",), has_farm=True),
    "drying-records": S(("farm_id","harvest_id","drying_method","starting_moisture_pct","final_moisture_pct","start_date","end_date","notes"), ("harvest_id","drying_method"), has_farm=True),
    "storage-facilities": S(("name","facility_type","provider_name","district","location_label","capacity","capacity_unit","cost_per_quintal_day","crops","availability_note","contact_method"), ("name","district"), create_roles=("admin","provider"), public_read=True, admin_managed=True, private=False),
    "storage-bookings": S(("farm_id","facility_id","crop","quantity_quintals","start_date","end_date","contact_method","notes"), ("facility_id","crop","quantity_quintals"), has_farm=True),
    "equipment-listings": S(("name","equipment_type","provider_name","district","location_label","price","price_unit","available_from","available_to","availability_note","contact_method"), ("name","equipment_type","district"), create_roles=("admin","provider"), public_read=True, admin_managed=True, private=False),
    "equipment-bookings": S(("farm_id","listing_id","start_date","end_date","purpose","contact_method","notes"), ("listing_id","start_date"), has_farm=True),
    "farmer-listings": S(("farm_id","crop","quantity","unit","quality_grade","asking_price","district","available_from","notes"), ("crop","quantity"), public_read=True, has_farm=True),
    "buyer-requests": S(("crop","quantity","unit","quality_requirement","target_price","district","needed_by","notes"), ("crop","quantity"), create_roles=("buyer",), public_read=True, private=False),
    "expert-questions": S(("farm_id","title","question","crop","category","district","attachment_ids","anonymous","privacy_note"), ("question","category"), has_farm=True),
    "expert-answers": S(("question_id","answer","source_name","source_url","expert_verification_note"), ("question_id","answer"), create_roles=("expert",)),
    "expert-votes": S(("question_id","answer_id","vote","reason"), ("question_id","vote"), create_roles=("farmer",)),
    "crop-damage-reports": S(("farm_id","damage_type","observation_date","district","mandal","village","affected_area_acres","severity","description","attachment_ids","insurance_policy_reference","sowing_date"), ("damage_type","observation_date","description"), has_farm=True),
    "complaints": S(("category","subject","description","district","mandal","village","date_observed","attachment_ids","external_reference","preferred_contact_method"), ("category","description")),
    "insurance-records": S(("farm_id","provider","policy_number_masked","crop","season","coverage_note","premium_amount","start_date","end_date","official_contact","notes"), ("provider","crop"), has_farm=True),
    "insurance-claims": S(("farm_id","policy_reference","damage_report_id","date_reported","claim_reference","status_note","next_action","deadline","official_url","notes"), ("policy_reference","date_reported"), has_farm=True),
    "community-posts": S(("group_name","crop","district","post_type","body","experience_or_question","attachment_ids"), ("body","post_type"), public_read=True, private=False),
    "market-feedback": S(("market","commodity","feedback_type","observation_date","description","evidence_upload_ids"), ("market","feedback_type","description")),
    "fpo-directory": S(("name","district","crops","collection_centre","membership_process","official_url"), ("name","district"), create_roles=("admin",), public_read=True, admin_managed=True, private=False),
    "fpo-groups": S(("group_name","fpo_name","district","crop","purpose","meeting_date","notes"), ("group_name",)),
    "pest-reports": S(("crop","pest_name","district","approximate_area_label","severity","observation_date","description","evidence_upload_ids"), ("crop","pest_name","district","observation_date"), public_read=True, private=False),
    "notices": S(("title","body","district","crop","category","published_at","expires_at","notes"), ("title","body"), create_roles=("admin",), public_read=True, admin_managed=True, private=False),
    "family-helpers": S(("helper_user_id","scopes","status_note","expires_at"), ("helper_user_id","scopes")),
    "service-directory": S(("service_name","service_type","district","mandal","address_label","phone_public","hours","official_url","language_support"), ("service_name","service_type","district"), create_roles=("admin",), public_read=True, admin_managed=True, private=False),
    "livestock-fish-records": S(("farm_id","record_type","species","record_date","quantity","unit","cost","notes"), ("record_type","record_date"), has_farm=True),
    "crop-risk-reports": S(("farm_id","crop","crop_stage","risk_score","factors","computed_at","limitations"), ("crop","risk_score"), has_farm=True),
    "input-products": S(("product_name","category","brand","unit","notes"), ("product_name","category"), create_roles=("admin",), public_read=True, admin_managed=True, private=False),
    "harvest-plans": S(("farm_id","crop","target_window_start","target_window_end","labour_note","machinery_note","drying_note","storage_note","transport_note"), ("crop",), has_farm=True),
    "offline-drafts": S(("client_operation_id","entity_resource","draft_payload","device_saved_at"), ("client_operation_id","entity_resource","draft_payload")),
    "farm-observations": S(("farm_id","observation_date","crop","observation_type","description","severity","attachment_ids"), ("observation_date","observation_type","description"), has_farm=True),
    "benefit-tracking": S(("scheme_id","status_note","application_date","application_reference","documents","next_action","next_action_date"), ("scheme_id",)),
    "local-alerts": S(("alert_type","crop","district","approximate_area_label","severity","message","published_at","expires_at","notes"), ("alert_type","district","message"), create_roles=("admin","expert"), public_read=True, admin_managed=True, private=False),
    "source-records": S(("display_name","data_type_note","status_note","district","crop"), ("display_name",), create_roles=("admin",), admin_managed=True),
    "content-reports": S(("target_resource","target_id","reason","description","attachment_ids"), ("target_resource","target_id","reason"), create_roles=("farmer","expert","buyer","provider")),
}

PUBLIC_RESOURCE_SLUGS = {slug for slug, spec in RESOURCE_SPECS.items() if spec.public_read}
# Only these public views can be discovered without authentication.
PUBLIC_RESOURCE_SLUGS |= {"market-prices", "schemes", "storage-facilities", "equipment-listings", "fpo-directory", "service-directory", "notices", "disease-knowledge", "input-products", "local-alerts"}
