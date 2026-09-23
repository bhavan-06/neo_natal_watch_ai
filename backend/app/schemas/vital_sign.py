from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class VitalSignSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    heart_rate: Optional[float] = None
    spo2: Optional[float] = None
    respiratory_rate: Optional[float] = None
    temperature: Optional[float] = None
    systolic_bp: Optional[float] = None
    diastolic_bp: Optional[float] = None

