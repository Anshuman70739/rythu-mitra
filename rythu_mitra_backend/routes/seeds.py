"""Seed packet safety assistant: evidence capture, label completeness, QR preview, germination and complaint workflow."""
from __future__ import annotations
from datetime import date
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import io
import re
from flask import Blueprint, current_app, jsonify, request, send_file, session
from werkzeug.datastructures import FileStorage
from PIL import Image
from ..db import connect, utc_now, json_dump, json_load, RESOURCE_TABLES
from ..security import api_error, current_user, require_auth, csrf_required, rate_limit, audit, json_body
from ..services.uploads import save_private_image, upload_path, UploadError
from .domains import _create, _serialize, _label_completeness

bp=Blueprint("seeds",__name__)


def _is_trusted_official_https(url:str)->bool:
    try:
        parsed=urlparse(url)
        if parsed.scheme!="https" or not parsed.hostname or parsed.username or parsed.password or parsed.port not in (None,443):return False
        host=parsed.hostname.casefold().rstrip(".")
        if host in current_app.config["TRUSTED_QR_DOMAINS"]:return True
        return host.endswith(".gov.in") or host.endswith(".nic.in")
    except ValueError:return False


def _ocr_text(path:Path)->tuple[str,str]:
    # OCR is optional and only produces text for farmer review; it never certifies a packet.
    try:
        import pytesseract
        with Image.open(path) as image:
            text=pytesseract.image_to_string(image, timeout=5)
        return text[:12000],"OCR_ASSISTED_RAW_TEXT"
    except Exception:
        return "","OCR_UNAVAILABLE"


def _ocr_candidates(text: str) -> list[dict]:
    """Extract rough label-adjacent strings for confirmation, never silently fill fields."""
    patterns={
        "crop":r"(?:crop|name of crop|seed crop)\s*[:：-]\s*([^\r\n]{1,80})",
        "variety":r"(?:variety|hybrid|cultivar)\s*[:：-]\s*([^\r\n]{1,100})",
        "brand":r"(?:brand|company|manufacturer|marketed by)\s*[:：-]\s*([^\r\n]{1,100})",
        "lot_number":r"(?:lot(?:\s*no)?|lot number|lot\s*#)\s*[:：-]\s*([A-Z0-9/._-]{2,60})",
        "batch_number":r"(?:batch(?:\s*no)?|batch number|batch\s*#)\s*[:：-]\s*([A-Z0-9/._-]{2,60})",
        "packing_date":r"(?:packing date|packed on|date of packing|mfg\.? date|manufacturing date)\s*[:：-]\s*([^\r\n]{3,40})",
        "validity_date":r"(?:valid up to|validity|use before|expiry date|valid till|valid upto)\s*[:：-]\s*([^\r\n]{3,40})",
        "germination_label_pct":r"(?:germination(?:\s*percentage)?|germination capacity)\s*[:：-]?\s*(\d{1,3}(?:\.\d+)?\s*%)",
        "purity_pct":r"(?:physical purity|purity)\s*[:：-]?\s*(\d{1,3}(?:\.\d+)?\s*%)",
        "net_weight":r"(?:net weight|net wt\.?|quantity)\s*[:：-]\s*([^\r\n]{1,40})",
        "mrp":r"(?:mrp|maximum retail price)\s*[:：-]?\s*(?:rs\.?|₹)?\s*([0-9,]+(?:\.[0-9]{1,2})?)",
        "dealer":r"(?:dealer|retailer|sold by)\s*[:：-]\s*([^\r\n]{1,120})",
        "certification_number":r"(?:certification(?:\s*no|\s*number)?|license(?:\s*no|\s*number)?|certificate\s*no)\s*[:：-]\s*([A-Z0-9/._-]{2,80})",
    }
    candidates=[]
    for field, pattern in patterns.items():
        match=re.search(pattern,text,re.IGNORECASE)
        if match:
            candidates.append({"field":field,"candidate":match.group(1).strip()[:120],"confidence":"NOT_SCORED","requires_farmer_confirmation":True})
    return candidates


@bp.post("/api/seed/scans")
@csrf_required
@require_auth(("farmer",))
@rate_limit(8,60)
def create_seed_scan():
    user=current_user()
    wanted=(("front_packet","front packet"),("back_packet","back packet"),("certification_tag","certification tag"),("qr_label","QR/barcode label"),("receipt","receipt"))
    photos=[];errors=[];ocr_texts=[]
    for field,label in wanted:
        up=request.files.get(field)
        if up and up.filename:
            try:
                saved=save_private_image(up,user["id"],f"seed_{field}")
                photos.append({"field":field,**saved})
                if field in {"front_packet","back_packet","certification_tag","qr_label"}:
                    text,status=_ocr_text(Path(current_app.config["UPLOAD_DIR"])/str(user["id"])/(saved["id"]+".jpg"))
                    if text:ocr_texts.append({"image_field":field,"text":text,"status":status})
            except UploadError as exc:errors.append(f"{label}: {exc}")
    if not photos:return api_error(errors[0] if errors else "Attach at least one packet, certification-tag, QR/barcode, or receipt image.")
    if errors:
        # Keep successfully stored evidence but tell the client which additional image failed.
        pass
    upload_ids=[x["id"] for x in photos if x["field"] != "receipt"]
    receipt=next((x["id"] for x in photos if x["field"] == "receipt"),None)
    candidates=[]
    for record in ocr_texts:
        candidates.extend({**candidate,"image_field":record["image_field"]} for candidate in _ocr_candidates(record.get("text","")))
    data={"crop":request.form.get("crop",""),"variety":request.form.get("variety",""),"brand":request.form.get("brand",""),"lot_number":request.form.get("lot_number",""),"batch_number":request.form.get("batch_number",""),"packing_date":request.form.get("packing_date",""),"validity_date":request.form.get("validity_date",""),"germination_label_pct":request.form.get("germination_label_pct") or None,"purity_pct":request.form.get("purity_pct") or None,"net_weight":request.form.get("net_weight") or None,"mrp":request.form.get("mrp") or None,"dealer":request.form.get("dealer",""),"certification_number":request.form.get("certification_number",""),"qr_content":request.form.get("qr_content",""),"packet_upload_ids":upload_ids,"receipt_upload_id":receipt,"ocr_text":ocr_texts,"ocr_candidates":candidates,"ocr_candidates_status":"REQUIRES_FARMER_CONFIRMATION","ocr_status":"OCR_ASSISTED_RAW_TEXT" if ocr_texts else "OCR_UNAVAILABLE","farmer_confirmed":False}
    farm_id=request.form.get("farm_id")
    if farm_id:data["farm_id"]=farm_id
    # Drop empty fields, but do not treat OCR candidates as farmer-confirmed values.
    data={k:v for k,v in data.items() if v not in (None,"")}
    try:
        row=_create("seed-scans",data,user)
    except (ValueError,PermissionError) as exc:
        return api_error(str(exc),403 if isinstance(exc,PermissionError) else 400,uploads=photos)
    serialized=_serialize(row,is_owner=True,resource="seed-scans")
    serialized["review_required_fields"]=_label_completeness(serialized.get("payload",{}))
    serialized["note"]="Images/OCR are evidence only. OCR text must be checked by the farmer. This scan does not verify seed authenticity, purity or germination."
    audit("seed_packet_scanned","seed-scans",user["id"],{"scan_id":row["id"],"upload_count":len(photos)})
    return jsonify(success=True,record=serialized,uploads=photos,upload_errors=errors),201


@bp.post("/api/seed/scans/<string:scan_id>/confirm")
@csrf_required
@require_auth(("farmer",))
@rate_limit(10,60)
def confirm_seed_scan(scan_id):
    data,error=json_body()
    if error:return error
    if data.get("confirmation") is not True:
        return api_error("Set confirmation=true only after reviewing every field against the physical packet.")
    supplied=data.get("confirmed_fields",{})
    if not isinstance(supplied,dict):return api_error("confirmed_fields must be an object of fields you checked.")
    editable={"crop","variety","brand","lot_number","batch_number","packing_date","validity_date","germination_label_pct","purity_pct","net_weight","mrp","dealer","certification_number","qr_content","farm_id"}
    unknown=set(supplied)-editable
    if unknown:return api_error("Unsupported confirmed field(s): "+", ".join(sorted(unknown)))
    user=current_user()
    with connect() as conn:
        row=conn.execute("SELECT * FROM seed_scans WHERE id=? AND owner_id=? AND status!='DELETED'",(scan_id,user["id"])).fetchone()
    if row is None:return api_error("Seed scan not found or not owned by this account.",404)
    prior=json_load(row["payload_json"])
    # The submitted map is explicit human confirmation; OCR text by itself is never copied into accepted fields.
    merged={key:prior.get(key) for key in editable if prior.get(key) not in (None,"")}
    merged.update(supplied)
    for key in list(merged):
        if merged[key] in (None,""):
            merged.pop(key)
    merged["farmer_confirmed"]=True
    try:
        seed_lot=_create("seed-lots",merged,user)
    except (ValueError,PermissionError) as exc:return api_error(str(exc),403 if isinstance(exc,PermissionError) else 400)
    prior["farmer_confirmed"]=True
    prior["confirmed_fields"]={k:v for k,v in merged.items() if k in editable}
    prior["linked_seed_lot_id"]=seed_lot["id"]
    prior["confirmed_at"]=utc_now()
    prior["confirmation_note"]="Farmer confirmed the entered fields against the packet; this does not certify authenticity or laboratory quality."
    with connect() as conn:
        conn.execute("UPDATE seed_scans SET payload_json=?,last_updated=?,updated_at=? WHERE id=? AND owner_id=?",(json_dump(prior),utc_now(),utc_now(),scan_id,user["id"]))
        updated=conn.execute("SELECT * FROM seed_scans WHERE id=? AND owner_id=?",(scan_id,user["id"])).fetchone()
    audit("seed_scan_fields_confirmed","seed-scans",user["id"],{"scan_id":scan_id,"seed_lot_id":seed_lot["id"],"fields":sorted(k for k in merged if k in editable)})
    return jsonify(success=True,scan=_serialize(updated,is_owner=True,resource="seed-scans"),seed_lot=_serialize(seed_lot,is_owner=True,resource="seed-lots"),message="Fields were saved as farmer-confirmed records; seed genuineness and laboratory quality remain unverified."),201


@bp.post("/api/seed/qr-decode")
@csrf_required
@require_auth(("farmer",))
@rate_limit(8,60)
def decode_seed_qr():
    upload=request.files.get("image")
    if not upload or not upload.filename:return api_error("Attach a photo containing a QR code or barcode.")
    try:
        from pyzbar.pyzbar import decode as decode_codes
    except Exception:
        return jsonify(success=False,status="UNAVAILABLE",data_type="UNAVAILABLE",error="QR/barcode decoding is not installed. Optional pyzbar and the system zbar library are required; you can enter the printed QR contents in the manual check instead."),503
    user=current_user()
    try:
        saved=save_private_image(upload,user["id"],"seed_qr_scan")
    except UploadError as exc:return api_error(str(exc))
    path=Path(current_app.config["UPLOAD_DIR"])/str(user["id"])/(saved["id"]+".jpg")
    try:
        with Image.open(path) as image:
            codes=decode_codes(image)
    except Exception:
        current_app.logger.exception("QR/barcode decoding failed")
        return jsonify(success=False,status="UNAVAILABLE",data_type="UNAVAILABLE",error="The code could not be decoded. Keep the private image evidence and enter the code manually."),503
    decoded=[]
    for code in codes[:10]:
        content=bytes(code.data).decode("utf-8","replace").strip()[:2000]
        parsed=urlparse(content)
        safe_url=content if parsed.scheme=="https" and parsed.hostname and not parsed.username and not parsed.password else None
        decoded.append({"format":str(getattr(code,"type","unknown"))[:40],"contents":content,"destination_url":safe_url,"trusted_official_domain":_is_trusted_official_https(content) if safe_url else False,"authenticity":"NOT_DETERMINED"})
    audit("seed_qr_decoded","uploads",user["id"],{"upload_id":saved["id"],"codes_found":len(decoded)})
    return jsonify(success=True,status="DECODED" if decoded else "NO_CODE_FOUND",data_type="USER_SUBMITTED",upload=saved,codes=decoded,warning="Decoded text is evidence only. Rythu Mitra does not fetch the destination or confirm seed authenticity; compare the brand/lot and use official verification."),200


@bp.post("/api/seed/qr-check")
@csrf_required
@require_auth(("farmer","expert","admin"))
@rate_limit(20,60)
def check_qr_content():
    data,error=json_body()
    if error:return error
    content=data.get("qr_content")
    if not isinstance(content,str) or not content.strip() or len(content)>2000:return api_error("Provide the QR/barcode contents as text.")
    content=content.strip();parsed=urlparse(content);url_like=parsed.scheme or parsed.netloc
    trusted=_is_trusted_official_https(content) if url_like else False
    params=parse_qs(parsed.query) if url_like else {}
    qr_lot=(params.get("lot") or params.get("lot_number") or params.get("batch") or params.get("batch_number") or [None])[0]
    user_lot=str(data.get("lot_number") or "").strip() or None
    user_brand=str(data.get("brand") or "").strip() or None
    qr_brand=(params.get("brand") or [None])[0]
    mismatch=False;comparisons=[]
    if user_lot and qr_lot:
        matched=user_lot.casefold()==str(qr_lot).casefold();comparisons.append({"field":"lot_number","matched":matched});mismatch|=not matched
    if user_brand and qr_brand:
        matched=user_brand.casefold()==str(qr_brand).casefold();comparisons.append({"field":"brand","matched":matched});mismatch|=not matched
    status="POSSIBLE_MISMATCH" if mismatch else "UNVERIFIED"
    safe_destination=content if parsed.scheme=="https" and parsed.hostname and not parsed.username and not parsed.password else None
    return jsonify(success=True,status=status,data_type="USER_SUBMITTED",contents=content,destination_url=safe_destination,url_scheme=parsed.scheme or None,https_url=safe_destination is not None,trusted_official_domain=trusted,comparison=comparisons,qr_lot_number=qr_lot,qr_brand=qr_brand,warning="Rythu Mitra does not open/fetch the QR destination or confirm seed authenticity. Check the destination independently and seek official verification.")


@bp.post("/api/seed/packet-check")
@csrf_required
@require_auth(("farmer","expert","admin"))
def packet_check():
    data,error=json_body()
    if error:return error
    completeness=_label_completeness(data)
    return jsonify(success=True,**completeness,verification_status="UNVERIFIED",authenticity="NOT_DETERMINED",next_steps=["Confirm every field against the physical packet.","Ask the dealer for a purchase bill.","Use the lot number with the relevant official authority if further checking is required."],note="Label completeness is not proof of genuineness, seed purity, germination, or certification status.")


@bp.post("/api/seed/germination")
@csrf_required
@require_auth(("farmer",))
@rate_limit(20,60)
def germination_test():
    data,error=json_body()
    if error:return error
    tested=data.get("tested_count");germinated=data.get("germinated_count")
    if isinstance(tested,bool) or isinstance(germinated,bool):return api_error("Counts must be whole numbers.")
    try:tested_i=int(tested);germinated_i=int(germinated)
    except (TypeError,ValueError):return api_error("tested_count and germinated_count must be whole numbers.")
    if tested_i<1 or tested_i>100000:return api_error("tested_count must be from 1 to 100000.")
    if germinated_i<0 or germinated_i>tested_i:return api_error("germinated_count cannot be negative or exceed tested_count.")
    if float(tested)!=tested_i or float(germinated)!=germinated_i:return api_error("Counts must be whole numbers.")
    payload={"tested_count":tested_i,"germinated_count":germinated_i,"test_date":data.get("test_date") or date.today().isoformat(),"test_method":data.get("test_method") or "Farmer-reported home screening","label_germination_pct":data.get("label_germination_pct"),"seed_lot_id":data.get("seed_lot_id"),"notes":data.get("notes","")}
    if payload["seed_lot_id"] in (None,""):payload.pop("seed_lot_id")
    if payload["label_germination_pct"] in (None,""):payload.pop("label_germination_pct")
    try:
        # The generic creator validates ownership, counts and required fields, then computes the percentage.
        row=_create("seed-test-results",payload,current_user())
    except (ValueError,PermissionError) as exc:return api_error(str(exc))
    result=_serialize(row,is_owner=True,resource="seed-test-results")
    result["germination_percentage"]=round(germinated_i/tested_i*100,2)
    result["screening_label"]="Informal home screening — not official laboratory certification"
    audit("seed_germination_test","seed-test-results",session.get("user_id"),{"id":row["id"]})
    return jsonify(success=True,record=result,disclaimer=result["screening_label"]),201


@bp.post("/api/seed/complaints")
@csrf_required
@require_auth(("farmer",))
@rate_limit(6,300)
def create_seed_complaint():
    data,error=json_body()
    if error:return error
    user=current_user()
    try:row=_create("seed-complaints",data,user)
    except PermissionError as exc:return api_error(str(exc),403)
    except ValueError as exc:return api_error(str(exc))
    record=_serialize(row,is_owner=True,resource="seed-complaints")
    audit("seed_complaint_created","seed-complaints",user["id"],{"id":row["id"],"complaint_number":record["complaint_number"]})
    return jsonify(success=True,record=record,official_submission={"submitted":False,"status":"NOT_FILED_BY_PLATFORM","message":"Saved in Rythu Mitra only. Submit through the relevant official channel yourself and add the external reference if one is issued."}),201


@bp.get("/api/seed/escalation")
def seed_escalation():
    return jsonify(success=True,status="OFFICIAL_LINKS_ONLY",data_type="CURATED",contacts=[
        {"name":"Telangana State Seed & Organic Certification Authority (TSSOCA)","url":"https://scadev.seedsgrowerp.com/newsite3/ContactTSSOCA.php","note":"Use its current official contact details; Rythu Mitra has not filed a complaint."},
        {"name":"Telangana government agriculture department", "url":"https://www.telangana.gov.in/departments/agriculture-and-co-operation/", "note":"Check district and mandal agriculture office details on the government page."},
        {"name":"T-SEED government portal", "url":"https://ossds.telangana.gov.in/", "note":"Portal information may relate to seed allocation/subsidy; it is not proof of a packet's authenticity."},
    ],note="Links are supplied for user-directed escalation only. No government integration or official complaint submission is claimed.")


@bp.get("/api/v1/uploads/<string:upload_id>")
@require_auth()
def get_private_upload(upload_id):
    user=current_user()
    path,error=upload_path(upload_id,user["id"],is_admin=user["role"]=="admin")
    if error and user["role"]=="expert":
        # Experts can view an upload only after its owner shares that exact ID
        # with a submitted/answered expert question. This is not broad file access.
        with connect() as conn:
            shared_rows=conn.execute("SELECT owner_id,payload_json FROM expert_questions WHERE status IN ('SUBMITTED','ANSWERED','APPROVED') AND owner_id IS NOT NULL").fetchall()
            upload_row=conn.execute("SELECT owner_id,stored_name FROM uploads WHERE id=?",(upload_id,)).fetchone()
        shared=False
        if upload_row is not None:
            for question in shared_rows:
                payload=json_load(question["payload_json"])
                attachments=payload.get("attachment_ids",[])
                if question["owner_id"]==upload_row["owner_id"] and isinstance(attachments,list) and upload_id in {str(item) for item in attachments}:
                    shared=True;break
            if shared:
                path=Path(current_app.config["UPLOAD_DIR"])/str(upload_row["owner_id"])/upload_row["stored_name"]
                error=None
    if error:return api_error(error,404 if error=="Upload not found." else 403)
    if not path or not path.is_file():return api_error("Upload file is unavailable.",404)
    return send_file(path,mimetype="image/jpeg",as_attachment=False,download_name="evidence.jpg",max_age=0)
