"""Private, re-encoded image storage. Uploaded files are never served as static assets."""
from __future__ import annotations
import hashlib
import io
import secrets
from pathlib import Path
from PIL import Image, ImageOps, UnidentifiedImageError
from flask import current_app
from werkzeug.datastructures import FileStorage
from ..db import connect, utc_now

ALLOWED_DECODE_FORMATS = {"JPEG", "PNG", "WEBP"}

class UploadError(ValueError):
    pass


def save_private_image(upload: FileStorage, owner_id: int, category: str) -> dict:
    if upload is None or not upload.filename:
        raise UploadError("Choose an image file.")
    extension = Path(upload.filename).suffix.lower()
    if extension not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise UploadError("Use a .jpg, .jpeg, .png, or .webp image file.")
    raw = upload.stream.read(current_app.config["MAX_UPLOAD_BYTES"] + 1)
    if not raw:
        raise UploadError("The selected image is empty.")
    if len(raw) > current_app.config["MAX_UPLOAD_BYTES"]:
        raise UploadError("Each image must be no larger than the configured upload limit.")
    try:
        Image.MAX_IMAGE_PIXELS = current_app.config.get("MAX_IMAGE_PIXELS", 20_000_000)
        with Image.open(io.BytesIO(raw)) as probe:
            fmt = (probe.format or "").upper()
            if fmt not in ALLOWED_DECODE_FORMATS:
                raise UploadError("Use a real JPEG, PNG, or WebP image.")
            dimensions = probe.width * probe.height
            if dimensions > current_app.config.get("MAX_IMAGE_PIXELS", 20_000_000):
                raise UploadError("Image dimensions exceed the safety limit.")
            if probe.width < 16 or probe.height < 16:
                raise UploadError("Image dimensions are too small to use.")
            expected = {"JPEG": {".jpg", ".jpeg"}, "PNG": {".png"}, "WEBP": {".webp"}}
            if extension not in expected[fmt]:
                raise UploadError("The file extension does not match the decoded image format.")
            claimed = (upload.mimetype or "").lower()
            actual_mime = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}[fmt]
            if claimed.startswith("image/") and claimed != actual_mime:
                raise UploadError("The declared image type does not match the decoded image format.")
            probe.verify()
        with Image.open(io.BytesIO(raw)) as source:
            image = ImageOps.exif_transpose(source).convert("RGB")
            if image.width < 16 or image.height < 16:
                raise UploadError("Image dimensions are too small to use.")
            if image.width * image.height > current_app.config.get("MAX_IMAGE_PIXELS", 20_000_000):
                raise UploadError("Image dimensions exceed the safety limit.")
            output = io.BytesIO()
            image.save(output, format="JPEG", quality=88, optimize=True)
            cleaned = output.getvalue()
    except UploadError:
        raise
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise UploadError("The upload is not a safe, readable image.") from exc
    file_id = secrets.token_urlsafe(18).replace("-", "").replace("_", "")[:24]
    stored_name = f"{file_id}.jpg"
    root = Path(current_app.config["UPLOAD_DIR"])
    target_dir = root / str(owner_id)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / stored_name
    target.write_bytes(cleaned)
    stamp = utc_now()
    original_name = Path(upload.filename).name[:180]
    digest = hashlib.sha256(cleaned).hexdigest()
    with connect() as conn:
        conn.execute("INSERT INTO uploads(id,owner_id,category,stored_name,media_type,byte_size,sha256,original_name,created_at) VALUES(?,?,?,?,?,?,?,?,?)",
                     (file_id, owner_id, category[:60], stored_name, "image/jpeg", len(cleaned), digest, original_name, stamp))
    return {"id": file_id, "category": category, "media_type": "image/jpeg", "byte_size": len(cleaned), "sha256": digest, "created_at": stamp}


def upload_path(upload_id: str, owner_id: int, *, is_admin: bool = False) -> tuple[Path | None, str | None]:
    with connect() as conn:
        row = conn.execute("SELECT * FROM uploads WHERE id=?", (upload_id,)).fetchone()
    if row is None:
        return None, "Upload not found."
    if row["owner_id"] != owner_id and not is_admin:
        return None, "You cannot access this upload."
    return Path(current_app.config["UPLOAD_DIR"]) / str(row["owner_id"]) / row["stored_name"], None
