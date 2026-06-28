"""
Settings Router: Manage app-level configuration at runtime.

Stores settings in a singleton MongoDB document so they persist
across restarts. Falls back to defaults from config.py.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from bson import ObjectId

from app.database import get_settings_collection
from app.dependencies import get_current_user
from app.config import settings as app_config

router = APIRouter(prefix="/api/settings", tags=["Settings"])

SETTINGS_DOC_ID = "global_config"


class AppSettings(BaseModel):
    app_name: str = Field(default="HematoScan", max_length=64)
    image_model_mode: str = Field(
        default="auto",
        pattern=r"^(auto|cnn|opencv)$",
        description="'auto' = try CNN first, fallback to OpenCV+GB; 'cnn' = only CNN; 'opencv' = only OpenCV+GB",
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _get_or_create_settings() -> dict:
    """Get the settings document from MongoDB, creating default if missing."""
    col = await get_settings_collection()
    doc = await col.find_one({"_id": SETTINGS_DOC_ID})
    if doc is None:
        default = AppSettings()
        await col.insert_one({
            "_id": SETTINGS_DOC_ID,
            "app_name": default.app_name,
            "image_model_mode": default.image_model_mode,
        })
        doc = {
            "_id": SETTINGS_DOC_ID,
            "app_name": default.app_name,
            "image_model_mode": default.image_model_mode,
        }
    return doc


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("", response_model=AppSettings)
async def get_settings(current_user: dict = Depends(get_current_user)):
    """Get current application settings."""
    doc = await _get_or_create_settings()
    return AppSettings(
        app_name=doc.get("app_name", "HematoScan"),
        image_model_mode=doc.get("image_model_mode", "auto"),
    )


@router.put("", response_model=AppSettings)
async def update_settings(
    body: AppSettings,
    current_user: dict = Depends(get_current_user),
):
    """Update application settings."""
    col = await get_settings_collection()
    await col.update_one(
        {"_id": SETTINGS_DOC_ID},
        {"$set": {
            "app_name": body.app_name,
            "image_model_mode": body.image_model_mode,
        }},
        upsert=True,
    )
    return body


@router.get("/deep-learning-status")
async def deep_learning_status(current_user: dict = Depends(get_current_user)):
    """Check if deep learning frameworks (TF/PyTorch) and trained model files are available."""
    import os
    from app.services.model_service import CNN_MODEL_PATH

    try:
        import tensorflow as tf
        tf_available = True
        tf_version = tf.__version__
    except ImportError:
        tf_available = False
        tf_version = None

    try:
        import torch
        pt_available = True
        pt_version = torch.__version__
    except ImportError:
        pt_available = False
        pt_version = None

    cnn_model_file_exists = os.path.exists(CNN_MODEL_PATH)
    framework_available = tf_available or pt_available

    return {
        "tensorflow_available": tf_available,
        "tensorflow_version": tf_version,
        "pytorch_available": pt_available,
        "pytorch_version": pt_version,
        "framework_available": framework_available,
        "cnn_available": framework_available and cnn_model_file_exists,
        "cnn_model_file_exists": cnn_model_file_exists,
    }
