from datetime import datetime
from pydantic import BaseModel, ConfigDict

class PatientSchema(BaseModel):
    id: str
    patient_code: str | None = None
    name: str | None = None
    date_of_birth: datetime | None = None
    contact_info: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

