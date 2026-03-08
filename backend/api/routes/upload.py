"""Image upload; delegates to Cloudinary (SpeedRay)."""

from fastapi import APIRouter, File, UploadFile, HTTPException, Query

from ...storage import get_metadata, upload_image

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/image")
async def upload_xray_image(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "Expected image file")
    content = await file.read()
    result = upload_image(content, folder="speedray")
    return result


@router.get("/metadata")
async def upload_metadata(public_id: str = Query(..., description="Cloudinary public_id")):
    """Return Cloudinary image metadata and stored annotations (bbox + severity)."""
    data = get_metadata(public_id)
    if not data and public_id:
        raise HTTPException(404, "Image not found")
    return data
