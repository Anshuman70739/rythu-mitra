"""Core auth, dashboard, crop/weather, market, and calculator APIs."""
from __future__ import annotations
from datetime import datetime, timezone, date
import json
import math
import secrets
from flask import Blueprint, current_app, jsonify, request, session, render_template
from werkzeug.security import check_password_hash, generate_password_hash
from ..db import connect, utc_now, json_dump, json_load, RESOURCE_TABLES
from ..security import api_error, current_user, public_user, require_auth, csrf_required, rate_limit, audit, json_body, text_field, number_field
from ..services.weather import get_weather
from ..services.models import predict_crop, has_model_asset, has_disease_model_bundle
from ..services.markets import fetch_configured_provider

bp = Blueprint("core", __name__)
PROFILE_TEXT_FIELDS = {"name":120,"language":2,"district":80,"mandal":80,"village":80,"soil_type":100,"irrigation":100,"current_crop":100,"crop_stage":100,"previous_crop":100,"season":50}
PROFILE_NUM_FIELDS = {"land_area":(0.01,100000),"budget":(0,100000000),"experience":(0,100)}


def model_fertilizer_reference(n: float, p: float, k: float) -> list[str]:
    items = []
    if n < 50: items.append("Measured N is below this simple reference threshold; confirm units and Soil Health Card before any input decision.")
    elif n > 100: items.append("Measured N is above this simple reference threshold; do not add more without qualified local advice.")
    if p < 40: items.append("Measured P is below this reference threshold; confirm laboratory units and local recommendation.")
    if k < 40: items.append("Measured K is below this reference threshold; confirm laboratory units and local recommendation.")
    return items or ["No alert from the simple reference thresholds. This is not a fertilizer prescription."]


def _count(table: str, where: str = "1=1", params: tuple = ()) -> int:
    if table not in set(RESOURCE_TABLES.values()) | {"users", "notifications", "legacy_records"}:
        return 0
    with connect() as conn:
        return int(conn.execute(f"SELECT COUNT(*) FROM {table} WHERE {where}", params).fetchone()[0])


@bp.get("/")
def home():
    # Backend-first bundle can be tested without a frontend template. Once the
    # approved frontend is integrated, render it automatically.
    for candidate in ("rythu_mitra.html", "index.html"):
        try:
            current_app.jinja_env.get_template(candidate)
            return render_template(candidate, csrf_token=session.get("csrf_token", ""))
        except Exception:
            continue
    return jsonify(service="Rythu Mitra backend", api_prefix="/api/v1", health="/health", message="Backend is running. Integrate the approved frontend template to display the full website.")


@bp.get("/privacy-policy")
def privacy_policy():
    """Serve the project-specific privacy information page."""
    return render_template("privacy_policy.html")


@bp.get("/terms-and-conditions")
def terms_and_conditions():
    """Serve the project-specific terms page."""
    return render_template("terms_and_conditions.html")


@bp.get("/api/session")
def session_info():
    return jsonify(success=True, user=public_user(current_user()), csrf_token=session.get("csrf_token"), demo_mode=bool(current_app.config["DEMO_MODE"]))


@bp.post("/api/register")
@csrf_required
@rate_limit(5, 300)
def register():
    data, error = json_body()
    if error: return error
    try:
        name = text_field(data, "name", required=True, max_length=120)
        phone = text_field(data, "phone", required=True, max_length=15)
        password = text_field(data, "password", required=True, max_length=256)
        role = text_field(data, "role", default="farmer", max_length=20) or "farmer"
        language = text_field(data, "language", default="en", max_length=2) or "en"
        if not phone.isdigit() or not 8 <= len(phone) <= 15: raise ValueError("Enter a valid phone number.")
        if len(password) < 8: raise ValueError("Password must contain at least 8 characters.")
        if role not in {"farmer", "buyer"}: raise ValueError("Self-registration is limited to farmer and buyer accounts.")
        if language not in {"en", "te"}: raise ValueError("Language must be en or te.")
    except ValueError as exc:
        return api_error(str(exc))
    stamp = utc_now()
    try:
        with connect() as conn:
            cur = conn.execute("INSERT INTO users(name,phone,role,password_hash,language,created_at,updated_at) VALUES(?,?,?,?,?,?,?)",
                (name, phone, role, generate_password_hash(password), language, stamp, stamp))
            user_id = cur.lastrowid
        session.clear()
        session["user_id"] = user_id
        session["csrf_token"] = secrets.token_urlsafe(32)
        session["scan_session_ref"] = secrets.token_urlsafe(32)
        session.permanent = True
        audit("register_success", "users", user_id, {"role": role})
        return jsonify(success=True, user=public_user(current_user()), csrf_token=session["csrf_token"]), 201
    except Exception as exc:
        if "UNIQUE constraint failed: users.phone" in str(exc):
            return api_error("An account with this phone number already exists.", 409)
        current_app.logger.exception("Registration failed")
        return api_error("Account could not be created.", 500)


@bp.post("/api/login")
@csrf_required
@rate_limit(8, 60)
def login():
    data, error = json_body()
    if error: return error
    phone = str(data.get("phone", "")).strip()
    password = data.get("password", "")
    if not phone.isdigit() or not 8 <= len(phone) <= 15 or not isinstance(password, str) or not password or len(password) > 256:
        audit("login_failed", "users", None, {"reason": "invalid_input"})
        return api_error("Invalid sign-in details.", 401)
    with connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE phone=? AND is_active=1", (phone,)).fetchone()
    if row is None or not check_password_hash(row["password_hash"], password):
        audit("login_failed", "users", None, {"reason": "invalid_credentials"})
        return api_error("Invalid sign-in details.", 401)
    scan_session_ref = session.get("scan_session_ref") or secrets.token_urlsafe(32)
    session.clear()
    session["user_id"] = row["id"]
    session["csrf_token"] = secrets.token_urlsafe(32)
    session["scan_session_ref"] = scan_session_ref
    session.permanent = True
    audit("login_success", "users", row["id"], {"role": row["role"]})
    return jsonify(success=True, user=public_user(row), csrf_token=session["csrf_token"])


@bp.post("/api/logout")
@csrf_required
def logout():
    uid = session.get("user_id")
    if uid is not None:
        audit("logout", "users", uid, {})
    session.clear()
    session["csrf_token"] = secrets.token_urlsafe(32)
    session["scan_session_ref"] = secrets.token_urlsafe(32)
    session.permanent = True
    return jsonify(success=True, csrf_token=session["csrf_token"])


@bp.post("/api/profile")
@csrf_required
@require_auth()
def update_profile():
    data, error = json_body()
    if error: return error
    updates = {}
    try:
        for key, max_len in PROFILE_TEXT_FIELDS.items():
            if key in data:
                value = text_field(data, key, max_length=max_len)
                if key == "language" and value not in {"en", "te"}:
                    raise ValueError("Language must be en or te.")
                if key == "name" and not value:
                    raise ValueError("Name cannot be empty.")
                updates[key] = value
        for key, bounds in PROFILE_NUM_FIELDS.items():
            if key in data:
                value = number_field(data, key, minimum=bounds[0], maximum=bounds[1])
                updates[key] = int(value) if key == "experience" else value
        if not updates: raise ValueError("No supported profile fields were supplied.")
    except ValueError as exc:
        return api_error(str(exc))
    updates["updated_at"] = utc_now()
    columns = ",".join(f"{k}=?" for k in updates)
    with connect() as conn:
        conn.execute(f"UPDATE users SET {columns} WHERE id=?", (*updates.values(), session["user_id"]))
    audit("profile_updated", "users", session["user_id"], {"fields": sorted(k for k in updates if k != "updated_at")})
    return jsonify(success=True, user=public_user(current_user()))


@bp.get("/api/weather")
@rate_limit(30, 60)
def weather():
    city = (request.args.get("city") or "Hyderabad").strip()
    if not city or len(city) > 80 or any(char in city for char in "<>;{}"):
        return api_error("Enter a valid location.")
    result = get_weather(city, force_refresh=request.args.get("refresh") == "1")
    return jsonify(result), (200 if result.get("success") else 503)


@bp.post("/api/recommendations")
@csrf_required
@rate_limit(20, 60)
def recommend_crop():
    data, error = json_body()
    if error: return error
    try:
        features = [number_field(data, k, required=True, minimum=lo, maximum=hi) for k,lo,hi in (
            ("N",0,300),("P",0,300),("K",0,300),("temperature",-5,60),("humidity",0,100),("ph",0,14),("rainfall",0,1000))]
    except ValueError as exc:
        return api_error(str(exc))
    result = predict_crop(features)
    if not result.get("success"):
        return jsonify(result), 503
    crop_key = result["crop"].strip().casefold()
    catalog = {
        "paddy": {"water_requirement": "High; follow local irrigation advice.", "duration_days": "110–150", "risk": "Water availability and pest pressure", "estimated_cost": None},
        "cotton": {"water_requirement": "Moderate; avoid waterlogging.", "duration_days": "150–180", "risk": "Pest pressure and rain during flowering", "estimated_cost": None},
        "maize": {"water_requirement": "Moderate; moisture is important around flowering.", "duration_days": "90–120", "risk": "Moisture stress and fall armyworm", "estimated_cost": None},
        "chilli": {"water_requirement": "Regular, well-drained irrigation.", "duration_days": "150–210", "risk": "Disease and price volatility", "estimated_cost": None},
        "tomato": {"water_requirement": "Regular irrigation; avoid standing water.", "duration_days": "90–140", "risk": "Disease and price volatility", "estimated_cost": None},
    }
    result["plan"] = catalog.get(crop_key, {"water_requirement": "Confirm locally.", "duration_days": "Varies by variety", "risk": "Weather, pest, soil and market conditions", "estimated_cost": None})
    result["simple_reference_nutrient_check"] = model_fertilizer_reference(features[0], features[1], features[2])
    result["reasoning"] = "Crop name is the model prediction. Nutrient notes are simple reference checks, not fertilizer prescriptions. No calibrated suitability score is inferred."
    result["disclaimer"] = "MODEL OUTPUT only. Validate measurements, local crop suitability, water access, costs and seasonal recommendations with qualified local agricultural staff."
    return jsonify(result)


@bp.post("/api/yield-estimate")
@csrf_required
def yield_reference():
    data, error = json_body()
    if error: return error
    try:
        ph = number_field(data,"ph",required=True,minimum=0,maximum=14)
        temp = number_field(data,"temperature",required=True,minimum=-5,maximum=60)
        rain = number_field(data,"rainfall",required=True,minimum=0,maximum=1000)
    except ValueError as exc:
        return api_error(str(exc))
    score = 100 - (15 if not 5.5 <= ph <= 7.5 else 0) - (15 if not 20 <= temp <= 30 else 0) - (20 if rain < 50 else 10 if rain > 250 else 0)
    return jsonify(success=True, status="CURATED_RULES", data_type="CURATED", reference_favorability_score=max(score,40), score_type="REFERENCE FAVORABILITY SCORE", note="This is not a trained yield model and does not estimate tonnes per acre or guarantee outcomes.")


@bp.post("/api/market-net-income")
@csrf_required
def market_net_income():
    data, error = json_body()
    if error: return error
    try:
        qty = number_field(data,"quantity",required=True,minimum=0.1,maximum=1_000_000)
        price = number_field(data,"price",required=True,minimum=0,maximum=100_000)
        transport = number_field(data,"transport",minimum=0,maximum=100_000_000) or 0
        charges = number_field(data,"charges",minimum=0,maximum=100_000_000) or 0
        storage = number_field(data,"storage_cost",minimum=0,maximum=100_000_000) or 0
        other = number_field(data,"other_costs",minimum=0,maximum=100_000_000) or 0
    except ValueError as exc:
        return api_error(str(exc))
    selling = qty * price
    net = selling - transport - charges - storage - other
    return jsonify(success=True, status="CALCULATED", data_type="USER_ENTERED_CALCULATION", selling_value=round(selling,2), expected_selling_value=round(selling,2), estimated_net_income=round(net,2), costs={"transport":transport,"market_charges":charges,"storage":storage,"other":other}, disclaimer="Arithmetic estimate only. It uses the values you supplied and does not forecast price, yield, quality, payment or profit.")


@bp.post("/api/storage-calculation")
@csrf_required
def storage_calculation():
    data, error = json_body()
    if error: return error
    try:
        qty=number_field(data,"quantity",required=True,minimum=0.1,maximum=1_000_000)
        days=number_field(data,"days",required=True,minimum=1,maximum=365)
        daily=number_field(data,"cost_per_quintal_day",required=True,minimum=0,maximum=10000)
        now_price=number_field(data,"sell_now_price",required=True,minimum=0,maximum=100000)
        future=number_field(data,"future_price",required=True,minimum=0,maximum=100000)
        transport=number_field(data,"transport",minimum=0,maximum=100_000_000) or 0
        charges=number_field(data,"charges",minimum=0,maximum=100_000_000) or 0
        spoilage=number_field(data,"spoilage_cost",minimum=0,maximum=100_000_000) or 0
    except ValueError as exc: return api_error(str(exc))
    cost=qty*days*daily
    sell_now=qty*now_price-transport-charges
    store_then=qty*future-transport-charges-cost-spoilage
    return jsonify(success=True, status="CALCULATED", data_type="USER_ENTERED_CALCULATION", storage_cost=round(cost,2), sell_now=round(sell_now,2), store_then_sell=round(store_then,2), difference=round(store_then-sell_now,2), disclaimer="Scenario arithmetic only. Future price is user-entered, not a prediction; spoilage, moisture loss, quality change, interest and delays may alter results.")


@bp.post("/api/finance/break-even")
@csrf_required
@require_auth()
def break_even():
    data, error = json_body()
    if error: return error
    try:
        costs=number_field(data,"total_costs",required=True,minimum=0,maximum=1_000_000_000)
        yield_qty=number_field(data,"expected_quantity",required=True,minimum=0.001,maximum=1_000_000_000)
        units=text_field(data,"unit",default="quintal",max_length=30)
        target_price=number_field(data,"expected_price",minimum=0,maximum=100_000)
    except ValueError as exc: return api_error(str(exc))
    out={"success":True,"status":"CALCULATED","data_type":"USER_ENTERED_CALCULATION","break_even_price_per_unit":round(costs/yield_qty,2),"unit":units,"disclaimer":"Scenario calculation, not financial advice or a guarantee."}
    if target_price is not None:
        out["scenario_gross_value"]=round(target_price*yield_qty,2)
        out["scenario_net_value"]=round(target_price*yield_qty-costs,2)
        out["break_even_quantity_at_scenario_price"]=round(costs/target_price,2) if target_price>0 else None
        out["quantity_note"]="Break-even quantity is available only when expected_price is greater than zero. All values are user-entered scenarios."
    return jsonify(out)


@bp.post("/api/crop-risk")
@csrf_required
@require_auth(("farmer","expert","admin"))
def crop_risk():
    data,error=json_body()
    if error:return error
    try:
        crop=text_field(data,"crop",required=True,max_length=80)
        stage=text_field(data,"crop_stage",default="unknown",max_length=80)
        humidity=number_field(data,"humidity",minimum=0,maximum=100)
        rain=number_field(data,"rain_probability",minimum=0,maximum=100)
        wind=number_field(data,"wind_kmh",minimum=0,maximum=300)
        reported_pest=number_field(data,"nearby_pest_reports",minimum=0,maximum=1000) or 0
    except ValueError as exc:return api_error(str(exc))
    score=20; factors=[]
    if humidity is not None and humidity>=80: score+=15; factors.append({"factor":"humidity","effect":"increases_rule_based_risk","reason":"Humidity input is high."})
    if rain is not None and rain>=60: score+=15; factors.append({"factor":"rain_probability","effect":"increases_rule_based_risk","reason":"Rain probability input is high."})
    if wind is not None and wind>25: score+=10; factors.append({"factor":"wind","effect":"spraying_caution","reason":"Wind input exceeds the configured caution threshold."})
    if reported_pest>0: score+=min(25,int(reported_pest)*5); factors.append({"factor":"community_pest_reports","effect":"increases_attention","reason":"Reports are community-supplied and may be unverified."})
    score=max(0,min(100,score))
    result={"success":True,"status":"CURATED_RULES","data_type":"CURATED","risk_score":score,"score_type":"TRANSPARENT RULE-BASED ATTENTION SCORE, NOT A PROBABILITY","crop":crop,"crop_stage":stage,"factors":factors,"computed_at":utc_now(),"source_name":"Rythu Mitra rule set + supplied inputs","source_url":None,"limitations":"Not a validated agronomic risk model. Community reports and user inputs can be incomplete; confirm locally."}
    return jsonify(result)


@bp.post("/api/irrigation-advice")
@csrf_required
@require_auth()
def irrigation_advice():
    data,error=json_body()
    if error:return error
    try:
        crop=text_field(data,"crop",required=True,max_length=80)
        stage=text_field(data,"crop_stage",default="unknown",max_length=80)
        rain=number_field(data,"recent_rainfall_mm",minimum=0,maximum=2000)
        moisture=text_field(data,"soil_moisture_observation",default="unknown",max_length=100)
        method=text_field(data,"irrigation_method",default="unknown",max_length=100)
    except ValueError as exc:return api_error(str(exc))
    messages=["Check actual soil moisture and crop-stage guidance before deciding whether to irrigate."]
    if rain is not None and rain>=10: messages.append("User-entered recent rainfall is notable; inspect the field and drainage before adding water.")
    if "wet" in moisture.casefold() or "తడి" in moisture: messages.append("The soil moisture observation indicates wet soil; avoid unnecessary irrigation and check crop-specific needs.")
    return jsonify(success=True,status="CURATED_RULES",data_type="CURATED",crop=crop,crop_stage=stage,irrigation_method=method,advice=messages,assumptions=["Rainfall and soil moisture were supplied by the user.","No sensor reading or validated crop-specific water model is connected."],source_name="Rythu Mitra reference checklist",source_url=None)


@bp.post("/api/assistant/intent")
@csrf_required
@require_auth()
@rate_limit(20,60)
def assistant_intent():
    data,error=json_body()
    if error:return error
    try:q=text_field(data,"text",required=True,max_length=500)
    except ValueError as exc:return api_error(str(exc))
    text=q.casefold()
    matches=[]
    terms={"weather":["weather","rain","forecast","వాతావరణం","వర్షం"],"market-prices":["price","market","mandi","rate","ధర","మార్కెట్"],"crop-tasks":["task","today","calendar","పని","ఈరోజు"],"seed-scans":["seed","packet","బీజం","విత్తన"],"complaints":["complaint","problem report","ఫిర్యాదు"]}
    for intent,words in terms.items():
        if any(word in text for word in words): matches.append(intent)
    chosen=matches[0] if matches else "help"
    return jsonify(success=True,status="INTENT_SUGGESTION",data_type="MODEL_OUTPUT",recognized_text=q,intent=chosen,possible_intents=matches,confirmation_required=True,action_executed=False,note="The assistant only suggests a destination. Confirm the recognized text and action before any data is submitted.")


@bp.get("/api/dashboard")
@require_auth(("farmer","expert","admin","buyer","provider"))
def dashboard():
    user=current_user(); uid=user["id"]
    weather=get_weather(user["district"] or "Hyderabad")
    today=date.today()
    with connect() as conn:
        tasks=[]
        task_table=RESOURCE_TABLES["crop-tasks"]
        for row in conn.execute(f"SELECT * FROM {task_table} WHERE owner_id=? AND status!='DELETED' ORDER BY created_at DESC LIMIT 50",(uid,)):
            payload=json_load(row["payload_json"])
            due=payload.get("due_date")
            status=row["status"]
            if status not in {"COMPLETED","SKIPPED"} and due:
                try:
                    due_date=date.fromisoformat(str(due)[:10])
                    status="OVERDUE" if due_date<today else "DUE" if due_date==today else "UPCOMING"
                except ValueError:
                    pass
            tasks.append({"id":row["id"], **payload, "status":status,"data_type":row["data_type"],"last_updated":row["last_updated"]})
        tasks.sort(key=lambda x: (0 if x["status"]=="OVERDUE" else 1 if x["status"]=="DUE" else 2, str(x.get("due_date") or "9999-12-31")))
        scans=[dict(r) for r in conn.execute("SELECT id,result,confidence,label_verified,low_confidence,created_at,model_version FROM disease_scan_history WHERE owner_id=? ORDER BY created_at DESC LIMIT 5",(uid,))]
        notices=[dict(r) for r in conn.execute("SELECT id,title,body,severity,read_at,created_at,data_type,source_name,source_url FROM notifications WHERE user_id=? ORDER BY created_at DESC LIMIT 5",(uid,))]
        market_rows=conn.execute("SELECT * FROM market_prices WHERE status IN ('ACTIVE','APPROVED','PUBLISHED') ORDER BY created_at DESC LIMIT 5").fetchall()
        alert_rows=conn.execute("SELECT * FROM local_alerts WHERE status IN ('ACTIVE','APPROVED','PUBLISHED') ORDER BY created_at DESC LIMIT 50").fetchall()
        expense_rows=conn.execute("SELECT payload_json FROM farm_expenses WHERE owner_id=? AND status!='DELETED'",(uid,)).fetchall()
        income_rows=conn.execute("SELECT payload_json FROM farm_income WHERE owner_id=? AND status!='DELETED'",(uid,)).fetchall()
        inventory_rows=conn.execute("SELECT id,payload_json,last_updated,data_type FROM inventory_items WHERE owner_id=? AND status!='DELETED'",(uid,)).fetchall()
        seed_rows=conn.execute("SELECT id,payload_json,last_updated,data_type FROM seed_lots WHERE owner_id=? AND status!='DELETED'",(uid,)).fetchall()
    market=[]
    for row in market_rows:
        payload=json_load(row["payload_json"])
        payload.update({"id":row["id"],"record_status":row["status"],"data_type":row["data_type"],"source_name":row["source_name"],"source_url":row["source_url"],"last_updated":row["last_updated"],"last_verified":row["last_verified"]})
        pdate=payload.get("price_date")
        try:
            payload["age_days"]=(today-date.fromisoformat(str(pdate)[:10])).days
            payload["is_stale"]=payload["age_days"]>2
            payload["freshness_status"]="STALE" if payload["is_stale"] else "RECENT_DATE_CHECK_ONLY"
        except Exception:
            payload["age_days"]=None;payload["is_stale"]=True;payload["freshness_status"]="STALE_OR_DATE_UNKNOWN"
        market.append(payload)
    alerts=[]
    for row in alert_rows:
        payload=json_load(row["payload_json"])
        district=str(payload.get("district") or "").casefold()
        if district and user["district"] and district not in {str(user["district"]).casefold(),"telangana","all"}:continue
        expires=payload.get("expires_at")
        try:
            if expires and date.fromisoformat(str(expires)[:10])<today:continue
        except ValueError:continue
        is_seed=any("seed" in str(payload.get(k) or "").casefold() or "విత్తన" in str(payload.get(k) or "") for k in ("alert_type","message","title","category"))
        if is_seed:
            alerts.append({"id":row["id"],**payload,"status":row["status"],"data_type":row["data_type"],"source_name":row["source_name"],"source_url":row["source_url"],"last_updated":row["last_updated"]})
    inventory_alerts=[]
    for row in inventory_rows:
        payload=json_load(row["payload_json"])
        try:
            if float(payload.get("quantity"))<=float(payload.get("low_stock_threshold",0)):
                inventory_alerts.append({"id":row["id"],"item_name":payload.get("item_name"),"quantity":payload.get("quantity"),"unit":payload.get("unit"),"data_type":row["data_type"]})
        except (TypeError,ValueError):pass
    seed_expiry_alerts=[]
    for row in seed_rows:
        payload=json_load(row["payload_json"]);expiry=payload.get("validity_date")
        try:
            expiry_date=date.fromisoformat(str(expiry)[:10])
            if expiry_date<today or (expiry_date-today).days<=30:
                seed_expiry_alerts.append({"id":row["id"],"crop":payload.get("crop"),"brand":payload.get("brand"),"validity_date":expiry_date.isoformat(),"status":"EXPIRED" if expiry_date<today else "EXPIRING_SOON","data_type":row["data_type"]})
        except (ValueError,TypeError):pass
    def _sum_payload(rows):
        total=0.0
        for item in rows:
            try:total+=float(json_load(item["payload_json"]).get("amount",0) or 0)
            except (ValueError,TypeError):pass
        return round(total,2)
    profile={k:user[k] for k in ("name","district","mandal","village","current_crop","crop_stage","language","land_area","soil_type","irrigation","previous_crop","season","budget")}
    actions=[]
    if any(t["status"]=="OVERDUE" for t in tasks):actions.append("Review overdue crop tasks.")
    if any(t["status"]=="DUE" for t in tasks):actions.append("Check tasks due today.")
    if seed_expiry_alerts:actions.append("Review seed packet validity dates; expiry checks do not verify authenticity.")
    if inventory_alerts:actions.append("Review farm inventory items at or below their low-stock thresholds.")
    if not actions:actions.append("No stored task is marked due. Review crop-stage guidance and verify local conditions.")
    actions.append("Check source and freshness labels before acting on weather or market information.")
    return jsonify(success=True,status="PARTIAL_DASHBOARD",data_type="MIXED",profile=profile,weather=weather,actions=actions,crop_calendar=tasks[:12],notifications=notices,market=market,recent_history=scans,seed_alerts=alerts,seed_expiry_alerts=seed_expiry_alerts,inventory_alerts=inventory_alerts,finance_summary={"expense_total":_sum_payload(expense_rows),"income_total":_sum_payload(income_rows),"calculation_basis":"Recorded user-entered records only; excludes unrecorded costs and is not profit forecasting."},schemes_count=_count(RESOURCE_TABLES["schemes"],"status IN ('ACTIVE','APPROVED','PUBLISHED')"),data_status={"profile":"USER_ENTERED","weather":weather.get("status","UNAVAILABLE"),"crop_calendar":"USER_SUBMITTED" if tasks else "UNAVAILABLE","market":"MIXED" if market else "UNAVAILABLE","recent_history":"MODEL_OUTPUT" if scans else "UNAVAILABLE","seed_alerts":"MIXED" if alerts else "UNAVAILABLE","inventory":"USER_SUBMITTED" if inventory_rows else "UNAVAILABLE"})


@bp.get("/api/family-dashboard")
@require_auth(("farmer",))
def family_dashboard():
    """Show only dashboard-safe summary fields for accounts that explicitly granted access."""
    user=current_user(); today=date.today(); summaries=[]
    with connect() as conn:
        invitations=conn.execute(f"SELECT owner_id,payload_json FROM {RESOURCE_TABLES['family-helpers']} WHERE status='ACCEPTED'").fetchall()
    for invite in invitations:
        grant=json_load(invite["payload_json"])
        if str(grant.get("helper_user_id")) != str(user["id"]) or "view_dashboard" not in grant.get("scopes",[]):
            continue
        expires=grant.get("expires_at")
        if expires:
            try:
                if date.fromisoformat(str(expires)[:10]) < today: continue
            except ValueError:
                continue
        owner_id=invite["owner_id"]
        with connect() as conn:
            owner=conn.execute("SELECT id,name,district,current_crop,crop_stage FROM users WHERE id=? AND is_active=1",(owner_id,)).fetchone()
            task_rows=conn.execute(f"SELECT id,payload_json,status,data_type,last_updated FROM {RESOURCE_TABLES['crop-tasks']} WHERE owner_id=? AND status!='DELETED' ORDER BY created_at DESC LIMIT 30",(owner_id,)).fetchall()
        if owner is None: continue
        tasks=[]
        for row in task_rows:
            item=json_load(row["payload_json"]); due=item.get("due_date"); status=row["status"]
            if status not in {"COMPLETED","SKIPPED"} and due:
                try:
                    due_day=date.fromisoformat(str(due)[:10]);status="OVERDUE" if due_day<today else "DUE" if due_day==today else "UPCOMING"
                except ValueError: pass
            # Do not expose free-text notes, attachments, finance records or private documents.
            tasks.append({"id":row["id"],"task":item.get("task"),"category":item.get("category"),"crop":item.get("crop"),"stage":item.get("stage"),"due_date":due,"status":status,"data_type":row["data_type"],"last_updated":row["last_updated"]})
        tasks.sort(key=lambda item:(0 if item["status"]=="OVERDUE" else 1 if item["status"]=="DUE" else 2,str(item.get("due_date") or "9999-12-31")))
        summaries.append({"account_reference":f"family-{owner['id']}","farmer_name":owner["name"],"district":owner["district"],"current_crop":owner["current_crop"],"crop_stage":owner["crop_stage"],"crop_tasks":tasks[:12],"access_scope":"view_dashboard","expires_at":expires,"data_type":"USER_SUBMITTED"})
    return jsonify(success=True,status="SCOPED_FAMILY_VIEW",data_type="MIXED" if summaries else "UNAVAILABLE",accounts=summaries,note="Only invited dashboard fields and crop tasks are shown. Finance, private uploads, documents and account settings are excluded.")


@bp.get("/api/markets")
@rate_limit(30,60)
def market_records():
    commodity=(request.args.get("commodity") or "").strip()[:80]
    district=(request.args.get("district") or "").strip()[:80]
    provider=request.args.get("provider") == "live"
    if provider:
        result=fetch_configured_provider(commodity or None,district or None,(request.args.get("market") or "").strip()[:100] or None,(request.args.get("state") or "").strip()[:80] or None)
        return jsonify(result),(200 if result.get("success") else 503)
    table=RESOURCE_TABLES["market-prices"]
    with connect() as conn:
        rows=conn.execute(f"SELECT * FROM {table} WHERE status IN ('ACTIVE','APPROVED','PUBLISHED') ORDER BY created_at DESC LIMIT 100").fetchall()
    found=[]
    for row in rows:
        d=json_load(row["payload_json"])
        if commodity and commodity.casefold() not in str(d.get("commodity","")).casefold():continue
        if district and district.casefold() not in str(d.get("district","")).casefold():continue
        d.update({"id":row["id"],"record_status":row["status"],"data_type":row["data_type"],"source_name":row["source_name"],"source_url":row["source_url"],"last_updated":row["last_updated"],"last_verified":row["last_verified"]})
        try:d["age_days"]=(date.today()-date.fromisoformat(str(d.get("price_date"))[:10])).days;d["is_stale"]=d["age_days"]>2;d["freshness_status"]="STALE" if d["is_stale"] else "RECENT_DATE_CHECK_ONLY"
        except Exception:d["age_days"]=None;d["is_stale"]=True;d["freshness_status"]="STALE_OR_DATE_UNKNOWN"
        found.append(d)
    if not found:return jsonify(success=False,status="UNAVAILABLE",data_type="UNAVAILABLE",records=[],error="No market price records are configured. Live provider access requires an authorised adapter."),503
    status="DEMO" if all(x["data_type"]=="DEMO" for x in found) else "MIXED" if len({x["data_type"] for x in found})>1 else found[0]["data_type"]
    return jsonify(success=True,status=status,data_type=status,records=found,source_note="Staleness is calculated from each record's price_date; import times do not make old prices current.")


@bp.get("/api/markets/trend")
@rate_limit(30,60)
def market_trend():
    commodity=(request.args.get("commodity") or "").strip()[:80]
    market_name=(request.args.get("market") or "").strip()[:100]
    if not commodity or not market_name:return api_error("commodity and market are required.")
    table=RESOURCE_TABLES["market-prices"]
    with connect() as conn:
        rows=conn.execute(f"SELECT * FROM {table} WHERE status IN ('ACTIVE','APPROVED','PUBLISHED') ORDER BY created_at DESC LIMIT 500").fetchall()
    points=[]
    for row in rows:
        payload=json_load(row["payload_json"])
        if str(payload.get("commodity","")).casefold()!=commodity.casefold() or str(payload.get("market","")).casefold()!=market_name.casefold():continue
        price_date=payload.get("price_date")
        try:age_days=(date.today()-date.fromisoformat(str(price_date)[:10])).days
        except Exception:age_days=None
        points.append({"date":price_date,"minimum_price":payload.get("minimum_price"),"modal_price":payload.get("modal_price"),"maximum_price":payload.get("maximum_price"),"arrival_quantity":payload.get("arrival_quantity"),"data_type":row["data_type"],"source_name":row["source_name"],"source_url":row["source_url"],"last_updated":row["last_updated"],"age_days":age_days,"stale":age_days is None or age_days>2})
    points.sort(key=lambda x:str(x.get("date") or ""))
    if not points:return jsonify(success=False,status="UNAVAILABLE",data_type="UNAVAILABLE",records=[],error="No historical prices are available for this commodity and market."),404
    dtype="MIXED" if len({x["data_type"] for x in points})>1 else points[-1]["data_type"]
    return jsonify(success=True,status="HISTORICAL_RECORDS",data_type=dtype,commodity=commodity,market=market_name,records=points,note="Historical observations only; no future price is predicted. Each observation must be checked for freshness and source.")


@bp.get("/api/schemes/matches")
@require_auth()
def scheme_matches():
    user = current_user()
    profile_complete = bool(user["district"] and user["land_area"] and user["current_crop"])
    match_status = "VERIFY_OFFICIALLY" if profile_complete else "MORE_INFORMATION_REQUIRED"
    table = RESOURCE_TABLES["schemes"]
    with connect() as conn:
        rows = conn.execute(
            f"SELECT * FROM {table} WHERE status IN ('ACTIVE','APPROVED','PUBLISHED') ORDER BY created_at DESC LIMIT 100"
        ).fetchall()

    matches = []
    known_names = set()
    for row in rows:
        payload = json_load(row["payload_json"])
        name = str(payload.get("name") or "").strip()
        if name:
            known_names.add(name.casefold())
        matches.append({
            "id": row["id"], **payload,
            "match_status": match_status,
            "eligibility_note": "This is not an eligibility decision. Confirm current eligibility, required documents, deadlines and application status with the official authority.",
            "status": "VERIFY_OFFICIALLY",
            "data_type": row["data_type"],
            "source_name": row["source_name"],
            "source_url": row["source_url"],
            "last_verified": row["last_verified"],
        })

    # Public, source-labelled starter directory so a new deployment with an empty
    # SQLite database still shows useful official scheme entry points.
    curated_schemes = [
        {
            "id": "curated-pm-kisan",
            "name": "PM-KISAN Samman Nidhi",
            "description": "Central Government income-support scheme for eligible farmer families.",
            "benefit": "Support amount, installment status and exclusions must be checked against the current official rules.",
            "eligibility": "Eligibility depends on the current PM-KISAN guidelines and exclusion criteria.",
            "official_url": "https://pmkisan.gov.in/",
            "source_name": "Government of India — PM-KISAN",
            "source_url": "https://pmkisan.gov.in/",
        },
        {
            "id": "curated-rythu-bharosa",
            "name": "Telangana Rythu Bharosa",
            "description": "Telangana State agriculture support scheme. Use the official portal for current government orders and notices.",
            "benefit": "Current coverage, amounts, season schedule and application process must be verified from official state announcements.",
            "eligibility": "Check the latest Telangana Government rules and district-level instructions.",
            "official_url": "https://rythubharosa.telangana.gov.in/",
            "source_name": "Government of Telangana — Rythu Bharosa",
            "source_url": "https://rythubharosa.telangana.gov.in/",
        },
        {
            "id": "curated-pmfby",
            "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
            "description": "Central crop-insurance programme for notified crops and areas under applicable seasonal rules.",
            "benefit": "Insurance coverage, premium share and claim process depend on notified crops, location, season and scheme rules.",
            "eligibility": "Confirm crop/area notification, enrolment dates and current season requirements on the official portal.",
            "official_url": "https://pmfby.gov.in/",
            "source_name": "Government of India — PMFBY",
            "source_url": "https://pmfby.gov.in/",
        },
    ]
    for scheme in curated_schemes:
        if scheme["name"].casefold() in known_names:
            continue
        matches.append({
            **scheme,
            "match_status": match_status,
            "eligibility_note": "Curated official entry point only; this is not an eligibility decision. Verify current rules, documents, deadlines and application status on the official website.",
            "status": "VERIFY_OFFICIALLY",
            "data_type": "CURATED",
            "last_verified": None,
        })

    return jsonify(
        success=True,
        profile_complete=profile_complete,
        matches=matches,
        note="Scheme directory includes curated official entry points. No live eligibility check or application submission is implied.",
    )


@bp.get("/health")
def health():
    path=current_app.config["DATABASE_PATH"]
    return jsonify(status="ok",database_exists=__import__('pathlib').Path(path).exists(),demo_mode=current_app.config["DEMO_MODE"],app_env=current_app.config["APP_ENV"])


@bp.get("/ready")
def ready():
    try:
        with connect() as conn:
            conn.execute("SELECT 1").fetchone()
            version=conn.execute("SELECT MAX(version) FROM schema_migrations").fetchone()[0]
        return jsonify(status="ready",database="healthy",schema_version=version,models={"crop":"configured" if has_model_asset("crop_model.pkl") else "unavailable", "disease":"configured" if has_disease_model_bundle() else "unavailable"},weather="OPENWEATHER" if current_app.config.get("OPENWEATHER_API_KEY") else "OPEN_METEO_FALLBACK",market_adapter="configured" if (current_app.config.get("DATA_GOV_IN_API_KEY") or current_app.config.get("MARKET_DATA_BASE_URL")) else "unavailable")
    except Exception:
        current_app.logger.exception("Readiness probe failed")
        return jsonify(status="not_ready",database="unavailable"),503


@bp.get("/api/admin/summary")
@require_auth(("admin",))
def admin_summary():
    counts={slug:_count(table,"status!='DELETED'") for slug,table in RESOURCE_TABLES.items()}
    counts["farmers"]=_count("users","role='farmer'")
    counts["experts"]=_count("users","role='expert'")
    counts["buyers"]=_count("users","role='buyer'")
    return jsonify(success=True,counts=counts,system_status={"database":"healthy","crop_model":"configured" if has_model_asset("crop_model.pkl") else "unavailable","disease_model":"configured" if has_disease_model_bundle() else "unavailable","weather":"configured" if current_app.config.get("OPENWEATHER_API_KEY") else "unavailable","market_adapter":"configured" if (current_app.config.get("DATA_GOV_IN_API_KEY") or current_app.config.get("MARKET_DATA_BASE_URL")) else "unavailable"})
