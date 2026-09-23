from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

class MaternalProfileSchema(BaseModel):
    id: int
    pregnancy_id: int
    maternal_age: Optional[float] = None
    bmi: Optional[float] = None
    map_value: Optional[float] = None
    chronic_hypertension: bool = False
    diabetes: bool = False
    other_conditions: Optional[str] = None
    recorded_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

