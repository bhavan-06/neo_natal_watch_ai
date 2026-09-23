from sqlalchemy.orm import Session
from . import models
from backend.app.schemas import predict_schema
from datetime import datetime

def ensure_patient_exists(db: Session, patient_id: str):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        patient = models.Patient(id=patient_id, name=f"Patient {patient_id}")
        db.add(patient)
        db.commit()
    return patient

def create_vital_signs(db: Session, records: list[predict_schema.VitalSignRecord]):
    if not records:
        return
    
    patient_id = records[0].patient_id
    ensure_patient_exists(db, patient_id)
    
    db_records = []
    for r in records:
        db_record = models.VitalSign(
            patient_id=r.patient_id,
            timestamp=datetime.fromisoformat(r.timestamp),
            heart_rate=r.heart_rate,
            spo2=r.spo2,
            respiratory_rate=r.respiratory_rate,
            temperature=r.temperature,
            systolic_bp=r.systolic_bp,
            diastolic_bp=r.diastolic_bp
        )
        db_records.append(db_record)
        
    db.bulk_save_objects(db_records)
    db.commit()

def save_prediction(db: Session, result: dict):
    ensure_patient_exists(db, result["patient_id"])
    
    db_prediction = models.Prediction(
        patient_id=result["patient_id"],
        timestamp=datetime.fromisoformat(result["timestamp"]),
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        xgb_score=result["individual_models"]["xgboost"],
        cnn_lstm_score=result["individual_models"]["cnn_lstm"],
        ae_score=result["individual_models"]["autoencoder"],
        transformer_score=result["individual_models"]["transformer"]
    )
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction

