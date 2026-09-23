"""
Pydantic schemas for the FastAPI backend.
Defines the expected shape of incoming API requests and outgoing responses.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class VitalSignRecord(BaseModel):
    timestamp: str
    patient_id: str
    heart_rate: float
    spo2: float
    respiratory_rate: float
    temperature: float
    systolic_bp: float
    diastolic_bp: float

class PredictionRequest(BaseModel):
    """
    We need at least 60 records (1 hour of 1-minute intervals) 
    to calculate the 60-minute rolling features for XGBoost.
    """
    records: List[VitalSignRecord] = Field(..., min_length=60, description="List of at least 60 consecutive 1-minute vital sign readings.")

class ModelProbabilities(BaseModel):
    xgboost: float
    cnn_lstm: float
    autoencoder: float
    transformer: float

class PredictionResponse(BaseModel):
    patient_id: str
    timestamp: str
    risk_score: float
    risk_level: str
    individual_models: ModelProbabilities
    message: str

