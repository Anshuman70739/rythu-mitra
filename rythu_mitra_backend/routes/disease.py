"""Preliminary plant-image model inference and private scan history."""
from __future__ import annotations
import io
import secrets
from pathlib import Path
from flask import Blueprint, current_app, jsonify, request, session
from PIL import Image, ImageOps, UnidentifiedImageError
from werkzeug.datastructures import FileStorage
from ..db import connect, utc_now, json_load
from ..security import api_error, current_user, csrf_required, rate_limit, require_auth, audit
from ..services.models import predict_disease
from ..services.uploads import save_private_image, UploadError
from .domains import _create, _serialize

bp=Blueprint("disease",__name__)

@bp.post("/api/disease-scan")
@csrf_required
@rate_limit(10,60)
def disease_scan():
    upload=request.files.get("image")
    if not upload or not upload.filename:return api_error("Choose a crop image.")
    raw=upload.stream.read(current_app.config["MAX_UPLOAD_BYTES"]+1)
    if len(raw)>current_app.config["MAX_UPLOAD_BYTES"]:return api_error("Image exceeds the configured upload limit.",413)
    try:
        Image.MAX_IMAGE_PIXELS=current_app.config.get("MAX_IMAGE_PIXELS",20_000_000)
        with Image.open(io.BytesIO(raw)) as probe:
            fmt=(probe.format or "").upper()
            if fmt not in {"JPEG","PNG","WEBP"}:return api_error("Use a real JPEG, PNG, or WebP image.")
            if probe.width < 16 or probe.height < 16:return api_error("Image dimensions are too small to analyse.")
            if probe.width * probe.height > current_app.config.get("MAX_IMAGE_PIXELS",20_000_000):return api_error("Image dimensions exceed the safety limit.")
            extension=Path(upload.filename or "").suffix.lower()
            expected={"JPEG":{".jpg",".jpeg"},"PNG":{".png"},"WEBP":{".webp"}}
            if extension not in expected[fmt]:return api_error("The file extension does not match the decoded image format.")
            claimed=(upload.mimetype or "").lower()
            actual_mime={"JPEG":"image/jpeg","PNG":"image/png","WEBP":"image/webp"}[fmt]
            if claimed.startswith("image/") and claimed!=actual_mime:return api_error("The declared image type does not match the decoded image format.")
            probe.verify()
        with Image.open(io.BytesIO(raw)) as src:
            image=ImageOps.exif_transpose(src).convert("RGB")
            if image.width*image.height>current_app.config.get("MAX_IMAGE_PIXELS",20_000_000):return api_error("Image dimensions exceed the safety limit.")
    except (UnidentifiedImageError,OSError,Image.DecompressionBombError,Image.DecompressionBombWarning):return api_error("The upload is not a safe, readable image.")
    result=predict_disease(image)
    if not result.get("success"):
        return jsonify(result),503
    user=current_user();upload_info=None
    if user:
        try:
            upload_info=save_private_image(FileStorage(stream=io.BytesIO(raw),filename=upload.filename,content_type=upload.content_type),user["id"],"disease_scan")
        except UploadError as exc:return api_error(str(exc))
    scan_id=secrets.token_urlsafe(18).replace("-", "").replace("_", "")[:24]
    session_ref=session.get("scan_session_ref") or secrets.token_urlsafe(32)
    session["scan_session_ref"]=session_ref
    with connect() as conn:
        conn.execute("INSERT INTO disease_scan_history(id,owner_id,session_ref,upload_id,result,class_index,confidence,label_verified,low_confidence,model_version,guidance,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            (scan_id,user["id"] if user else None,session_ref,upload_info["id"] if upload_info else None,result.get("result") or "Unverified model result",result.get("class_index"),result.get("confidence"),int(bool(result.get("label_verified"))),int(bool(result.get("low_confidence"))),result.get("model_version"),result.get("guidance","Preliminary result only."),utc_now()))
    audit("disease_scan_completed","disease_scan_history",user["id"] if user else None,{"scan_id":scan_id,"low_confidence":bool(result.get("low_confidence"))})
    result.update({"scan_id":scan_id,"image_id":upload_info["id"] if upload_info else None,"saved_to_account":bool(user),"history_save_available":not bool(user),"created_at":utc_now()})
    if not user:
        result["note"]="This scan is in a temporary browser session. Sign in and explicitly save it to attach the result to your account. The image itself was not retained for an anonymous session."
    return jsonify(result)


@bp.get("/api/scan-history")
@require_auth()
def get_scan_history():
    uid=session["user_id"]
    limit=request.args.get("limit",50)
    try:limit=max(1,min(int(limit),100))
    except ValueError:return api_error("limit must be an integer.")
    with connect() as conn:
        rows=conn.execute("SELECT id AS scan_id,result,class_index,confidence,label_verified,low_confidence,model_version,guidance,created_at,saved_at,upload_id FROM disease_scan_history WHERE owner_id=? ORDER BY created_at DESC LIMIT ?",(uid,limit)).fetchall()
        reviews=conn.execute("SELECT id,owner_id,payload_json,status,source_name,data_type,last_updated FROM disease_reviews WHERE status!='DELETED' ORDER BY created_at DESC LIMIT 500").fetchall()
        experts={r["id"]:r["name"] for r in conn.execute("SELECT id,name FROM users WHERE is_active=1 AND role='expert'").fetchall()}
    result=[]
    for scan_row in rows:
        scan=dict(scan_row);attached_reviews=[]
        for item in reviews:
            payload=json_load(item["payload_json"])
            if str(payload.get("scan_id")) != str(scan["scan_id"]): continue
            # Reveal only the review content tied to this authenticated owner's scan.
            attached_reviews.append({"id":item["id"],"assessment":payload.get("assessment"),"review_notes":payload.get("review_notes"),"recommended_next_step":payload.get("recommended_next_step"),"follow_up_required":payload.get("follow_up_required"),"reviewed_at":payload.get("reviewed_at"),"reviewer_name":experts.get(payload.get("reviewer_user_id"),"Agriculture expert"),"status":item["status"],"data_type":item["data_type"],"limitations":payload.get("review_limitations")})
        scan["expert_reviews"]=attached_reviews
        result.append(scan)
    return jsonify(success=True,records=result,data_type="MODEL_OUTPUT")


@bp.post("/api/disease-scans/<string:scan_id>/expert-review")
@csrf_required
@require_auth(("expert",))
@rate_limit(10,60)
def expert_review_scan(scan_id):
    data=request.get_json(silent=True) or {}
    required=("question_id","assessment","review_notes")
    if any(not isinstance(data.get(k),str) or not data.get(k).strip() for k in required):
        return api_error("question_id, assessment and review_notes are required.")
    if len(data["review_notes"])>3000:return api_error("review_notes must be at most 3000 characters.")
    if data.get("recommended_next_step") is not None and (not isinstance(data["recommended_next_step"],str) or len(data["recommended_next_step"])>1000):
        return api_error("recommended_next_step must be text of at most 1000 characters.")
    follow=data.get("follow_up_required",False)
    if not isinstance(follow,bool):return api_error("follow_up_required must be true or false.")
    payload={"scan_id":scan_id,"question_id":data["question_id"].strip(),"assessment":data["assessment"].strip().upper(),"review_notes":data["review_notes"].strip(),"recommended_next_step":str(data.get("recommended_next_step") or "").strip(),"follow_up_required":follow}
    try:row=_create("disease-reviews",payload,current_user())
    except PermissionError as exc:return api_error(str(exc),403)
    except ValueError as exc:return api_error(str(exc))
    audit("disease_expert_review_created","disease-reviews",session.get("user_id"),{"review_id":row["id"],"scan_id":scan_id,"question_id":payload["question_id"]})
    return jsonify(success=True,record=_serialize(row,is_owner=True,resource="disease-reviews"),note="An authenticated expert recorded a preliminary review of evidence shared with the question; this is not a lab certificate or a guaranteed diagnosis."),201


@bp.post("/api/scan-history")
@csrf_required
@require_auth()
def save_scan_history():
    data=request.get_json(silent=True) or {}
    scan_id=data.get("scan_id") or data.get("id")
    if not isinstance(scan_id,str) or not scan_id:return api_error("scan_id is required.")
    uid=session["user_id"];session_ref=session.get("scan_session_ref")
    with connect() as conn:
        row=conn.execute("SELECT id FROM disease_scan_history WHERE id=? AND session_ref=? AND owner_id IS NULL",(scan_id,session_ref)).fetchone()
        if row is None:return api_error("This scan does not belong to the current anonymous browser session or was already saved.",404)
        conn.execute("UPDATE disease_scan_history SET owner_id=?,saved_at=? WHERE id=? AND owner_id IS NULL",(uid,utc_now(),scan_id))
        record=conn.execute("SELECT id AS scan_id,result,class_index,confidence,label_verified,low_confidence,model_version,guidance,created_at,saved_at,upload_id FROM disease_scan_history WHERE id=? AND owner_id=?",(scan_id,uid)).fetchone()
    audit("disease_scan_saved","disease_scan_history",uid,{"scan_id":scan_id})
    return jsonify(success=True,record=dict(record))


@bp.delete("/api/scan-history/<string:scan_id>")
@csrf_required
@require_auth()
def delete_scan_history(scan_id):
    with connect() as conn:
        row=conn.execute("SELECT id,upload_id FROM disease_scan_history WHERE id=? AND owner_id=?",(scan_id,session["user_id"])).fetchone()
        if row is None:return api_error("Scan not found.",404)
        conn.execute("DELETE FROM disease_scan_history WHERE id=? AND owner_id=?",(scan_id,session["user_id"]))
        # The upload is private and may be referenced elsewhere, so retain it until
        # a dedicated attachment-cleanup policy can prove it is unreferenced.
    audit("disease_scan_deleted","disease_scan_history",session["user_id"],{"scan_id":scan_id})
    return jsonify(success=True,message="Scan history entry deleted. Uploaded evidence is retained privately until cleanup.")
