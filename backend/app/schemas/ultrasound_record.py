from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UltrasoundRecordSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pregnancy_id: Optional[int] = None
    assessment_id: Optional[int] = None
    ultrasound_date: Optional[datetime] = None
    gestational_age: Optional[float] = None
    image_reference: Optional[str] = None
    findings: Optional[str] = None
    source_dataset: Optional[str] = None
    metadata_json: Optional[str] = None
    created_at: Optional[datetime] = None
