from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class NicuVitalSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nicu_admission_id: Optional[int] = None
    timestamp: Optional[datetime] = None
    heart_rate: Optional[float] = None
    spo2: Optional[float] = None
    respiratory_rate: Optional[float] = None
    temperature: Optional[float] = None
    source: Optional[str] = None
    created_at: Optional[datetime] = None
