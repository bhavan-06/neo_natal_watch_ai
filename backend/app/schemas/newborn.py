from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class NewbornSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pregnancy_id: Optional[int] = None
    newborn_code: Optional[str] = None
    name: Optional[str] = None
    birth_date: Optional[datetime] = None
    gestational_age_at_birth: Optional[float] = None
    birth_weight: Optional[float] = None
    birth_length: Optional[float] = None
    birth_status: Optional[str] = None
    created_at: Optional[datetime] = None
