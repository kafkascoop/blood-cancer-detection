from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId

from app.models.detection import DetectionResponse
from app.database import get_detections_collection
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/results", tags=["Results"])


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


@router.get("", response_model=list[DetectionResponse])
async def list_results(
    limit: int = 20,
    skip: int = 0,
    current_user: dict = Depends(get_current_user),
):
    """List all detection results for the current user."""
    detections = await get_detections_collection()
    cursor = (
        detections.find({"user_id": ObjectId(current_user["_id"])})
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )
    results = await cursor.to_list(length=limit)
    return [_detection_to_response(r) for r in results]


@router.get("/{detection_id}", response_model=DetectionResponse)
async def get_result(
    detection_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get a single detection result by ID."""
    detections = await get_detections_collection()
    detection = await detections.find_one({
        "_id": ObjectId(detection_id),
        "user_id": ObjectId(current_user["_id"]),
    })

    if detection is None:
        raise HTTPException(status_code=404, detail="Detection result not found")

    return _detection_to_response(detection)
