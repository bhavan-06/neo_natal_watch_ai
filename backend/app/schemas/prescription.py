from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PrescriptionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: Optional[str] = None
    pregnancy_id: Optional[int] = None
    clinician_id: Optional[str] = None
    medication_name: Optional[str] = None
    dosage: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
