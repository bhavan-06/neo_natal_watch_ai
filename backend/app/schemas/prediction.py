from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PredictionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: Optional[str] = None
    pregnancy_id: Optional[int] = None
    assessment_id: Optional[int] = None
    prediction_type: Optional[str] = None
    target: Optional[str] = None
    predicted_value: Optional[float] = None
    confidence: Optional[float] = None
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    prediction_horizon: Optional[str] = None
    timestamp: Optional[datetime] = None
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    xgb_score: Optional[float] = None
    cnn_lstm_score: Optional[float] = None
    ae_score: Optional[float] = None
    transformer_score: Optional[float] = None
    created_at: Optional[datetime] = None
