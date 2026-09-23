from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ModelOutputSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: Optional[str] = None
    pregnancy_id: Optional[int] = None
    newborn_id: Optional[int] = None
    nicu_admission_id: Optional[int] = None
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    input_reference: Optional[str] = None
    output_type: Optional[str] = None
    output_value: Optional[float] = None
    confidence: Optional[float] = None
    explanation_reference: Optional[str] = None
    created_at: Optional[datetime] = None
