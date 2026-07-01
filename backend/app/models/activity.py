from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ActivityLogEntry(BaseModel):
    """Schema for a single activity log entry stored in MongoDB."""

    id: str = ""
    user_id: Optional[str] = None
    username: Optional[str] = None
    method: str = Field(..., pattern=r"^(GET|POST|PUT|PATCH|DELETE|OPTIONS|HEAD)$")
    endpoint: str = ""
    status_code: int = 0
    duration_ms: Optional[int] = None
    detail: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = {"from_attributes": True}


class ActivityLogResponse(BaseModel):
    """Response model for a single activity log."""

    id: str
    user_id: Optional[str] = None
    username: Optional[str] = None
    method: str
    endpoint: str
    status_code: int
    duration_ms: Optional[int] = None
    detail: Optional[str] = None
    created_at: datetime


class ActivityLogStats(BaseModel):
    """Aggregated activity log statistics."""

    total_logs: int = 0
    method_counts: dict[str, int] = {}
    status_code_counts: dict[str, int] = {}
    endpoint_counts: dict[str, int] = {}
    monthly_logs: list[int] = [0] * 12
