from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ClinicalEventSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: Optional[str] = None
    pregnancy_id: Optional[int] = None
    event_type: Optional[str] = None
    event_date: Optional[datetime] = None
    details: Optional[str] = None
    created_at: Optional[datetime] = None
