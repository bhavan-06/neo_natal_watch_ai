from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class NicuAdmissionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    newborn_id: Optional[int] = None
    admission_date: Optional[datetime] = None
    discharge_date: Optional[datetime] = None
    admission_reason: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
