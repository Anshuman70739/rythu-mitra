"""Admin-only integrity, audit, source freshness, and curated CSV market import endpoints."""
from __future__ import annotations
import csv
import io
from datetime import date
from flask import Blueprint, jsonify, request, session
from ..db import connect, utc_now, json_dump, json_load, RESOURCE_TABLES
from ..security import api_error, require_auth, csrf_required, audit, json_body, text_field
from .domains import _serialize

bp=Blueprint("admin",__name__)

@bp.get("/api/admin/users")
@require_auth(("admin",))
def admin_users():
    try:limit=max(1,min(int(request.args.get("limit",100)),500))
    except ValueError:return api_error("limit must be an integer.")
    with connect() as conn:
        rows=conn.execute("SELECT id,name,phone,role,language,district,mandal,village,is_active,suspended_at,created_at,updated_at FROM users ORDER BY id DESC LIMIT ?",(limit,)).fetchall()
    result=[]
    for row in rows:
        item=dict(row)
        phone=str(item.pop("phone") or "")
        item["phone_masked"]=("*"*max(0,len(phone)-4)+phone[-4:]) if phone else None
        result.append(item)
    return jsonify(success=True,users=result)


@bp.patch("/api/admin/users/<int:user_id>")
@csrf_required
@require_auth(("admin",))
def update_user_admin(user_id):
    data,error=json_body()
    if error:return error
    allowed_roles={"farmer","expert","admin","buyer","provider"}
    changes={}
    if "role" in data:
        role=str(data["role"]).strip().lower()
        if role not in allowed_roles:return api_error("Unsupported account role.")
        changes["role"]=role
    if "is_active" in data:
        if not isinstance(data["is_active"],bool):return api_error("is_active must be true or false.")
        changes["is_active"]=int(data["is_active"])
        changes["suspended_at"]=None if data["is_active"] else utc_now()
    if not changes:return api_error("Supply role or is_active.")
    actor=session.get("user_id")
    with connect() as conn:
        target=conn.execute("SELECT id,role,is_active FROM users WHERE id=?",(user_id,)).fetchone()
        if target is None:return api_error("User not found.",404)
        if user_id==actor and (changes.get("is_active")==0 or changes.get("role") not in (None,"admin")):
            return api_error("You cannot suspend or demote your own active admin account.",409)
        if target["role"]=="admin" and (changes.get("is_active")==0 or changes.get("role") not in (None,"admin")):
            active_admins=conn.execute("SELECT COUNT(*) FROM users WHERE role='admin' AND is_active=1").fetchone()[0]
            if active_admins<=1:return api_error("The last active admin cannot be suspended or demoted.",409)
        columns=",".join(f"{key}=?" for key in changes)
        conn.execute(f"UPDATE users SET {columns},updated_at=? WHERE id=?",(*changes.values(),utc_now(),user_id))
        changed=conn.execute("SELECT id,name,role,is_active,suspended_at,updated_at FROM users WHERE id=?",(user_id,)).fetchone()
    audit("admin_user_updated",str(user_id),actor,{"changes":{k:v for k,v in changes.items() if k!="suspended_at"}})
    return jsonify(success=True,user=dict(changed))


@bp.post("/api/admin/notifications")
@csrf_required
@require_auth(("admin",))
def admin_create_notification():
    data,error=json_body()
    if error:return error
    try:
        user_id=int(data.get("user_id"))
        title=text_field(data,"title",required=True,max_length=160)
        body=text_field(data,"body",required=True,max_length=2000)
        severity=text_field(data,"severity",default="info",max_length=20) or "info"
    except (TypeError,ValueError) as exc:return api_error(str(exc))
    if severity not in {"info","success","warning","urgent"}:return api_error("Unsupported notification severity.")
    import secrets
    notification_id=secrets.token_urlsafe(15)
    with connect() as conn:
        if not conn.execute("SELECT 1 FROM users WHERE id=? AND is_active=1",(user_id,)).fetchone():return api_error("Active recipient not found.",404)
        conn.execute("INSERT INTO notifications(id,user_id,title,body,severity,source_name,data_type,created_at) VALUES(?,?,?,?,?,?,?,?)",(notification_id,user_id,title,body,severity,"Admin notice","SYSTEM",utc_now()))
    audit("admin_notification_created",notification_id,session.get("user_id"),{"recipient_id":user_id,"severity":severity})
    return jsonify(success=True,notification_id=notification_id,message="Notification saved in Rythu Mitra; no SMS or external message was sent."),201


@bp.get("/api/admin/audit-logs")
@require_auth(("admin",))
def audit_logs():
    try:limit=max(1,min(int(request.args.get("limit",100)),500))
    except ValueError:return api_error("limit must be an integer.")
    with connect() as conn:
        rows=conn.execute("SELECT id,user_id,action,target,details_json,request_id,created_at FROM audit_logs ORDER BY id DESC LIMIT ?",(limit,)).fetchall()
    return jsonify(success=True,records=[{"id":r["id"],"user_id":r["user_id"],"action":r["action"],"target":r["target"],"details":json_load(r["details_json"]),"request_id":r["request_id"],"created_at":r["created_at"]} for r in rows])


@bp.get("/api/admin/data-health")
@require_auth(("admin",))
def data_health():
    data={}
    with connect() as conn:
        for slug in ("market-prices","schemes","storage-facilities","equipment-listings","fpo-directory","notices","pest-reports","local-alerts"):
            table=RESOURCE_TABLES[slug]
            rows=conn.execute(f"SELECT status,data_type,last_updated,last_verified,expires_at,payload_json FROM {table} WHERE status!='DELETED'").fetchall()
            stale=0;unverified=0
            for row in rows:
                payload=json_load(row["payload_json"])
                source_date=payload.get("price_date") or payload.get("observation_date") or row["last_verified"] or row["last_updated"]
                try:
                    age=(date.today()-date.fromisoformat(str(source_date)[:10])).days
                    if age>2 and slug=="market-prices":stale+=1
                    if row["expires_at"] and date.fromisoformat(row["expires_at"][:10])<date.today():stale+=1
                except Exception:pass
                if not row["last_verified"] and row["data_type"] not in {"USER_SUBMITTED","MODEL_OUTPUT"}:unverified+=1
            data[slug]={"total":len(rows),"stale_count":stale,"missing_verification_date_count":unverified,"data_types":sorted({r["data_type"] for r in rows}),"workflow_statuses":sorted({r["status"] for r in rows})}
    return jsonify(success=True,generated_at=utc_now(),data=data,note="Missing verification metadata and stale data must be displayed; they are not silently promoted to live status.")


@bp.post("/api/admin/market-prices/import-csv")
@csrf_required
@require_auth(("admin",))
def import_market_csv():
    upload=request.files.get("file")
    if upload is None:return api_error("Upload a CSV file in multipart field 'file'.")
    raw=upload.stream.read(1_000_001)
    if len(raw)>1_000_000:return api_error("CSV must be under 1 MB.",413)
    try:text=raw.decode("utf-8-sig")
    except UnicodeDecodeError:return api_error("CSV must be UTF-8.")
    reader=csv.DictReader(io.StringIO(text))
    required={"commodity","market","minimum_price","modal_price","maximum_price","price_date","source_name","source_url","data_type"}
    if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):return api_error("CSV columns required: "+", ".join(sorted(required)))
    rows=[];errors=[]
    for idx,row in enumerate(reader, start=2):
        try:
            commodity=row["commodity"].strip()[:80];market=row["market"].strip()[:100]
            if not commodity or not market:raise ValueError("commodity and market are required")
            low=float(row["minimum_price"]);modal=float(row["modal_price"]);high=float(row["maximum_price"])
            if min(low,modal,high)<0 or not low<=modal<=high:raise ValueError("prices must satisfy 0 <= minimum <= modal <= maximum")
            price_date=date.fromisoformat(row["price_date"][:10]).isoformat()
            source_name=row["source_name"].strip()[:160];source_url=row["source_url"].strip()
            if not source_name or not source_url.startswith("https://"):raise ValueError("source_name and HTTPS source_url are required")
            dtype=row["data_type"].strip().upper()
            if dtype not in {"CURATED","DEMO"}:raise ValueError("manual CSV imports may only be CURATED or DEMO; LIVE must come from a configured provider adapter")
            payload={"commodity":commodity,"market":market,"district":row.get("district","").strip()[:80],"minimum_price":low,"modal_price":modal,"maximum_price":high,"arrival_quantity":row.get("arrival_quantity",""),"price_date":price_date,"unit":row.get("unit","₹/quintal").strip()[:40],"notes":row.get("notes","").strip()[:1000]}
            rows.append((payload,source_name,source_url,dtype))
        except (ValueError,TypeError,KeyError) as exc:errors.append({"row":idx,"error":str(exc)})
    if errors:return jsonify(success=False,error="CSV validation failed; no rows were imported.",row_errors=errors),400
    with connect() as conn:
        for payload,source_name,source_url,dtype in rows:
            import secrets
            rid=secrets.token_urlsafe(16)
            conn.execute("INSERT INTO market_prices(id,owner_id,farm_id,payload_json,status,source_name,source_url,data_type,last_updated,last_verified,created_at,updated_at) VALUES(?,NULL,NULL,?,?,?,?,?,?,?,?,?)",
                (rid,json_dump(payload),"DRAFT",source_name,source_url,dtype,utc_now(),None,utc_now(),utc_now()))
    audit("market_csv_imported","market_prices",session.get("user_id"),{"rows":len(rows),"data_type":"CURATED/DEMO"})
    return jsonify(success=True,imported=len(rows),status="DRAFT",message="Rows imported for admin review. They are not public until moderated; manual imports cannot claim LIVE status."),201
