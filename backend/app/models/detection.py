from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class BloodTestData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    wbc: float = Field(ge=0)
    rbc: float = Field(ge=0)
    hemoglobin: float = Field(ge=0)
    platelets: float = Field(ge=0)
    neutrophils: float = Field(ge=0)
    lymphocytes: float = Field(ge=0)
    monocytes: float = Field(ge=0)
    eosinophils: float = Field(ge=0)
    basophils: float = Field(ge=0)
    blast_cells: float = Field(ge=0, alias="blastCells")


class ImageUploadData(BaseModel):
    file_name: str
    file_size: int
    content_type: str


class DetectionCreate(BaseModel):
    patient_name: str = Field(min_length=1, max_length=100)
    type: str = Field(pattern="^(image|blood_test)$")
    notes: Optional[str] = None


class DetectionResponse(BaseModel):
    id: str
    user_id: str
    patient_name: str
    type: str
    prediction: str
    confidence: float
    status: str
    image_data: Optional[dict] = None
    blood_test_data: Optional[dict] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DetectionStats(BaseModel):
    total_tests: int = 0
    normal_results: int = 0
    abnormal_detections: int = 0
    pending_results: int = 0
    monthly_tests: list[int] = [0] * 12
