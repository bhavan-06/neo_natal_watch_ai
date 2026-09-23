from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class LabResultSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pregnancy_id: Optional[int] = None
    assessment_id: Optional[int] = None
    papp_a: Optional[float] = None
    plgf: Optional[float] = None
    free_beta_hcg: Optional[float] = None
    test_date: Optional[datetime] = None
    gestational_age: Optional[float] = None
    status: Optional[str] = None
    source: Optional[str] = None
    recorded_at: Optional[datetime] = None
