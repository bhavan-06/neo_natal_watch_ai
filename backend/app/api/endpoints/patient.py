from fastapi import APIRouter, Depends, HTTPException
from typing import List, Any, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.db.models import (
    Patient, Pregnancy, FetalAssessment, Prediction, GrowthAnalysis,
    ClinicalEvent, Newborn, NicuAdmission, NicuVital, Alert,
    MaternalProfile, UltrasoundRecord, LabResult, DopplerResult,
    DoctorReview, Prescription, ModelOutput, VitalSign
)
from backend.app.schemas.patient import PatientSchema
from backend.app.schemas.pregnancy import PregnancySchema
from backend.app.schemas.fetal_assessment import FetalAssessmentSchema
from backend.app.schemas.prediction import PredictionSchema
from backend.app.schemas.growth_analysis import GrowthAnalysisSchema
from backend.app.schemas.newborn import NewbornSchema
from backend.app.schemas.nicu_admission import NicuAdmissionSchema
from backend.app.schemas.timeline import TimelineEntrySchema
from backend.app.schemas.maternal_profile import MaternalProfileSchema
from backend.app.schemas.ultrasound_record import UltrasoundRecordSchema
from backend.app.schemas.lab_result import LabResultSchema
from backend.app.schemas.doppler_result import DopplerResultSchema
from backend.app.schemas.doctor_review import DoctorReviewSchema
from backend.app.schemas.prescription import PrescriptionSchema
from backend.app.schemas.model_output import ModelOutputSchema
from backend.app.schemas.alert import AlertSchema
from backend.app.schemas.nicu_vital import NicuVitalSchema
from backend.app.schemas.vital_sign import VitalSignSchema
from backend.app.services.prenatal_service import analyze_prenatal_status

router = APIRouter()

@router.get('/stats/summary')
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_patients = db.query(Patient).count()
    active_pregnancies = db.query(Pregnancy).filter(Pregnancy.pregnancy_status == 'ACTIVE').count()
    nicu_admissions = db.query(NicuAdmission).count()
    active_alerts = db.query(Alert).count()
    return {
        "total_patients": total_patients,
        "active_pregnancies": active_pregnancies,
        "nicu_admissions": nicu_admissions,
        "active_alerts": active_alerts
    }

@router.get('/', response_model=List[PatientSchema])
def get_patients(db: Session = Depends(get_db)):
    patients = db.query(Patient).limit(100).all()
    return patients

@router.get('/{id}', response_model=PatientSchema)
def get_patient(id: str, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == id).first()
    if not patient:
        raise HTTPException(status_code=404, detail='Patient not found')
    return patient

@router.get('/{id}/timeline', response_model=List[TimelineEntrySchema])
def get_patient_timeline(id: str, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == id).first()
    if not patient:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    timeline = []
    
    # Gather clinical events
    events = db.query(ClinicalEvent).filter(ClinicalEvent.patient_id == id).all()
    for e in events:
        timeline.append({'date': e.event_date, 'type': 'clinical_event', 'details': e.details})
        
    # Gather alerts
    alerts = db.query(Alert).filter(Alert.patient_id == id).all()
    for a in alerts:
        timeline.append({'date': a.created_at, 'type': 'alert', 'details': f"{a.alert_type} ({a.severity})"})

    # Gather doctor reviews
    reviews = db.query(DoctorReview).filter(DoctorReview.patient_id == id).all()
    for r in reviews:
        timeline.append({'date': r.review_date, 'type': 'clinical_event', 'details': f"Review ({r.clinician_id}): {r.assessment} - {r.recommendations}"})

    # Gather prescriptions
    prescriptions = db.query(Prescription).filter(Prescription.patient_id == id).all()
    for p in prescriptions:
        timeline.append({'date': p.start_date, 'type': 'clinical_event', 'details': f"Rx: {p.medication_name} ({p.dosage})"})
    
    timeline.sort(key=lambda x: x['date'] if x['date'] else datetime.min, reverse=True)
    return timeline

@router.get('/{id}/pregnancy', response_model=List[PregnancySchema])
def get_pregnancy(id: str, db: Session = Depends(get_db)):
    pregnancies = db.query(Pregnancy).filter(Pregnancy.patient_id == id).all()
    return pregnancies

@router.get('/{id}/maternal-profile', response_model=List[MaternalProfileSchema])
def get_maternal_profile(id: str, db: Session = Depends(get_db)):
    pregnancies = db.query(Pregnancy).filter(Pregnancy.patient_id == id).all()
    profiles = []
    for preg in pregnancies:
        profiles.extend(preg.maternal_profiles)
    return profiles

@router.get('/{id}/fetal-assessments', response_model=List[FetalAssessmentSchema])
def get_fetal_assessments(id: str, db: Session = Depends(get_db)):
    pregnancies = db.query(Pregnancy).filter(Pregnancy.patient_id == id).all()
    assessments = []
    for preg in pregnancies:
        assessments.extend(preg.fetal_assessments)
    return assessments

@router.get('/{id}/ultrasounds', response_model=List[UltrasoundRecordSchema])
def get_ultrasounds(id: str, db: Session = Depends(get_db)):
    pregnancies = db.query(Pregnancy).filter(Pregnancy.patient_id == id).all()
    records = []
    for preg in pregnancies:
        records.extend(db.query(UltrasoundRecord).filter(UltrasoundRecord.pregnancy_id == preg.id).all())
    return records

@router.get('/{id}/labs', response_model=List[LabResultSchema])
def get_labs(id: str, db: Session = Depends(get_db)):
    pregnancies = db.query(Pregnancy).filter(Pregnancy.patient_id == id).all()
    records = []
    for preg in pregnancies:
        records.extend(db.query(LabResult).filter(LabResult.pregnancy_id == preg.id).all())
    return records

@router.get('/{id}/doppler', response_model=List[DopplerResultSchema])
def get_doppler(id: str, db: Session = Depends(get_db)):
    pregnancies = db.query(Pregnancy).filter(Pregnancy.patient_id == id).all()
    records = []
    for preg in pregnancies:
        records.extend(db.query(DopplerResult).filter(DopplerResult.pregnancy_id == preg.id).all())
    return records

@router.get('/{id}/predictions', response_model=List[PredictionSchema])
def get_predictions(id: str, db: Session = Depends(get_db)):
    predictions = db.query(Prediction).filter(Prediction.patient_id == id).all()
    return predictions

@router.get('/{id}/growth-analysis', response_model=List[GrowthAnalysisSchema])
def get_growth_analysis(id: str, db: Session = Depends(get_db)):
    pregnancies = db.query(Pregnancy).filter(Pregnancy.patient_id == id).all()
    growth = []
    for preg in pregnancies:
        growth.extend(preg.growth_analysis)
    return growth

@router.get('/{id}/doctor-reviews', response_model=List[DoctorReviewSchema])
def get_doctor_reviews(id: str, db: Session = Depends(get_db)):
    reviews = db.query(DoctorReview).filter(DoctorReview.patient_id == id).all()
    return reviews

@router.get('/{id}/prescriptions', response_model=List[PrescriptionSchema])
def get_prescriptions(id: str, db: Session = Depends(get_db)):
    prescriptions = db.query(Prescription).filter(Prescription.patient_id == id).all()
    return prescriptions

@router.get('/{id}/newborn', response_model=List[NewbornSchema])
def get_newborns(id: str, db: Session = Depends(get_db)):
    pregnancies = db.query(Pregnancy).filter(Pregnancy.patient_id == id).all()
    newborns = []
    for preg in pregnancies:
        newborns.extend(preg.newborns)
    return newborns

@router.get('/{id}/nicu', response_model=List[NicuAdmissionSchema])
def get_nicu_admissions(id: str, db: Session = Depends(get_db)):
    pregnancies = db.query(Pregnancy).filter(Pregnancy.patient_id == id).all()
    admissions = []
    for preg in pregnancies:
        for nb in preg.newborns:
            admissions.extend(nb.nicu_admissions)
    return admissions

@router.get('/{id}/alerts', response_model=List[AlertSchema])
def get_alerts(id: str, db: Session = Depends(get_db)):
    alerts = db.query(Alert).filter(Alert.patient_id == id).all()
    return alerts

@router.get('/{id}/model-outputs', response_model=List[ModelOutputSchema])
def get_model_outputs(id: str, db: Session = Depends(get_db)):
    outputs = db.query(ModelOutput).filter(ModelOutput.patient_id == id).all()
    return outputs

@router.get('/{id}/vitals', response_model=List[NicuVitalSchema])
def get_vitals(id: str, db: Session = Depends(get_db)):
    pregnancies = db.query(Pregnancy).filter(Pregnancy.patient_id == id).all()
    vitals = []
    for preg in pregnancies:
        for nb in preg.newborns:
            for adm in nb.nicu_admissions:
                vitals.extend(adm.nicu_vitals)
    vitals.sort(key=lambda x: x.timestamp if x.timestamp else datetime.min)
    return vitals

@router.get('/{id}/maternal-vitals', response_model=List[VitalSignSchema])
def get_maternal_vitals(id: str, db: Session = Depends(get_db)):
    records = db.query(VitalSign).filter(VitalSign.patient_id == id).order_by(VitalSign.timestamp.asc()).all()
    return records


@router.get('/{id}/prenatal-analysis')
def get_prenatal_analysis(
    id: str,
    pregnancy_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Run the Phase M prenatal analysis for a patient's pregnancy.

    Returns a full rule-based decision-support report including:
    - Growth variance (predicted vs actual EFW percentile)
    - Evaluation status (NORMAL_GROWTH_TRAJECTORY / CRITICAL_ADAPTIVE_DEVIATION_DETECTED)
    - Potential contributing pattern (4 patterns, rule-based)
    - Supporting evidence (Doppler, labs, maternal context)
    - Future outcome estimation (heuristic, not ML)
    - Monitoring considerations
    - Data gaps

    SAFETY: All outputs are SYNTHETIC / ACADEMIC simulation outputs.
    NOT a clinical diagnosis. Clinician review required.
    """
    patient = db.query(Patient).filter(Patient.id == id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Get target pregnancy (most recent if not specified)
    if pregnancy_id is not None:
        pregnancy = db.query(Pregnancy).filter(
            Pregnancy.id == pregnancy_id,
            Pregnancy.patient_id == id
        ).first()
        if not pregnancy:
            raise HTTPException(
                status_code=404,
                detail=f"Pregnancy {pregnancy_id} not found for patient {id}"
            )
    else:
        pregnancy = db.query(Pregnancy).filter(
            Pregnancy.patient_id == id
        ).order_by(Pregnancy.id.desc()).first()
        if not pregnancy:
            return {
                "patient_id": id,
                "status": "NO_PREGNANCY_FOUND",
                "message": "No pregnancy records found for this patient.",
                "safety_disclaimer": "SYNTHETIC / ACADEMIC simulation DATA — NOT FOR CLINICAL USE."
            }

    analysis = analyze_prenatal_status(db, pregnancy.id)
    analysis["patient_id"] = id
    return analysis


@router.get('/{id}/longitudinal-timeline')
def get_longitudinal_timeline(id: str, db: Session = Depends(get_db)):
    """
    Returns a complete chronological longitudinal timeline for the patient covering:
    Pregnancy → Maternal profile → T1 assessment → Prediction → T2 assessment →
    Growth analysis → Doctor reviews → Prescriptions → Birth → Newborn → NICU → NICU vitals → NICU ML predictions.
    """
    patient = db.query(Patient).filter(Patient.id == id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    timeline = []

    # Clinical events
    for e in db.query(ClinicalEvent).filter(ClinicalEvent.patient_id == id).all():
        timeline.append({"date": e.event_date, "type": "clinical_event", "category": "clinical",
                         "details": e.details, "event_type": e.event_type})

    # Alerts
    for a in db.query(Alert).filter(Alert.patient_id == id).all():
        timeline.append({"date": a.created_at, "type": "alert", "category": "clinical",
                         "details": f"{a.alert_type} ({a.severity})", "severity": a.severity})

    # Doctor reviews
    for r in db.query(DoctorReview).filter(DoctorReview.patient_id == id).all():
        timeline.append({"date": r.review_date, "type": "doctor_review", "category": "clinical",
                         "details": f"Review ({r.clinician_id}): {r.assessment}",
                         "clinician_id": r.clinician_id, "recommendations": r.recommendations})

    # Prescriptions
    for p in db.query(Prescription).filter(Prescription.patient_id == id).all():
        timeline.append({"date": p.start_date, "type": "prescription", "category": "clinical",
                         "details": f"Rx: {p.medication_name} ({p.dosage})",
                         "medication_name": p.medication_name, "dosage": p.dosage})

    # Pregnancies → Assessments → Predictions → Growth → Newborn → NICU
    for preg in db.query(Pregnancy).filter(Pregnancy.patient_id == id).all():
        timeline.append({"date": preg.pregnancy_start or preg.created_at,
                         "type": "pregnancy_start", "category": "prenatal",
                         "details": f"Pregnancy {preg.pregnancy_code} started (status: {preg.pregnancy_status})",
                         "pregnancy_id": preg.id, "status": preg.pregnancy_status})

        for fa in preg.fetal_assessments:
            timeline.append({"date": fa.assessment_date, "type": "fetal_assessment",
                              "category": "prenatal",
                              "details": f"Trimester {fa.trimester} assessment — EFW %ile: {fa.efw_percentile}, GA: {fa.gestational_age_weeks}w",
                              "trimester": fa.trimester, "efw_percentile": fa.efw_percentile,
                              "gestational_age_weeks": fa.gestational_age_weeks})

        for pred in preg.predictions:
            timeline.append({"date": pred.created_at, "type": "prediction",
                              "category": "prenatal",
                              "details": f"Prediction: {pred.target} = {pred.predicted_value} ({pred.risk_level})",
                              "target": pred.target, "predicted_value": pred.predicted_value,
                              "risk_level": pred.risk_level})

        for ga in preg.growth_analysis:
            timeline.append({"date": ga.generated_at, "type": "growth_analysis",
                              "category": "prenatal",
                              "details": f"Growth analysis: status={ga.evaluation_status}, variance={ga.growth_variance}pp",
                              "evaluation_status": ga.evaluation_status,
                              "growth_variance": ga.growth_variance})

        for nb in preg.newborns:
            timeline.append({"date": nb.birth_date or nb.created_at, "type": "birth",
                              "category": "neonatal",
                              "details": f"Birth: {nb.newborn_code} — {nb.birth_status}",
                              "newborn_code": nb.newborn_code, "birth_status": nb.birth_status,
                              "birth_weight": nb.birth_weight})

            for adm in nb.nicu_admissions:
                timeline.append({"date": adm.admission_date, "type": "nicu_admission",
                                  "category": "nicu",
                                  "details": f"NICU admission — status: {adm.status}",
                                  "nicu_admission_id": adm.id, "status": adm.status})
                if adm.discharge_date:
                    timeline.append({"date": adm.discharge_date, "type": "nicu_discharge",
                                      "category": "nicu",
                                      "details": f"NICU discharge — status: {adm.status}",
                                      "nicu_admission_id": adm.id})

    # Sort chronologically ascending
    timeline.sort(key=lambda x: x["date"] if x.get("date") else datetime.min)
    return {"patient_id": id, "total_events": len(timeline), "timeline": timeline}


@router.get('/{id}/explain')
def get_patient_shap_explanation(
    id: str,
    top_n: int = 5,
    db: Session = Depends(get_db)
):
    """
    Retrieves recent vital sign history for the specified patient,
    runs the XGBoost TreeSHAP explainer, and returns top feature contributions.

    Requires at least 60 recorded vital signs in MySQL.
    SAFETY: Model feature contribution explanation only.
    NOT a clinical diagnosis or treatment recommendation.
    """
    patient = db.query(Patient).filter(Patient.id == id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    vitals = (
        db.query(VitalSign)
        .filter(VitalSign.patient_id == id)
        .order_by(VitalSign.timestamp.asc())
        .all()
    )

    if len(vitals) < 60:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient sequence length for patient {id}. Found {len(vitals)} vitals, required 60."
        )

    from backend.app.schemas.predict_schema import VitalSignRecord
    from backend.app.services.inference_service import inference_service

    records = [
        VitalSignRecord(
            timestamp=v.timestamp.isoformat() if v.timestamp else datetime.utcnow().isoformat(),
            patient_id=v.patient_id,
            heart_rate=v.heart_rate or 0.0,
            spo2=v.spo2 or 0.0,
            respiratory_rate=v.respiratory_rate or 0.0,
            temperature=v.temperature or 0.0,
            systolic_bp=v.systolic_bp or 0.0,
            diastolic_bp=v.diastolic_bp or 0.0
        )
        for v in vitals[-60:]
    ]

    try:
        explanation = inference_service.explain_xgboost(records, top_n=top_n)
        return explanation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate SHAP explanation: {str(e)}")


@router.get('/{id}/anomaly-explain')
def get_patient_autoencoder_explanation(
    id: str,
    top_n: int = 5,
    db: Session = Depends(get_db)
):
    """
    Retrieves recent vital sign history for the specified patient,
    runs the Autoencoder anomaly explainer, and returns per-feature reconstruction errors.

    Requires at least 30 recorded vital signs in MySQL.
    SAFETY: Model feature contribution explanation only.
    NOT a clinical diagnosis or treatment recommendation.
    """
    patient = db.query(Patient).filter(Patient.id == id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    vitals = (
        db.query(VitalSign)
        .filter(VitalSign.patient_id == id)
        .order_by(VitalSign.timestamp.asc())
        .all()
    )

    if len(vitals) < 30:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient sequence length for patient {id}. Found {len(vitals)} vitals, required 30."
        )

    from backend.app.schemas.predict_schema import VitalSignRecord
    from backend.app.services.inference_service import inference_service

    records = [
        VitalSignRecord(
            timestamp=v.timestamp.isoformat() if v.timestamp else datetime.utcnow().isoformat(),
            patient_id=v.patient_id,
            heart_rate=v.heart_rate or 0.0,
            spo2=v.spo2 or 0.0,
            respiratory_rate=v.respiratory_rate or 0.0,
            temperature=v.temperature or 0.0,
            systolic_bp=v.systolic_bp or 0.0,
            diastolic_bp=v.diastolic_bp or 0.0
        )
        for v in vitals[-30:]
    ]

    try:
        explanation = inference_service.explain_autoencoder(records, top_n=top_n)
        return explanation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Autoencoder explanation: {str(e)}")


@router.get('/{id}/attention-explain')
def get_patient_transformer_attention(
    id: str,
    top_n: int = 5,
    db: Session = Depends(get_db)
):
    """
    Retrieves recent vital sign history for the specified patient,
    runs the Transformer attention explainer, and returns Multi-Head Self-Attention weights.

    Requires at least 30 recorded vital signs in MySQL.
    SAFETY: Model sequence attention distribution only.
    NOT a clinical diagnosis or treatment recommendation.
    """
    patient = db.query(Patient).filter(Patient.id == id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    vitals = (
        db.query(VitalSign)
        .filter(VitalSign.patient_id == id)
        .order_by(VitalSign.timestamp.asc())
        .all()
    )

    if len(vitals) < 30:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient sequence length for patient {id}. Found {len(vitals)} vitals, required 30."
        )

    from backend.app.schemas.predict_schema import VitalSignRecord
    from backend.app.services.inference_service import inference_service

    records = [
        VitalSignRecord(
            timestamp=v.timestamp.isoformat() if v.timestamp else datetime.utcnow().isoformat(),
            patient_id=v.patient_id,
            heart_rate=v.heart_rate or 0.0,
            spo2=v.spo2 or 0.0,
            respiratory_rate=v.respiratory_rate or 0.0,
            temperature=v.temperature or 0.0,
            systolic_bp=v.systolic_bp or 0.0,
            diastolic_bp=v.diastolic_bp or 0.0
        )
        for v in vitals[-30:]
    ]

    try:
        explanation = inference_service.explain_transformer(records, top_n=top_n)
        return explanation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Transformer attention explanation: {str(e)}")


@router.get('/{id}/forecast')
def get_patient_transformer_forecast(
    id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieves recent vital sign history for the specified patient and returns
    the multi-horizon forecasting audit status for the existing Transformer model.

    Requires at least 30 recorded vital signs in MySQL.
    SAFETY: Research output status only.
    NOT a clinical prediction or diagnosis.
    """
    patient = db.query(Patient).filter(Patient.id == id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    vitals = (
        db.query(VitalSign)
        .filter(VitalSign.patient_id == id)
        .order_by(VitalSign.timestamp.asc())
        .all()
    )

    if len(vitals) < 30:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient sequence length for patient {id}. Found {len(vitals)} vitals, required 30."
        )

    from backend.app.schemas.predict_schema import VitalSignRecord
    from backend.app.services.inference_service import inference_service

    records = [
        VitalSignRecord(
            timestamp=v.timestamp.isoformat() if v.timestamp else datetime.utcnow().isoformat(),
            patient_id=v.patient_id,
            heart_rate=v.heart_rate or 0.0,
            spo2=v.spo2 or 0.0,
            respiratory_rate=v.respiratory_rate or 0.0,
            temperature=v.temperature or 0.0,
            systolic_bp=v.systolic_bp or 0.0,
            diastolic_bp=v.diastolic_bp or 0.0
        )
        for v in vitals[-30:]
    ]

    try:
        forecast = inference_service.get_transformer_forecast(records)
        return forecast
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query Transformer forecast status: {str(e)}")



