from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class TimelineEntrySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: Optional[datetime] = None
    type: str
    details: Optional[str] = None

