import os
import uuid
import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from bson import ObjectId

from app.models.detection import BloodTestData, DetectionResponse
from app.services.prediction import predict_from_blood_test, predict_from_image
from app.database import get_detections_collection
from app.dependencies import get_current_user
from app.config import settings

router = APIRouter(prefix="/api/predict", tags=["Predictions"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


def _detection_to_response(detection: dict) -> DetectionResponse:
    return DetectionResponse(
        id=str(detection["_id"]),
        user_id=str(detection["user_id"]),
        patient_name=detection["patient_name"],
        type=detection["type"],
        prediction=detection["prediction"],
        confidence=detection["confidence"],
        status=detection["status"],
        image_data=detection.get("image_data"),
        blood_test_data=detection.get("blood_test_data"),
        notes=detection.get("notes"),
        created_at=detection["created_at"],
        updated_at=detection["updated_at"],
    )


@router.post("/image", response_model=DetectionResponse)
async def predict_from_image_upload(
    file: UploadFile = File(...),
    patient_name: str = Form(...),
    current_user: dict = Depends(get_current_user),
):
    """Upload a blood smear image and get a prediction."""
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image type. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}",
        )

    # Validate file size
    contents = await file.read()
    max_size = settings.max_upload_size_mb * 1024 * 1024
    if len(contents) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.max_upload_size_mb}MB",
        )

    # Save file to disk
    upload_dir = settings.upload_dir
    os.makedirs(upload_dir, exist_ok=True)
    file_ext = os.path.splitext(file.filename or "image.png")[1]
    saved_name = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(upload_dir, saved_name)
    with open(file_path, "wb") as f:
        f.write(contents)

    # Run prediction with the saved image path
    prediction, confidence = predict_from_image(file_path)
    now = datetime.now(timezone.utc)

    detection = {
        "user_id": ObjectId(current_user["_id"]),
        "patient_name": patient_name,
        "type": "image",
        "prediction": prediction,
        "confidence": confidence,
        "status": "completed",
        "image_data": {
            "file_name": saved_name,
            "original_name": file.filename,
            "file_size": len(contents),
            "content_type": file.content_type,
        },
        "blood_test_data": None,
        "notes": None,
        "created_at": now,
        "updated_at": now,
    }

    detections = await get_detections_collection()
    result = await detections.insert_one(detection)
    detection["_id"] = result.inserted_id

    return _detection_to_response(detection)


@router.post("/blood-test", response_model=DetectionResponse)
async def predict_from_blood_test_data(
    patient_name: str = Form(...),
    blood_data: str = Form(...),
    current_user: dict = Depends(get_current_user),
):
    """Submit blood test (CBC) parameters and get a prediction."""
    parsed = BloodTestData.model_validate(json.loads(blood_data))
    prediction, confidence = predict_from_blood_test(parsed)
    now = datetime.now(timezone.utc)

    detection = {
        "user_id": ObjectId(current_user["_id"]),
        "patient_name": patient_name,
        "type": "blood_test",
        "prediction": prediction,
        "confidence": confidence,
        "status": "completed",
        "image_data": None,
        "blood_test_data": parsed.model_dump(),
        "notes": None,
        "created_at": now,
        "updated_at": now,
    }

    detections = await get_detections_collection()
    result = await detections.insert_one(detection)
    detection["_id"] = result.inserted_id

    return _detection_to_response(detection)
