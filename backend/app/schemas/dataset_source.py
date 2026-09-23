from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class DatasetSourceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dataset_name: Optional[str] = None
    source_url: Optional[str] = None
    license: Optional[str] = None
    data_type: Optional[str] = None
    description: Optional[str] = None
    imported_at: Optional[datetime] = None
    notes: Optional[str] = None


class ImportJobSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dataset_id: Optional[int] = None
    file_name: Optional[str] = None
    rows_detected: Optional[int] = 0
    rows_imported: Optional[int] = 0
    rows_rejected: Optional[int] = 0
    status: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ImportErrorLogSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: Optional[int] = None
    row_data: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None

