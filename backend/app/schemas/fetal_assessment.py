from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class FetalAssessmentSchema(BaseModel):
    id: int
    pregnancy_id: int
    gestational_age_weeks: Optional[float] = None
    trimester: Optional[int] = None
    crl: Optional[float] = None
    nt: Optional[float] = None
    nasal_bone: Optional[str] = None
    efw: Optional[float] = None
    efw_percentile: Optional[float] = None
    growth_measurements: Optional[str] = None
    assessment_date: Optional[datetime] = None
    source: Optional[str] = None
    recorded_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

