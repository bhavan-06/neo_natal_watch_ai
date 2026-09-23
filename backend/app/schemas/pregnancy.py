from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class PregnancySchema(BaseModel):
    id: int
    patient_id: str
    pregnancy_code: Optional[str] = None
    pregnancy_status: Optional[str] = None
    conception_date: Optional[datetime] = None
    estimated_due_date: Optional[datetime] = None
    pregnancy_start: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

