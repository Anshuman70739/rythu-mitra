"""Compatibility APIs for the first Rythu Mitra frontend/backend contract."""
from __future__ import annotations
import json
from flask import Blueprint, jsonify, request, session
from ..db import connect, json_dump, json_load, utc_now
from ..security import api_error, current_user, require_auth, csrf_required, rate_limit, audit

bp=Blueprint("legacy",__name__)
LEGACY_KINDS={"market","scheme","equipment","storage","buyer","listing","buyer_request","booking","disaster","feedback","expert_question","disease_knowledge","seed_alert","complaint"}


def serialize(row, own=False, admin=False):
    payload=json_load(row["payload_json"])
    if not own and not admin:
        for key in ("phone","phone_number","contact","email","address","full_address","receipt_upload_id","policy_number"):
            payload.pop(key,None)
    return {"id":row["id"],"kind":row["kind"],"title":row["title"],"payload":payload,"status":row["status"],"source":row["source_name"],"source_name":row["source_name"],"source_url":row["source_url"],"data_type":row["data_type"],"last_updated":row["last_updated"],"last_verified":row["last_verified"],"created_at":row["created_at"]}


@bp.get("/api/records/<kind>")
def list_legacy_records(kind):
    if kind not in LEGACY_KINDS:return api_error("Unknown resource.",404)
    user=current_user();clauses=["kind=?","status!='DELETED'"];params=[kind]
    public=kind in {"market","scheme","equipment","storage","buyer","disease_knowledge","seed_alert"}
    if user and user["role"]=="admin":pass
    elif user:
        clauses.append("(owner_id=? OR (owner_id IS NULL AND status IN ('ACTIVE','APPROVED','PUBLISHED','Active')))");params.append(user["id"])
    elif public:
        clauses.append("owner_id IS NULL AND status IN ('ACTIVE','APPROVED','PUBLISHED','Active')")
    else:return api_error("Please sign in.",401)
    with connect() as conn:rows=conn.execute(f"SELECT * FROM legacy_records WHERE {' AND '.join(clauses)} ORDER BY created_at DESC LIMIT 100",tuple(params)).fetchall()
    term=(request.args.get("q") or "").casefold()
    values=[]
    for row in rows:
        item=serialize(row,own=user is not None and row["owner_id"]==user["id"],admin=user is not None and user["role"]=="admin")
        if term and term not in json_dump(item).casefold():continue
        values.append(item)
    dtypes={x["data_type"] for x in values}
    status="UNAVAILABLE" if not values else "MIXED" if len(dtypes)>1 else next(iter(dtypes))
    return jsonify(success=True,records=values,status=status,data_type=status)


@bp.post("/api/records/<kind>")
@csrf_required
@require_auth()
@rate_limit(12,60)
def create_legacy_record(kind):
    if kind not in LEGACY_KINDS:return api_error("Unknown resource.",404)
    user=current_user()
    permissions={"listing":{"farmer"},"buyer_request":{"buyer"},"booking":{"farmer"},"disaster":{"farmer"},"expert_question":{"farmer"},"feedback":{"farmer","expert","buyer"},"complaint":{"farmer"}}
    if kind in permissions and user["role"] not in permissions[kind]:return api_error("You are not authorized for this submission.",403)
    data=request.get_json(silent=True) or {}
    title=str(data.get("title","")).strip()
    if not 3<=len(title)<=120:return api_error("Title must be 3–120 characters.")
    clean={str(k)[:40]:v for k,v in data.items() if k not in {"csrf_token","title","owner_id","user_id","role","password","password_hash"}}
    if len(json_dump(clean).encode())>24000:return api_error("Record is too large.",413)
    stamp=utc_now()
    with connect() as conn:
        cur=conn.execute("INSERT INTO legacy_records(kind,owner_id,title,payload_json,status,source_name,source_url,data_type,last_updated,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)",(kind,user["id"],title,json_dump(clean),"SUBMITTED","User supplied",None,"USER_SUBMITTED",stamp,stamp))
        row=conn.execute("SELECT * FROM legacy_records WHERE id=?",(cur.lastrowid,)).fetchone()
    audit("legacy_record_created",kind,user["id"],{"id":row["id"]})
    return jsonify(success=True,record=serialize(row,own=True),message="Saved inside Rythu Mitra; no external authority or contact was notified."),201


@bp.patch("/api/records/<int:record_id>")
@csrf_required
@require_auth()
def update_legacy_record(record_id):
    user=current_user();data=request.get_json(silent=True) or {};status=str(data.get("status","")).strip().upper()
    allowed={"booking":{"SUBMITTED","CANCELLED"},"listing":{"SUBMITTED","CLOSED"},"buyer_request":{"SUBMITTED","CLOSED"},"disaster":{"DRAFT","SUBMITTED"},"complaint":{"USER_REPORTED","EVIDENCE_ADDED"}}
    with connect() as conn:
        row=conn.execute("SELECT id,kind FROM legacy_records WHERE id=? AND owner_id=? AND status!='DELETED'",(record_id,user["id"])).fetchone()
        if row is None:return api_error("Record not found or not owned by this account.",404)
        if status not in allowed.get(row["kind"],set()):return api_error("Invalid status change.")
        conn.execute("UPDATE legacy_records SET status=?,last_updated=? WHERE id=? AND owner_id=?",(status,utc_now(),record_id,user["id"]))
    audit("legacy_record_updated",str(record_id),user["id"],{"status":status})
    return jsonify(success=True,message="Status updated.")


@bp.patch("/api/admin/records/<int:record_id>")
@csrf_required
@require_auth(("admin",))
def moderate_legacy_record(record_id):
    data=request.get_json(silent=True) or {};status=str(data.get("status","")).strip().upper()
    if status not in {"UNDER_REVIEW","APPROVED","SUSPENDED","BLOCKED","CLOSED","REJECTED"}:return api_error("Invalid moderation status.")
    with connect() as conn:
        row=conn.execute("SELECT id FROM legacy_records WHERE id=?",(record_id,)).fetchone()
        if not row:return api_error("Record not found.",404)
        conn.execute("UPDATE legacy_records SET status=?,last_updated=? WHERE id=?",(status,utc_now(),record_id))
    audit("legacy_record_moderated",str(record_id),session.get("user_id"),{"status":status})
    return jsonify(success=True,message="Record moderated.")
