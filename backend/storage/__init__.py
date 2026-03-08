"""Backend storage package for SpeedRay."""

from .cloudinary_client import (
    add_annotation,
    build_annotated_image_url,
    build_annotated_image_url_with_text,
    diseases_to_annotations,
    get_metadata,
    regions_to_annotations,
    upload_image,
)
from .solana_client import submit_log

__all__ = [
    "upload_image",
    "add_annotation",
    "build_annotated_image_url",
    "build_annotated_image_url_with_text",
    "diseases_to_annotations",
    "get_metadata",
    "regions_to_annotations",
    "submit_log",
]
