from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ChatHistorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: Optional[str] = None
    pregnancy_id: Optional[int] = None
    newborn_id: Optional[int] = None
    user_role: Optional[str] = None
    question: Optional[str] = None
    response: Optional[str] = None
    model_used: Optional[str] = None
    created_at: Optional[datetime] = None
