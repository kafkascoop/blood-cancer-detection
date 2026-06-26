from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from bson import ObjectId

from app.models.detection import DetectionResponse, DetectionStats
from app.database import get_detections_collection
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


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


@router.get("")
async def get_dashboard(
    current_user: dict = Depends(get_current_user),
):
    """Get dashboard statistics and recent results."""
    detections = await get_detections_collection()
    user_id = ObjectId(current_user["_id"])

    # Get total counts
    total_tests = await detections.count_documents({"user_id": user_id})
    normal_results = await detections.count_documents({
        "user_id": user_id, "prediction": "Normal"
    })
    abnormal_detections = await detections.count_documents({
        "user_id": user_id,
        "prediction": {"$in": ["Benign", "Malignant"]},
    })
    pending_results = await detections.count_documents({
        "user_id": user_id, "status": "pending"
    })

    # Get monthly distribution
    monthly_tests = [0] * 12

    pipeline = [
        {"$match": {"user_id": user_id}},
        {
            "$group": {
                "_id": {"$month": "$created_at"},
                "count": {"$sum": 1},
            }
        },
    ]
    monthly_results = await detections.aggregate(pipeline).to_list(length=12)
    for r in monthly_results:
        month_idx = r["_id"] - 1  # MongoDB months are 1-indexed
        if 0 <= month_idx < 12:
            monthly_tests[month_idx] = r["count"]

    # Get recent results
    cursor = (
        detections.find({"user_id": user_id})
        .sort("created_at", -1)
        .limit(5)
    )
    recent_results = await cursor.to_list(length=5)

    stats = DetectionStats(
        total_tests=total_tests,
        normal_results=normal_results,
        abnormal_detections=abnormal_detections,
        pending_results=pending_results,
        monthly_tests=monthly_tests,
    )

    return {
        "stats": stats.model_dump(),
        "recent_results": [_detection_to_response(r) for r in recent_results],
    }
