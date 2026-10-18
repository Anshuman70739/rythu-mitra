"""Dedicated-domain CRUD API with field allowlists, SQL ownership checks and moderation."""
from __future__ import annotations
from datetime import date, datetime, timezone
from urllib.parse import urlparse
import json
import math
import secrets
from flask import Blueprint, jsonify, request, session, current_app
from ..db import connect, utc_now, json_dump, json_load, RESOURCE_TABLES
from ..resources import RESOURCE_SPECS, PUBLIC_RESOURCE_SLUGS
from ..security import api_error, current_user, csrf_required, require_auth, valid_csrf, audit, json_body, text_field, number_field, rate_limit

bp=Blueprint("domains",__name__)

NUMERIC_FIELDS={"area_acres","budget","experience","quantity","cost","price","amount","N","P","K","ph","organic_carbon","electrical_conductivity","germination_label_pct","purity_pct","net_weight","mrp","tested_count","germinated_count","minimum_price","modal_price","maximum_price","arrival_quantity","distance_km","transport_per_km","principal_amount","interest_rate_apr","amount_repaid","installment_amount","estimated_capacity","duration_minutes","estimated_volume_liters","rainfall_mm","low_stock_threshold","purchase_price","workers_required","days","wage_per_day","actual_cost","age_months","pond_area_acres","milk_liters","price_per_liter","feed_cost","veterinary_cost","moisture_pct","damage_pct","capacity","cost_per_quintal_day","quantity_quintals","target_price","asking_price","risk_score","affected_area_acres","premium_amount","pond_area","fish_losses","starting_moisture_pct","final_moisture_pct"}
ARRAY_FIELDS={"documents","steps","districts","crops","packet_upload_ids","attachment_ids","evidence_upload_ids","image_ids","documents_submitted","scopes","factors"}
OBJECT_FIELDS={"draft_payload"}
BOOLEAN_FIELDS={"farmer_confirmed","anonymous","enabled","verified","available","verified_by_official"}
URL_FIELDS={"official_url","documentation_url","website_url","booking_url","source_url","external_url","complaint_url","application_url"}
NUMERIC_BOUNDS={
    "area_acres":(0.01,100000), "land_area":(0.01,100000), "budget":(0,100000000),
    "experience":(0,100), "ph":(0,14), "risk_score":(0,100),
    "germination_label_pct":(0,100), "purity_pct":(0,100), "moisture_pct":(0,100),
    "damage_pct":(0,100), "starting_moisture_pct":(0,100), "final_moisture_pct":(0,100),
    "interest_rate_apr":(0,100), "minimum_price":(0,100000000), "modal_price":(0,100000000),
    "maximum_price":(0,100000000), "price":(0,100000000), "amount":(0,100000000),
    "cost":(0,100000000), "purchase_price":(0,100000000), "principal_amount":(0,100000000),
    "installment_amount":(0,100000000), "target_price":(0,100000000), "asking_price":(0,100000000),
    "premium_amount":(0,100000000), "mrp":(0,100000000), "quantity_quintals":(0.001,100000000),
}
DATE_FIELDS={"test_date","price_date","purchase_date","packing_date","validity_date","sowing_date","application_date","next_action_date","expense_date","income_date","start_date","end_date","next_due_date","event_date","record_date","harvest_date","observation_date","due_date","reminder_at","published_at","expires_at","target_harvest_date","target_window_start","target_window_end","available_from","available_to","last_verified","last_maintenance_date","stocking_date","end_date","date_observed","created_at","updated_at"}
PROTECTED_PAYLOAD_FIELDS={"owner_id","user_id","farmer_id","role","password","password_hash","csrf_token","session_id","auth_token","api_key","secret_key","status","verified","verification_status","officially_filed","official_filing_status","official_submission_status","verified_by_platform","is_genuine","genuine","last_verified","created_by_role","reviewed_by_role","reviewed_at","reviewer_user_id"}
PUBLIC_STATUS={"ACTIVE","APPROVED","PUBLISHED","ANSWERED","COMPLETED"}
ADMIN_STATUS={"DRAFT","PENDING_REVIEW","ACTIVE","APPROVED","PUBLISHED","UNDER_REVIEW","SUSPENDED","BLOCKED","CLOSED","REJECTED","EXPIRED"}


def clean_payload(data:dict, resource:str, *, partial:bool=False):
    spec=RESOURCE_SPECS[resource]
    allowed=set(spec.fields)
    incoming=set(data)-{"csrf_token"}
    forbidden=incoming & PROTECTED_PAYLOAD_FIELDS
    if forbidden:
        raise ValueError(f"Protected field(s) cannot be supplied: {', '.join(sorted(forbidden))}.")
    unknown=incoming-allowed
    if unknown:
        raise ValueError(f"Unsupported field(s) for {resource}: {', '.join(sorted(unknown))}.")
    if not partial:
        missing=[field for field in spec.required if field not in data or data[field] in (None, "")]
        if missing: raise ValueError(f"Required field(s): {', '.join(missing)}.")
    out={}
    for key,value in data.items():
        if key=="csrf_token" or (partial and key not in allowed):
            continue
        if key not in allowed:
            continue
        if isinstance(value,str):
            value=value.strip()
            if len(value)>4000: raise ValueError(f"{key} is too long.")
        if key in NUMERIC_FIELDS and value is not None:
            if isinstance(value,bool): raise ValueError(f"{key} must be numeric.")
            try:value=float(value)
            except (TypeError,ValueError):raise ValueError(f"{key} must be numeric.")
            if not math.isfinite(value):raise ValueError(f"{key} must be finite.")
            if key in NUMERIC_BOUNDS:
                low,high=NUMERIC_BOUNDS[key]
                if not low<=value<=high:raise ValueError(f"{key} must be between {low} and {high}.")
            elif key in {"experience","workers_required","days","age_months","tested_count","germinated_count","quantity","quantity_quintals","fish_losses","distance_km","transport_per_km","estimated_capacity","duration_minutes","estimated_volume_liters","arrival_quantity","low_stock_threshold","workers_required","wage_per_day","actual_cost","milk_liters","price_per_liter","feed_cost","veterinary_cost","capacity","cost_per_quintal_day"} and value<0:
                raise ValueError(f"{key} cannot be negative.")
        if key in URL_FIELDS and value not in (None, ""):
            if not isinstance(value,str):raise ValueError(f"{key} must be an HTTPS URL.")
            parsed=urlparse(value)
            if parsed.scheme!="https" or not parsed.hostname or parsed.username or parsed.password or len(value)>500:
                raise ValueError(f"{key} must be an HTTPS URL without embedded credentials.")
        if key in BOOLEAN_FIELDS and value is not None and not isinstance(value,bool):
            if value in (0,1) and not isinstance(value,float): value=bool(value)
            else: raise ValueError(f"{key} must be true or false.")
        if key in ARRAY_FIELDS and value is not None and not isinstance(value,list):
            raise ValueError(f"{key} must be a list.")
        if key in OBJECT_FIELDS and value is not None and not isinstance(value,dict):
            raise ValueError(f"{key} must be a JSON object.")
        if isinstance(value,(dict,list)) and key not in ARRAY_FIELDS and key not in OBJECT_FIELDS:
            raise ValueError(f"{key} must be a scalar value, not a list or object.")
        if value is not None and key not in NUMERIC_FIELDS and key not in BOOLEAN_FIELDS and key not in ARRAY_FIELDS and key not in OBJECT_FIELDS and not isinstance(value,str):
            raise ValueError(f"{key} must be text.")
        if key in DATE_FIELDS and value not in (None,""):
            candidate=str(value)
            try:
                if "T" in candidate:datetime.fromisoformat(candidate.replace("Z","+00:00"))
                else:date.fromisoformat(candidate[:10])
            except ValueError:raise ValueError(f"{key} must be an ISO date or timestamp.")
        if isinstance(value,(dict,list)):
            # A single uploaded resource can include metadata and arrays, never megabytes of embedded images.
            if len(json_dump(value).encode("utf-8"))>12000:raise ValueError(f"{key} is too large; upload files separately.")
        out[key]=value
    if {"minimum_price","modal_price","maximum_price"}.issubset(out):
        if not 0 <= out["minimum_price"] <= out["modal_price"] <= out["maximum_price"]:
            raise ValueError("Prices must satisfy 0 <= minimum_price <= modal_price <= maximum_price.")
    if "packing_date" in out and "validity_date" in out and out["packing_date"] and out["validity_date"]:
        if date.fromisoformat(str(out["validity_date"])[:10]) < date.fromisoformat(str(out["packing_date"])[:10]):
            raise ValueError("validity_date cannot be earlier than packing_date.")
    if "risk_score" in out and not 0 <= out["risk_score"] <= 100:
        raise ValueError("risk_score must be between 0 and 100.")
    if "vote" in out and out["vote"] not in {"helpful", "not_helpful"}:
        raise ValueError("vote must be helpful or not_helpful.")
    if "complaint_type" in out and out["complaint_type"] not in {
        "poor_germination", "suspected_counterfeit", "misleading_claims", "missing_label",
        "qr_mismatch", "wrong_variety", "crop_failure", "dealer_refused_bill", "other"
    }:
        raise ValueError("Choose a supported complaint type.")
    if "severity" in out and out["severity"] not in {"low", "medium", "high", "critical", "LOW", "MEDIUM", "HIGH", "CRITICAL"}:
        raise ValueError("severity must be low, medium, high, or critical.")
    return out


def _row_payload(row):
    return json_load(row["payload_json"])


def _is_expired_payload(payload):
    expires=payload.get("expires_at")
    if not expires:return False
    try:return date.fromisoformat(str(expires)[:10]) < date.today()
    except ValueError:return True


PUBLIC_FIELDS = {
    "farmer-listings": {"crop","quantity","unit","quality_grade","asking_price","district","available_from"},
    "buyer-requests": {"crop","quantity","unit","quality_requirement","target_price","district","needed_by"},
    "community-posts": {"group_name","crop","district","post_type","body","experience_or_question"},
    "pest-reports": {"crop","pest_name","district","approximate_area_label","severity","observation_date","description"},
    "local-alerts": {"alert_type","crop","district","approximate_area_label","severity","message","published_at","expires_at","notes"},
    "notices": {"title","body","district","crop","category","published_at","expires_at"},
    "fpo-directory": {"name","district","crops","collection_centre","membership_process","official_url"},
    "market-prices": {"commodity","market","district","minimum_price","modal_price","maximum_price","arrival_quantity","arrival_unit","price_date","unit","distance_km","transport_per_km","notes"},
    "schemes": {"name","description","benefit","eligibility","documents","steps","official_url","districts","state","verification_notes"},
    "equipment-listings": {"name","equipment_type","provider_name","district","location_label","price","price_unit","available_from","available_to","availability_note"},
    "storage-facilities": {"name","facility_type","provider_name","district","location_label","capacity","capacity_unit","cost_per_quintal_day","crops","availability_note"},
    "service-directory": {"service_name","service_type","district","mandal","address_label","phone_public","hours","official_url","language_support"},
    "input-products": {"product_name","category","brand","unit","notes"},
    "disease-knowledge": {"crop","condition_name","symptoms","safe_guidance","notes"},
}


def _serialize(row, *, is_owner=False, is_admin=False, resource=None):
    body=_row_payload(row)
    if not is_owner and not is_admin:
        # Prefer resource-specific public fields where available. Private IDs and
        # contact details are removed even from user-generated public listings.
        if resource in PUBLIC_FIELDS:
            body={k:v for k,v in body.items() if k in PUBLIC_FIELDS[resource]}
        for key in ("phone","phone_number","address","full_address","contact","contact_method","email","helper_user_id","application_reference","policy_number","receipt_upload_id","sale_slip_upload_id","report_upload_id","upload_id","attachment_ids","packet_upload_ids","image_ids","evidence_upload_ids","qr_content","farm_id"):
            body.pop(key,None)
    result={"id":row["id"],"payload":body,"status":row["status"],"source_name":row["source_name"],"source_url":row["source_url"],"data_type":row["data_type"],"confidence":row["confidence"],"last_updated":row["last_updated"],"last_verified":row["last_verified"],"expires_at":row["expires_at"],"created_at":row["created_at"]}
    # Flatten allowlisted user-facing fields for frontend convenience while retaining the payload object.
    result.update(body)
    return result


def _public_filter(resource, user):
    spec=RESOURCE_SPECS[resource]
    if user and user["role"]=="admin":return "1=1",()
    if user and resource=="expert-questions" and user["role"]=="expert":
        return "(owner_id=? OR status IN ('SUBMITTED','ANSWERED','APPROVED'))",(user["id"],)
    if user:
        return "(owner_id=? OR (owner_id IS NULL AND status IN ('ACTIVE','APPROVED','PUBLISHED'))) ",(user["id"],)
    if spec.public_read:
        return "owner_id IS NULL AND status IN ('ACTIVE','APPROVED','PUBLISHED')",()
    return None,()


def _validate_farm(data, user_id, role):
    farm_id=data.get("farm_id")
    if not farm_id:return None
    with connect() as conn:
        row=conn.execute("SELECT id FROM farms WHERE id=? AND owner_id=? AND status!='DELETED'",(str(farm_id),user_id)).fetchone()
    if row is None:
        raise ValueError("farm_id must identify a farm owned by your account.")
    return str(farm_id)


def _create(resource, data, user, record_owner_id=None):
    spec=RESOURCE_SPECS[resource]
    if user["role"] not in spec.create_roles:
        raise PermissionError("Your account role cannot create this resource.")
    record_owner_id = int(record_owner_id if record_owner_id is not None else user["id"])
    if resource == "family-helpers" and record_owner_id != user["id"]:
        raise PermissionError("Only the account owner may invite a helper.")
    raw=dict(data)
    metadata={}
    if spec.admin_managed and user["role"]=="admin":
        for meta_key in ("source_name","source_url","last_verified"):
            if meta_key in raw: metadata[meta_key]=raw.pop(meta_key)
    values=clean_payload(raw,resource)
    if resource == "seed-complaint-events":
        event_type=str(values.get("event_type", "")).strip().upper()
        allowed_by_role={
            "farmer":{"EVIDENCE_ADDED","FOLLOW_UP_NOTE","EXTERNAL_REFERENCE_REPORTED"},
            "expert":{"EVIDENCE_ADDED","FOLLOW_UP_NOTE","EXPERT_REVIEW_NOTE"},
            "admin":{"EVIDENCE_ADDED","FOLLOW_UP_NOTE","EXTERNAL_REFERENCE_REPORTED","EXPERT_REVIEW_NOTE","ADMIN_REVIEW_NOTE"},
        }
        if event_type not in allowed_by_role.get(user["role"], set()):
            raise ValueError("Unsupported complaint event for this account role. A user-reported external reference does not mean Rythu Mitra filed a complaint.")
        values["event_type"] = event_type
        values["created_by_role"] = user["role"]
        if event_type == "EXTERNAL_REFERENCE_REPORTED" and not str(values.get("official_reference") or "").strip():
            raise ValueError("Enter the reference supplied to you by the authority; this is a user-reported reference only.")
    if resource == "disease-reviews":
        with connect() as conn:
            scan=conn.execute("SELECT id,owner_id,upload_id FROM disease_scan_history WHERE id=? AND owner_id IS NOT NULL",(str(values.get("scan_id")),)).fetchone()
            question=conn.execute("SELECT id,owner_id,status,payload_json FROM expert_questions WHERE id=? AND status IN ('SUBMITTED','ANSWERED','APPROVED')",(str(values.get("question_id")),)).fetchone()
        if scan is None or question is None or scan["owner_id"] != question["owner_id"]:
            raise ValueError("The scan and expert question must belong to the same farmer account.")
        question_payload=json_load(question["payload_json"])
        attached=question_payload.get("attachment_ids",[])
        if not scan["upload_id"] or not isinstance(attached,list) or str(scan["upload_id"]) not in {str(x) for x in attached}:
            raise ValueError("The farmer must explicitly attach the scan image to the expert question before a review can be recorded.")
        assessment=values.get("assessment")
        if assessment not in {"MODEL_RESULT_PLAUSIBLE","MODEL_RESULT_UNCERTAIN","POSSIBLE_ALTERNATE_CAUSE","FIELD_VISIT_RECOMMENDED","UNABLE_TO_ASSESS"}:
            raise ValueError("Choose a supported preliminary expert-review assessment.")
        values["reviewed_by_role"]="expert"
        values["reviewer_user_id"]=user["id"]
        values["reviewed_at"]=utc_now()
        values["review_limitations"]="Expert review of submitted evidence is not laboratory confirmation or an official disease certificate."
    farm_id=_validate_farm(values,record_owner_id,user["role"]) if "farm_id" in spec.fields else None
    # Upload IDs are server-issued references, never raw filesystem paths. Enforce ownership.
    attachment_fields=("attachment_ids","packet_upload_ids","image_ids","evidence_upload_ids")
    upload_ids=[]
    for field in attachment_fields:
        candidate=values.get(field)
        if isinstance(candidate,list):upload_ids.extend(str(x) for x in candidate)
    for field in ("receipt_upload_id","report_upload_id","sale_slip_upload_id"):
        candidate=values.get(field)
        if candidate:upload_ids.append(str(candidate))
    if upload_ids:
        if any(len(x)>64 or not x.isalnum() for x in upload_ids):raise ValueError("Upload references are invalid.")
        placeholders=','.join('?' for _ in set(upload_ids))
        with connect() as conn:
            found={row[0] for row in conn.execute(f"SELECT id FROM uploads WHERE owner_id=? AND id IN ({placeholders})",(record_owner_id,*set(upload_ids))).fetchall()}
        if found!=set(upload_ids):raise ValueError("Every attachment must be uploaded by this account first.")
    # Parent references must be owned or legitimately public; never trust a client ID alone.
    if values.get("seed_lot_id"):
        with connect() as conn:
            row=conn.execute("SELECT id FROM seed_lots WHERE id=? AND owner_id=? AND status!='DELETED'",(str(values["seed_lot_id"]),record_owner_id)).fetchone()
        if row is None:raise ValueError("seed_lot_id must refer to a seed lot you own.")
    # Validate parent objects at the database boundary, not just by trusting an ID.
    parent_relations = {
        "scheme-documents": ("scheme_id", "schemes", True),
        "scheme-tracking": ("scheme_id", "schemes", True),
        "benefit-tracking": ("scheme_id", "schemes", True),
        "storage-bookings": ("facility_id", "storage-facilities", True),
        "equipment-bookings": ("listing_id", "equipment-listings", True),
        "produce-quality": ("harvest_id", "harvest-records", False),
        "drying-records": ("harvest_id", "harvest-records", False),
        "livestock-health": ("livestock_id", "livestock", False),
        "dairy-records": ("livestock_id", "livestock", False),
        "seed-complaint-events": ("complaint_id", "seed-complaints", False),
        "irrigation-records": ("water_source_id", "water-sources", False),
    }
    if resource in parent_relations:
        field, parent_resource, allow_public = parent_relations[resource]
        parent_id = values.get(field)
        if parent_id not in (None, ""):
            parent_table = RESOURCE_TABLES[parent_resource]
            with connect() as conn:
                parent = conn.execute(f"SELECT id,owner_id,status FROM {parent_table} WHERE id=? AND status!='DELETED'", (str(parent_id),)).fetchone()
            allowed = bool(parent and parent["owner_id"] == record_owner_id)
            if parent and allow_public and parent["status"] in PUBLIC_STATUS:
                allowed = True
            if resource == "seed-complaint-events" and parent and user["role"] in {"expert", "admin"} and parent["status"] in {"USER_REPORTED", "EVIDENCE_ADDED", "UNDER_REVIEW"}:
                allowed = True
            if not allowed:
                raise ValueError(f"{field} must refer to a record you own or are allowed to update.")
    if resource == "expert-answers":
        question_id = values.get("question_id")
        with connect() as conn:
            question = conn.execute("SELECT id,status FROM expert_questions WHERE id=? AND status IN ('SUBMITTED','ANSWERED','APPROVED')", (str(question_id),)).fetchone()
        if question is None:
            raise ValueError("question_id must identify an available submitted expert question.")
    if resource == "expert-votes":
        answer_id = values.get("answer_id")
        with connect() as conn:
            answer = conn.execute("SELECT id,payload_json FROM expert_answers WHERE id=? AND status!='DELETED'", (str(answer_id),)).fetchone()
        if answer is None or str(json_load(answer["payload_json"]).get("question_id")) != str(values.get("question_id")):
            raise ValueError("answer_id must belong to the supplied question_id.")
        with connect() as conn:
            question=conn.execute("SELECT owner_id FROM expert_questions WHERE id=?",(str(values.get("question_id")),)).fetchone()
        if question is None or question["owner_id"] != record_owner_id:
            raise ValueError("You may vote only on an answer to your own question.")
    if values.get("helper_user_id"):
        if resource!="family-helpers":raise ValueError("Unsupported helper relationship.")
        try:helper_id=int(values["helper_user_id"])
        except (TypeError,ValueError):raise ValueError("helper_user_id must be a registered user id.")
        if helper_id==user["id"]:raise ValueError("You cannot add your own account as a helper.")
        with connect() as conn:
            helper=conn.execute("SELECT id,role FROM users WHERE id=?",(helper_id,)).fetchone()
        if helper is None or helper["role"] != "farmer":raise ValueError("The helper must have a registered farmer account.")
        values["helper_user_id"]=helper_id
        scopes=values.get("scopes",[])
        if not isinstance(scopes,list) or not scopes or any(s not in {"view_dashboard","add_expenses","add_farm_diary"} for s in scopes):
            raise ValueError("scopes must include one or more supported limited permissions.")
        values["consent_at"]=None
    if resource == "content-reports":
        target_resource=values.get("target_resource")
        if target_resource not in RESOURCE_SPECS:
            raise ValueError("target_resource must be a supported Rythu Mitra resource.")
        target_id=str(values.get("target_id") or "")
        if not target_id or len(target_id)>64:
            raise ValueError("target_id must be a valid record identifier.")
        target_table=RESOURCE_TABLES[target_resource]
        with connect() as conn:
            target=conn.execute(f"SELECT id FROM {target_table} WHERE id=? AND status!='DELETED'",(target_id,)).fetchone()
        if target is None:
            raise ValueError("The reported content was not found.")
        values["status_note"]="Submitted for moderator review; not yet actioned."
    if resource=="seed-test-results":
        tested=values.get("tested_count");germinated=values.get("germinated_count")
        if tested is None or germinated is None or tested<1 or germinated>tested or int(tested)!=tested or int(germinated)!=germinated:
            raise ValueError("Use whole counts; tested_count must be positive and germinated_count cannot exceed it.")
        values["calculated_germination_pct"]=round(germinated/tested*100,2)
        values["screening_label"]="Informal home screening — not official laboratory certification"
    if resource=="seed-scans":
        values["verification_status"]="UNVERIFIED"
        values["label_completeness"]=_label_completeness(values)
        values["authenticity_claim"]="NOT_DETERMINED_FROM_IMAGE_OR_QR"
        values["user_confirmation_required"]=True
    if resource=="seed-complaints":
        values["complaint_number"]="RM-SEED-"+secrets.token_hex(4).upper()
        values["official_filing_status"]="NOT_FILED_BY_PLATFORM"
        values["timeline"]=[{"status":"USER_REPORTED","at":utc_now(),"note":"Saved inside Rythu Mitra; not submitted to a government authority."}]
    if resource=="crop-damage-reports":
        values["report_number"]="RM-DMG-"+secrets.token_hex(4).upper()
        values["official_submission_status"]="NOT_FILED_BY_PLATFORM"
    if resource=="complaints":
        values["complaint_number"]="RM-GRV-"+secrets.token_hex(4).upper()
        values["official_filing_status"]="NOT_FILED_BY_PLATFORM"
    if resource=="family-helpers":
        initial_status="PENDING_CONSENT"
    elif resource == "crop-tasks":
        due = values.get("due_date")
        try:
            due_day = date.fromisoformat(str(due)[:10]) if due else None
        except ValueError:
            due_day = None
        initial_status = "UPCOMING" if due_day and due_day > date.today() else "OVERDUE" if due_day and due_day < date.today() else "DUE"
    elif resource == "disease-reviews":
        initial_status="EXPERT_REVIEWED"
    elif resource in {"market-prices","schemes","market-sources","disease-knowledge","scheme-documents","storage-facilities","equipment-listings","fpo-directory","notices","service-directory","input-products","local-alerts","source-records"}:
        initial_status="DRAFT" if user["role"]=="admin" else "PENDING_REVIEW"
    elif resource in {"seed-complaints","complaints","crop-damage-reports","expert-questions","market-feedback","pest-reports","community-posts","farmer-listings","buyer-requests","storage-bookings","equipment-bookings","content-reports"}:
        initial_status="USER_REPORTED" if resource in {"seed-complaints","complaints","crop-damage-reports"} else "SUBMITTED"
    else:
        initial_status="ACTIVE"
    # User-entered source metadata is generated server-side. Admin-managed resources
    # start as CURATED drafts and must be moderated before public display.
    data_type="CURATED" if user["role"]=="admin" and spec.admin_managed else "USER_SUBMITTED"
    source_name="Admin-curated (pending verification)" if data_type=="CURATED" else "User supplied"
    source_url=None;last_verified=None
    if spec.admin_managed and user["role"]=="admin":
        source_name=str(data.get("source_name") or source_name)[:160]
        s_url=data.get("source_url")
        if s_url:
            if not isinstance(s_url,str) or not s_url.startswith("https://") or len(s_url)>500:raise ValueError("source_url must be an HTTPS URL.")
            source_url=s_url
        last_verified=data.get("last_verified")
        if last_verified is not None:
            try: date.fromisoformat(str(last_verified)[:10])
            except ValueError: raise ValueError("last_verified must be an ISO date.")
    # If URL metadata was supplied, don't store it as farmer-controlled content.
    values.pop("source_name",None) if "source_name" in values and "source_name" not in spec.fields else None
    stamp=utc_now();row_id=secrets.token_urlsafe(18).replace("-", "").replace("_", "")[:24]
    table=RESOURCE_TABLES[resource]
    with connect() as conn:
        conn.execute(f"INSERT INTO {table}(id,owner_id,farm_id,payload_json,status,source_name,source_url,data_type,last_updated,last_verified,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            (row_id,record_owner_id,farm_id,json_dump(values),initial_status,source_name,source_url,data_type,stamp,last_verified,stamp,stamp))
    if resource in {"expert-answers", "disease-reviews"}:
        with connect() as conn:
            conn.execute("UPDATE expert_questions SET status='ANSWERED',last_updated=?,updated_at=? WHERE id=? AND status IN ('SUBMITTED','ANSWERED','APPROVED')", (stamp,stamp,str(values.get("question_id"))))
    if resource == "seed-complaint-events":
        with connect() as conn:
            parent=conn.execute("SELECT payload_json,status FROM seed_complaints WHERE id=?", (str(values.get("complaint_id")),)).fetchone()
            if parent:
                parent_payload=json_load(parent["payload_json"])
                timeline=parent_payload.get("timeline",[])
                if not isinstance(timeline,list): timeline=[]
                timeline.append({"status":str(values.get("event_type"))[:50],"at":stamp,"note":str(values.get("description", ""))[:500],"official_reference":None})
                parent_payload["timeline"]=timeline[-50:]
                conn.execute("UPDATE seed_complaints SET payload_json=?,last_updated=?,updated_at=? WHERE id=?",(json_dump(parent_payload),stamp,stamp,str(values.get("complaint_id"))))
    audit("resource_created",resource,user["id"],{"id":row_id,"status":initial_status})
    with connect() as conn:row=conn.execute(f"SELECT * FROM {table} WHERE id=?",(row_id,)).fetchone()
    return row


def _label_completeness(payload):
    required=("crop","variety","brand","lot_number","packing_date","validity_date","germination_label_pct","mrp")
    missing=[k for k in required if payload.get(k) in (None,"")]
    return {"status":"LABEL_INCOMPLETE" if missing else "LABEL_INFORMATION_APPEARS_COMPLETE","missing_fields":missing,"note":"Completeness is not proof of authenticity, purity, germination, or legal certification."}


def _owner_ids(user, resource, action="read"):
    ids=[user["id"]]
    if resource=="family-helpers":return ids
    with connect() as conn:
        rows=conn.execute(f"SELECT owner_id,payload_json FROM {RESOURCE_TABLES['family-helpers']} WHERE status='ACCEPTED'").fetchall()
    for row in rows:
        payload=json_load(row["payload_json"])
        try:helper_id=int(payload.get("helper_user_id"))
        except (TypeError,ValueError):continue
        scopes=payload.get("scopes",[])
        expires=payload.get("expires_at")
        if expires:
            try:
                if date.fromisoformat(str(expires)[:10]) < date.today(): continue
            except ValueError:
                continue
        if helper_id!=user["id"]:continue
        if action=="read" and "view_dashboard" in scopes and resource in {"farms","farm-plots","crop-tasks","farm-diary","soil-records","expenses","income","harvest-records"}:
            ids.append(row["owner_id"])
        if action=="create" and "add_expenses" in scopes and resource in {"expenses"}:
            ids.append(row["owner_id"])
        if action=="create" and "add_farm_diary" in scopes and resource in {"farm-diary"}:
            ids.append(row["owner_id"])
    return sorted(set(ids))


@bp.get("/api/v1/<resource>")
def list_resource(resource):
    if resource not in RESOURCE_SPECS:return api_error("Unknown resource.",404)
    spec=RESOURCE_SPECS[resource];user=current_user()
    if not spec.public_read and user is None:return api_error("Please sign in to access this resource.",401)
    try:
        limit=max(1,min(int(request.args.get("limit",50) or 50),100))
        offset=max(0,min(int(request.args.get("offset",0) or 0),100000))
    except (TypeError,ValueError):
        return api_error("limit and offset must be integers.")
    term=(request.args.get("q") or "").strip().casefold()[:100]
    table=RESOURCE_TABLES[resource]
    clauses=["status!='DELETED'"];params=[]
    if resource == "family-helpers" and user is not None and user["role"] != "admin":
        clauses.append("(owner_id=? OR json_extract(payload_json,'$.helper_user_id')=?)")
        params.extend((user["id"], user["id"]))
    elif user and user["role"]=="admin":
        pass
    elif user and resource=="expert-questions" and user["role"]=="expert":
        clauses.append("(owner_id=? OR status IN ('SUBMITTED','ANSWERED','APPROVED'))");params.append(user["id"])
    elif user:
        owner_ids=_owner_ids(user,resource,"read")
        placeholders=','.join('?' for _ in owner_ids)
        if spec.public_read:clauses.append(f"(owner_id IN ({placeholders}) OR status IN ('ACTIVE','APPROVED','PUBLISHED'))")
        else:clauses.append(f"owner_id IN ({placeholders})")
        params.extend(owner_ids)
    elif spec.public_read:
        clauses.append("status IN ('ACTIVE','APPROVED','PUBLISHED')")
    else:return api_error("Please sign in to access this resource.",401)
    status_filter=(request.args.get("status") or "").strip().upper()
    if status_filter and status_filter in ADMIN_STATUS | {"ACTIVE","SUBMITTED","USER_REPORTED","PENDING_CONSENT","COMPLETED","UPCOMING","DUE","OVERDUE","SKIPPED","CANCELLED","ANSWERED"}:
        clauses.append("status=?");params.append(status_filter)
    sql=f"SELECT * FROM {table} WHERE {' AND '.join(clauses)} ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend((limit,offset))
    with connect() as conn:rows=conn.execute(sql,tuple(params)).fetchall()
    result=[]
    for row in rows:
        payload=_row_payload(row)
        if spec.public_read and _is_expired_payload(payload):
            continue
        owner=(user is not None and row["owner_id"]==user["id"])
        is_admin=user is not None and user["role"]=="admin"
        item=_serialize(row,is_owner=owner,is_admin=is_admin,resource=resource)
        if term and term not in json_dump(item).casefold():continue
        result.append(item)
    return jsonify(success=True,resource=resource,records=result,count=len(result),limit=limit,offset=offset,data_type="MIXED" if len({x["data_type"] for x in result})>1 else (result[0]["data_type"] if result else "UNAVAILABLE"))


@bp.post("/api/v1/<resource>")
@csrf_required
@require_auth()
@rate_limit(12, 60)
def create_resource(resource):
    if resource not in RESOURCE_SPECS:return api_error("Unknown resource.",404)
    data,error=json_body()
    if error:return error
    user=current_user()
    try:
        owner_ids=_owner_ids(user,resource,"create")
        effective_owner=user["id"]
        if resource!="family-helpers":
            delegated=[owner_id for owner_id in owner_ids if owner_id!=user["id"]]
            if delegated:
                farm_id=data.get("farm_id")
                if farm_id:
                    with connect() as conn:
                        farm=conn.execute("SELECT owner_id FROM farms WHERE id=? AND owner_id IN ("+",".join("?" for _ in delegated)+") AND status!='DELETED'",(str(farm_id),*delegated)).fetchone()
                    if farm is None: raise PermissionError("Select a farm owned by the family account that granted this helper permission.")
                    effective_owner=farm["owner_id"]
                elif len(delegated)==1 and resource in {"expenses","farm-diary"}:
                    effective_owner=delegated[0]
                else:
                    raise PermissionError("Choose the owner's farm to identify which family account this change belongs to.")
        row=_create(resource,data,user,record_owner_id=effective_owner)
        owner=row["owner_id"]==user["id"]
        return jsonify(success=True,record=_serialize(row,is_owner=owner,is_admin=user["role"]=="admin",resource=resource),message="Saved in Rythu Mitra; no external authority was notified." if resource in {"seed-complaints","complaints","crop-damage-reports","insurance-claims"} else "Record saved."),201
    except PermissionError as exc:return api_error(str(exc),403)
    except ValueError as exc:return api_error(str(exc))


@bp.get("/api/v1/<resource>/<string:resource_id>")
def get_resource(resource,resource_id):
    if resource not in RESOURCE_SPECS:return api_error("Unknown resource.",404)
    spec=RESOURCE_SPECS[resource];user=current_user();table=RESOURCE_TABLES[resource]
    if user is None and not spec.public_read:return api_error("Please sign in.",401)
    with connect() as conn:row=conn.execute(f"SELECT * FROM {table} WHERE id=? AND status!='DELETED'",(resource_id,)).fetchone()
    if row is None:return api_error("Record not found.",404)
    owner=user is not None and row["owner_id"]==user["id"]
    admin=user is not None and user["role"]=="admin"
    public=spec.public_read and row["status"] in PUBLIC_STATUS and not _is_expired_payload(_row_payload(row))
    expert_can_read=resource=="expert-questions" and user is not None and user["role"]=="expert" and row["status"] in {"SUBMITTED","ANSWERED","APPROVED"}
    helper_can_read=user is not None and row["owner_id"] in _owner_ids(user,resource,"read")
    if resource == "family-helpers" and user is not None:
        helper_can_read = helper_can_read or str(_row_payload(row).get("helper_user_id")) == str(user["id"])
    if not (owner or admin or public or expert_can_read or helper_can_read):return api_error("Record not found.",404)
    output=_serialize(row,is_owner=owner,is_admin=admin,resource=resource)
    if resource == "expert-questions" and owner:
        answer_table=RESOURCE_TABLES["expert-answers"]
        with connect() as conn:
            answer_rows=conn.execute(f"SELECT * FROM {answer_table} WHERE status!='DELETED' ORDER BY created_at ASC").fetchall()
        answers=[]
        for answer_row in answer_rows:
            answer_payload=json_load(answer_row["payload_json"])
            if str(answer_payload.get("question_id")) == str(resource_id):
                answers.append(_serialize(answer_row,is_owner=False,resource="expert-answers"))
        output["answers"]=answers
    return jsonify(success=True,record=output)


@bp.patch("/api/v1/<resource>/<string:resource_id>")
@csrf_required
@require_auth()
@rate_limit(20, 60)
def patch_resource(resource,resource_id):
    if resource not in RESOURCE_SPECS:return api_error("Unknown resource.",404)
    data,error=json_body()
    if error:return error
    user=current_user();table=RESOURCE_TABLES[resource]
    with connect() as conn:row=conn.execute(f"SELECT * FROM {table} WHERE id=? AND owner_id=? AND status!='DELETED'",(resource_id,user["id"])).fetchone()
    if row is None:return api_error("Record not found or not owned by this account.",404)
    body=dict(data)
    body.pop("status",None)
    if resource == "family-helpers" and ({"helper_user_id","scopes","consent_at"} & set(body)):
        return api_error("Helper identity, consent and permissions cannot be changed in place. Revoke the invite and create a new one.")
    try:updates=clean_payload(body,resource,partial=True)
    except ValueError as exc:return api_error(str(exc))
    if not updates and "status" not in data:return api_error("No supported changes were supplied.")
    old=_row_payload(row);old.update(updates)
    if "farm_id" in updates:_validate_farm(old,user["id"],user["role"])
    # A PATCH must obey the same private-attachment rules as creation.
    upload_ids=[]
    for field in ("attachment_ids","packet_upload_ids","image_ids","evidence_upload_ids"):
        values=old.get(field)
        if isinstance(values,list):upload_ids.extend(str(value) for value in values)
    for field in ("receipt_upload_id","report_upload_id","sale_slip_upload_id","upload_id"):
        if old.get(field):upload_ids.append(str(old[field]))
    if upload_ids:
        if any(len(x)>64 or not x.isalnum() for x in upload_ids):return api_error("Upload references are invalid.")
        placeholders=','.join('?' for _ in set(upload_ids))
        with connect() as conn:
            found={item[0] for item in conn.execute(f"SELECT id FROM uploads WHERE owner_id=? AND id IN ({placeholders})",(user["id"],*set(upload_ids))).fetchall()}
        if found!=set(upload_ids):return api_error("Every attachment must be uploaded by this account first.",403)
    if "seed_lot_id" in updates:
        with connect() as conn:
            found=conn.execute("SELECT id FROM seed_lots WHERE id=? AND owner_id=? AND status!='DELETED'",(str(updates["seed_lot_id"]),user["id"])).fetchone()
        if not found:return api_error("seed_lot_id must refer to a seed lot you own.",403)
    new_status=row["status"]
    if "status" in data:
        requested=str(data["status"]).upper()
        allowed={"crop-tasks":{"UPCOMING","DUE","OVERDUE","COMPLETED","SKIPPED"},"storage-bookings":{"SUBMITTED","CANCELLED"},"equipment-bookings":{"SUBMITTED","CANCELLED"},"farmer-listings":{"SUBMITTED","CLOSED"},"buyer-requests":{"SUBMITTED","CLOSED"},"seed-complaints":{"EVIDENCE_ADDED","CANCELLED"},"complaints":{"EVIDENCE_ADDED","CANCELLED"},"crop-damage-reports":{"EVIDENCE_ADDED","CANCELLED"},"scheme-tracking":{"DRAFT","SUBMITTED_TO_AUTHORITY","IN_PROGRESS","EXTERNAL_STATUS_REPORTED","NEEDS_ACTION","CANCELLED"},"family-helpers":{"REVOKED","CANCELLED"}}
        if requested not in allowed.get(resource,set()):return api_error("This status transition is not allowed for this resource.")
        new_status=requested
        if resource == "crop-tasks":
            if requested == "COMPLETED": old["completed_at"] = utc_now()
            elif requested in {"UPCOMING","DUE","OVERDUE","SKIPPED"}: old.pop("completed_at", None)
    with connect() as conn:
        conn.execute(f"UPDATE {table} SET payload_json=?,status=?,last_updated=?,updated_at=? WHERE id=? AND owner_id=?",(json_dump(old),new_status,utc_now(),utc_now(),resource_id,user["id"]))
        updated=conn.execute(f"SELECT * FROM {table} WHERE id=? AND owner_id=?",(resource_id,user["id"])).fetchone()
    audit("resource_updated",resource,user["id"],{"id":resource_id,"fields":sorted(updates),"status":new_status})
    return jsonify(success=True,record=_serialize(updated,is_owner=True,resource=resource))


@bp.delete("/api/v1/<resource>/<string:resource_id>")
@csrf_required
@require_auth()
@rate_limit(10, 60)
def delete_resource(resource,resource_id):
    if resource not in RESOURCE_SPECS:return api_error("Unknown resource.",404)
    user=current_user();table=RESOURCE_TABLES[resource]
    with connect() as conn:
        row=conn.execute(f"SELECT id FROM {table} WHERE id=? AND owner_id=? AND status!='DELETED'",(resource_id,user["id"])).fetchone()
        if row is None:return api_error("Record not found or not owned by this account.",404)
        conn.execute(f"UPDATE {table} SET status='DELETED',last_updated=?,updated_at=? WHERE id=? AND owner_id=?",(utc_now(),utc_now(),resource_id,user["id"]))
    audit("resource_soft_deleted",resource,user["id"],{"id":resource_id})
    return jsonify(success=True,status="DELETED",message="Record was archived, not physically erased.")


@bp.post("/api/v1/family-helpers/<string:invite_id>/accept")
@csrf_required
@require_auth()
def accept_helper(invite_id):
    user=current_user();table=RESOURCE_TABLES["family-helpers"]
    with connect() as conn:row=conn.execute(f"SELECT * FROM {table} WHERE id=? AND status='PENDING_CONSENT'",(invite_id,)).fetchone()
    if row is None:return api_error("Invitation not found or no longer pending.",404)
    payload=_row_payload(row)
    if str(payload.get("helper_user_id"))!=str(user["id"]):return api_error("Only the invited helper can accept this invitation.",403)
    scopes=payload.get("scopes",[])
    payload["consent_at"]=utc_now()
    with connect() as conn:
        conn.execute(f"UPDATE {table} SET payload_json=?,status='ACCEPTED',last_updated=?,updated_at=? WHERE id=? AND status='PENDING_CONSENT'",(json_dump(payload),utc_now(),utc_now(),invite_id))
        updated=conn.execute(f"SELECT * FROM {table} WHERE id=?",(invite_id,)).fetchone()
    audit("family_helper_consent", invite_id, user["id"], {"scopes":scopes})
    return jsonify(success=True,record=_serialize(updated,is_owner=False,resource="family-helpers"))


@bp.post("/api/admin/resources/<resource>/<string:resource_id>/moderate")
@csrf_required
@require_auth(("admin",))
def moderate_resource(resource,resource_id):
    if resource not in RESOURCE_SPECS:return api_error("Unknown resource.",404)
    data,error=json_body()
    if error:return error
    status=str(data.get("status","")).strip().upper()
    if status not in ADMIN_STATUS:return api_error("Unsupported moderation status.")
    source_name=data.get("source_name")
    source_url=data.get("source_url")
    last_verified=data.get("last_verified")
    if source_name is not None and (not isinstance(source_name,str) or not source_name.strip() or len(source_name)>160):return api_error("source_name must be 1–160 characters.")
    if source_url is not None and source_url and (not isinstance(source_url,str) or not source_url.startswith("https://") or len(source_url)>500):return api_error("source_url must be an HTTPS URL.")
    if last_verified is not None:
        try:date.fromisoformat(str(last_verified)[:10])
        except ValueError:return api_error("last_verified must be an ISO date.")
    table=RESOURCE_TABLES[resource]
    with connect() as conn:
        row=conn.execute(f"SELECT id FROM {table} WHERE id=?",(resource_id,)).fetchone()
        if row is None:return api_error("Record not found.",404)
        conn.execute(f"UPDATE {table} SET status=?,source_name=COALESCE(?,source_name),source_url=COALESCE(?,source_url),last_verified=COALESCE(?,last_verified),last_updated=?,updated_at=? WHERE id=?",(status,source_name.strip() if isinstance(source_name,str) else None,source_url if source_url else None,last_verified,utc_now(),utc_now(),resource_id))
        updated=conn.execute(f"SELECT * FROM {table} WHERE id=?",(resource_id,)).fetchone()
    audit("resource_moderated",resource,session.get("user_id"),{"id":resource_id,"status":status})
    return jsonify(success=True,record=_serialize(updated,is_admin=True,resource=resource))
