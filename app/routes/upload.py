import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.config import UPLOAD_DIR, MAX_UPLOAD_SIZE_BYTES, ALLOWED_IMAGE_TYPES

router = APIRouter(prefix="/api/upload", tags=["Uploads"])

@router.post("", summary="Upload Image (Photo / Sighting / Report)")
async def upload_image(file: UploadFile = File(...)):
    """
    Handle photo uploads with size enforcement, MIME verification, and unique filename generation.
    Returns the public relative URL of the uploaded image.
    """
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image type '{file.content_type}'. Allowed types: JPG, PNG, WEBP.",
        )

    # Read content with size check
    contents = await file.read()
    if len(contents) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds maximum limit of 5MB.",
        )

    ext = Path(file.filename or "image.jpg").suffix.lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        ext = ".jpg"

    safe_filename = f"{uuid.uuid4().hex}{ext}"
    dest_path = UPLOAD_DIR / safe_filename
    with open(dest_path, "wb") as f:
        f.write(contents)

    return {
        "status": "SUCCESS",
        "filename": safe_filename,
        "url": f"/uploads/{safe_filename}",
        "size_bytes": len(contents),
    }
