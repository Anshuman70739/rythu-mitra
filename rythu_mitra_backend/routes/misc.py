"""Notifications, private evidence uploads, and idempotent offline synchronization."""
from __future__ import annotations
import json
import secrets
from flask import Blueprint, jsonify, request, session, current_app, send_file
from ..db import connect, utc_now, json_dump, json_load, RESOURCE_TABLES
from ..security import api_error, current_user, require_auth, csrf_required, rate_limit, audit, json_body
from ..services.uploads import save_private_image, upload_path, UploadError
from .domains import _create, _serialize

bp=Blueprint("misc",__name__)
OFFLINE_ALLOWED={"farm-diary","expenses","income","crop-tasks","farm-observations","soil-records","irrigation-records","inventory-items","seed-test-results","seed-complaints"}
UPLOAD_CATEGORIES={"farm_photo","soil_report","receipt","damage_evidence","scheme_document","input_bill","seed_packet","disease_scan","harvest_evidence","other"}

@bp.post("/api/v1/uploads")
@csrf_required
@require_auth(("farmer","expert","admin","buyer","provider"))
@rate_limit(20,60)
def create_upload():
    user=current_user();upload=request.files.get("image")
    category=(request.form.get("category") or "other").strip()
    if category not in UPLOAD_CATEGORIES:return api_error("Unsupported upload category.")
    try:result=save_private_image(upload,user["id"],category)
    except UploadError as exc:return api_error(str(exc))
    audit("private_upload_created","uploads",user["id"],{"upload_id":result["id"],"category":category,"bytes":result["byte_size"]})
    return jsonify(success=True,upload=result,storage="PRIVATE",message="Image is privately stored; access requires an authorized session."),201


@bp.get("/api/notifications")
@require_auth()
def list_notifications():
    user=current_user()
    try:limit=max(1,min(int(request.args.get("limit",30)),100))
    except ValueError:return api_error("limit must be an integer.")
    with connect() as conn:
        rows=conn.execute("SELECT id,title,body,severity,read_at,source_name,source_url,data_type,created_at FROM notifications WHERE user_id=? ORDER BY created_at DESC LIMIT ?",(user["id"],limit)).fetchall()
    return jsonify(success=True,records=[dict(row) for row in rows])


@bp.post("/api/notifications/<string:notification_id>/read")
@csrf_required
@require_auth()
def mark_notification_read(notification_id):
    user=current_user()
    with connect() as conn:
        row=conn.execute("SELECT id FROM notifications WHERE id=? AND user_id=?",(notification_id,user["id"])).fetchone()
        if row is None:return api_error("Notification not found.",404)
        conn.execute("UPDATE notifications SET read_at=? WHERE id=? AND user_id=?",(utc_now(),notification_id,user["id"]))
    audit("notification_read",notification_id,user["id"],{})
    return jsonify(success=True,read_at=utc_now())


@bp.post("/api/offline/sync")
@csrf_required
@require_auth(("farmer",))
@rate_limit(20,60)
def sync_offline_operations():
    data,error=json_body(max_bytes=128_000)
    if error:return error
    ops=data.get("operations")
    if not isinstance(ops,list) or not 1<=len(ops)<=25:return api_error("operations must contain 1 to 25 offline operations.")
    user=current_user();results=[]
    for op in ops:
        if not isinstance(op,dict):
            results.append({"success":False,"error":"Each operation must be an object."});continue
        operation_id=op.get("operation_id");resource=op.get("resource");payload=op.get("payload")
        if not isinstance(operation_id,str) or not 8<=len(operation_id)<=100 or not isinstance(resource,str) or resource not in OFFLINE_ALLOWED or not isinstance(payload,dict):
            results.append({"success":False,"operation_id":operation_id if isinstance(operation_id,str) else None,"error":"Invalid operation ID, resource, or payload."});continue
        with connect() as conn:
            previous=conn.execute("SELECT result_json,created_at FROM offline_sync_operations WHERE owner_id=? AND operation_id=?",(user["id"],operation_id)).fetchone()
            if previous:
                prior=json_load(previous["result_json"])
                if prior.get("status") == "PROCESSING":
                    try:
                        from datetime import datetime, timezone
                        created=datetime.fromisoformat(str(previous["created_at"]).replace("Z","+00:00"))
                        if created.tzinfo is None: created=created.replace(tzinfo=timezone.utc)
                        if (datetime.now(timezone.utc)-created).total_seconds()>900:
                            conn.execute("DELETE FROM offline_sync_operations WHERE owner_id=? AND operation_id=?",(user["id"],operation_id))
                            previous=None
                    except ValueError:
                        conn.execute("DELETE FROM offline_sync_operations WHERE owner_id=? AND operation_id=?",(user["id"],operation_id))
                        previous=None
                if previous:
                    results.append(prior);continue
            # Reserve the idempotency key first so concurrent retries cannot create a second record.
            conn.execute("INSERT INTO offline_sync_operations(owner_id,operation_id,resource,result_json,created_at) VALUES(?,?,?,?,?)",(user["id"],operation_id,resource,json_dump({"success":False,"status":"PROCESSING","operation_id":operation_id}),utc_now()))
        try:
            row=_create(resource,payload,user)
            item={"success":True,"status":"SYNCED","operation_id":operation_id,"record":_serialize(row,is_owner=True)}
            with connect() as conn:conn.execute("UPDATE offline_sync_operations SET result_json=? WHERE owner_id=? AND operation_id=?",(json_dump(item),user["id"],operation_id))
            results.append(item)
        except Exception as exc:
            with connect() as conn:conn.execute("DELETE FROM offline_sync_operations WHERE owner_id=? AND operation_id=?",(user["id"],operation_id))
            if isinstance(exc,(ValueError,PermissionError)):
                results.append({"success":False,"status":"REJECTED","operation_id":operation_id,"error":str(exc)})
            else:
                current_app.logger.exception("Offline sync operation failed")
                results.append({"success":False,"status":"FAILED","operation_id":operation_id,"error":"Could not synchronize this record; it remains eligible for retry."})
    audit("offline_sync_batch","offline_sync_operations",user["id"],{"count":len(ops),"succeeded":sum(1 for x in results if x.get("success"))})
    return jsonify(success=all(x.get("success") for x in results),results=results,note="Sync status is saved per operation ID. Keep local drafts until each operation reports SYNCED."),200
