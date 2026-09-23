from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class GrowthAnalysisSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pregnancy_id: Optional[int] = None
    predicted_efw_percentile: Optional[float] = None
    actual_efw_percentile: Optional[float] = None
    growth_variance: Optional[float] = None
    evaluation_status: Optional[str] = None
    contributing_patterns: Optional[str] = None
    model_version: Optional[str] = None
    generated_at: Optional[datetime] = None
