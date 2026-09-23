from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DopplerResultSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pregnancy_id: Optional[int] = None
    assessment_id: Optional[int] = None
    gestational_age: Optional[float] = None
    uterine_artery_pi: Optional[float] = None
    uterine_artery_status: Optional[str] = None
    umbilical_artery_status: Optional[str] = None
    other_values: Optional[str] = None
    test_date: Optional[datetime] = None
    source: Optional[str] = None
    recorded_at: Optional[datetime] = None
