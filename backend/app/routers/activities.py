"""
Activity Logs Router

Provides endpoints to query the activity_logs collection with filtering
by HTTP method, status code, date range, and endpoint path.
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from bson import ObjectId

from app.models.activity import ActivityLogEntry, ActivityLogResponse, ActivityLogStats
from app.database import get_activities_collection
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/activities", tags=["Activities"])

# ---------- Allowed HTTP methods for filtering ----------
VALID_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"}


def _doc_to_response(doc: dict) -> ActivityLogResponse:
    """Convert a MongoDB document to a response model."""
    return ActivityLogResponse(
        id=str(doc["_id"]),
        user_id=doc.get("user_id"),
        username=doc.get("username"),
        method=doc["method"],
        endpoint=doc["endpoint"],
        status_code=doc["status_code"],
        duration_ms=doc.get("duration_ms"),
        detail=doc.get("detail"),
        created_at=doc["created_at"],
    )


# =============================================================================
# List Activity Logs (with filters)
# =============================================================================


@router.get("", response_model=list[ActivityLogResponse])
async def list_activities(
    method: Optional[str] = Query(None, description="Filter by HTTP method (GET, POST, PUT, PATCH, DELETE)"),
    status_code: Optional[int] = Query(None, ge=100, le=599, description="Filter by HTTP status code"),
    endpoint: Optional[str] = Query(None, description="Filter by endpoint path (partial match)"),
    date_from: Optional[datetime] = Query(None, description="Start date (ISO 8601)"),
    date_to: Optional[datetime] = Query(None, description="End date (ISO 8601)"),
    user_only: bool = Query(False, description="Only show activities for the current user"),
    limit: int = Query(50, ge=1, le=500, description="Number of results per page"),
    skip: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: dict = Depends(get_current_user),
):
    """List activity logs with optional filters.

    Supports filtering by:
    - `method`: GET, POST, PUT, PATCH, DELETE
    - `status_code`: e.g. 200, 404, 500
    - `endpoint`: partial text match on the request path
    - `date_from` / `date_to`: ISO 8601 date range
    - `user_only`: when True, only returns logs for the authenticated user
    """
    # Build the query filter
    query: dict = {}

    if method:
        method_upper = method.upper()
        if method_upper not in VALID_METHODS:
            raise HTTPException(status_code=400, detail=f"Invalid method '{method}'. Allowed: {', '.join(sorted(VALID_METHODS))}")
        query["method"] = method_upper

    if status_code is not None:
        query["status_code"] = status_code

    if endpoint:
        query["endpoint"] = {"$regex": endpoint, "$options": "i"}

    if date_from or date_to:
        date_filter: dict = {}
        if date_from:
            date_filter["$gte"] = date_from
        if date_to:
            date_filter["$lte"] = date_to
        if date_filter:
            query["created_at"] = date_filter

    if user_only:
        query["user_id"] = str(current_user["_id"])

    col = await get_activities_collection()
    cursor = (
        col.find(query)
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )
    docs = await cursor.to_list(length=limit)
    return [_doc_to_response(d) for d in docs]


# =============================================================================
# Get Activity Log Stats
# =============================================================================


@router.get("/stats", response_model=ActivityLogStats)
async def get_activity_stats(
    current_user: dict = Depends(get_current_user),
):
    """Get aggregated statistics for activity logs.

    Returns counts grouped by method, status code, endpoint, and monthly distribution.
    """
    col = await get_activities_collection()

    # Total count
    total_logs = await col.count_documents({})

    # Count by method
    method_pipeline = [
        {"$group": {"_id": "$method", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
    ]
    method_results = await col.aggregate(method_pipeline).to_list(length=20)
    method_counts = {r["_id"]: r["count"] for r in method_results}

    # Count by status code (grouped into ranges)
    status_pipeline = [
        {
            "$group": {
                "_id": {
                    "$switch": {
                        "branches": [
                            {"case": {"$and": [{"$gte": ["$status_code", 200]}, {"$lt": ["$status_code", 300]}]}, "then": "2xx Success"},
                            {"case": {"$and": [{"$gte": ["$status_code", 300]}, {"$lt": ["$status_code", 400]}]}, "then": "3xx Redirect"},
                            {"case": {"$and": [{"$gte": ["$status_code", 400]}, {"$lt": ["$status_code", 500]}]}, "then": "4xx Client Error"},
                        ],
                        "default": "5xx Server Error",
                    }
                },
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"_id": 1}},
    ]
    status_results = await col.aggregate(status_pipeline).to_list(length=10)
    status_counts = {r["_id"]: r["count"] for r in status_results}

    # Count by endpoint (top 20)
    endpoint_pipeline = [
        {"$group": {"_id": "$endpoint", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 20},
    ]
    endpoint_results = await col.aggregate(endpoint_pipeline).to_list(length=20)
    endpoint_counts = {r["_id"]: r["count"] for r in endpoint_results}

    # Monthly distribution
    monthly_pipeline = [
        {
            "$group": {
                "_id": {"$month": "$created_at"},
                "count": {"$sum": 1},
            }
        },
    ]
    monthly_results = await col.aggregate(monthly_pipeline).to_list(length=12)
    monthly_logs = [0] * 12
    for r in monthly_results:
        month_idx = r["_id"] - 1
        if 0 <= month_idx < 12:
            monthly_logs[month_idx] = r["count"]

    return ActivityLogStats(
        total_logs=total_logs,
        method_counts=method_counts,
        status_code_counts=status_counts,
        endpoint_counts=endpoint_counts,
        monthly_logs=monthly_logs,
    )


# =============================================================================
# Get Single Activity Log
# =============================================================================


@router.get("/{log_id}", response_model=ActivityLogResponse)
async def get_activity_log(
    log_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get a single activity log entry by ID."""
    col = await get_activities_collection()
    doc = await col.find_one({"_id": ObjectId(log_id)})

    if doc is None:
        raise HTTPException(status_code=404, detail="Activity log not found")

    return _doc_to_response(doc)
