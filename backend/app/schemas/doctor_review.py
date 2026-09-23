from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DoctorReviewSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: Optional[str] = None
    pregnancy_id: Optional[int] = None
    clinician_id: Optional[str] = None
    review_date: Optional[datetime] = None
    findings: Optional[str] = None
    assessment: Optional[str] = None
    recommendations: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
