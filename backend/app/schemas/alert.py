from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AlertSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: Optional[str] = None
    newborn_id: Optional[int] = None
    nicu_admission_id: Optional[int] = None
    alert_type: Optional[str] = None
    severity: Optional[str] = None
    risk_score: Optional[float] = None
    triggering_factors: Optional[str] = None
    model_version: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
