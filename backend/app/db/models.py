
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Patient(Base):
    __tablename__ = 'patients'

    id = Column(String(50), primary_key=True, index=True) # Also patient_id
    patient_code = Column(String(100), unique=True, index=True, nullable=True)
    name = Column(String(255), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    contact_info = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    pregnancies = relationship('Pregnancy', back_populates='patient', cascade='all, delete-orphan')
    model_outputs = relationship('ModelOutput', back_populates='patient')
    clinical_events = relationship('ClinicalEvent', back_populates='patient')
    doctor_reviews = relationship('DoctorReview', back_populates='patient')
    prescriptions = relationship('Prescription', back_populates='patient')
    alerts = relationship('Alert', back_populates='patient')
    chat_history = relationship('ChatHistory', back_populates='patient')
    
    # Old relations for compatibility if needed, though they might be migrated
    vitals = relationship('VitalSign', back_populates='patient', cascade='all, delete-orphan')
    predictions = relationship('Prediction', back_populates='patient', cascade='all, delete-orphan')


class Pregnancy(Base):
    __tablename__ = 'pregnancies'

    id = Column(Integer, primary_key=True, index=True) # pregnancy_id
    patient_id = Column(String(50), ForeignKey('patients.id'), index=True)
    pregnancy_code = Column(String(100), nullable=True)
    pregnancy_status = Column(String(50), nullable=True)
    conception_date = Column(DateTime, nullable=True)
    estimated_due_date = Column(DateTime, nullable=True)
    pregnancy_start = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    patient = relationship('Patient', back_populates='pregnancies')
    maternal_profiles = relationship('MaternalProfile', back_populates='pregnancy', cascade='all, delete-orphan')
    fetal_assessments = relationship('FetalAssessment', back_populates='pregnancy', cascade='all, delete-orphan')
    predictions = relationship('Prediction', back_populates='pregnancy')
    growth_analysis = relationship('GrowthAnalysis', back_populates='pregnancy')
    model_outputs = relationship('ModelOutput', back_populates='pregnancy')
    clinical_events = relationship('ClinicalEvent', back_populates='pregnancy')
    doctor_reviews = relationship('DoctorReview', back_populates='pregnancy')
    prescriptions = relationship('Prescription', back_populates='pregnancy')
    newborns = relationship('Newborn', back_populates='pregnancy')
    chat_history = relationship('ChatHistory', back_populates='pregnancy')


class MaternalProfile(Base):
    __tablename__ = 'maternal_profiles'

    id = Column(Integer, primary_key=True, index=True)
    pregnancy_id = Column(Integer, ForeignKey('pregnancies.id'), index=True)
    maternal_age = Column(Float, nullable=True)
    bmi = Column(Float, nullable=True)
    map_value = Column(Float, nullable=True) # MAP
    chronic_hypertension = Column(Boolean, default=False)
    diabetes = Column(Boolean, default=False)
    other_conditions = Column(Text, nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    pregnancy = relationship('Pregnancy', back_populates='maternal_profiles')


class FetalAssessment(Base):
    __tablename__ = 'fetal_assessments'

    id = Column(Integer, primary_key=True, index=True)
    pregnancy_id = Column(Integer, ForeignKey('pregnancies.id'), index=True)
    gestational_age_weeks = Column(Float, nullable=True)
    trimester = Column(Integer, nullable=True)
    crl = Column(Float, nullable=True)
    nt = Column(Float, nullable=True)
    nasal_bone = Column(String(50), nullable=True)
    efw = Column(Float, nullable=True)
    efw_percentile = Column(Float, nullable=True)
    growth_measurements = Column(Text, nullable=True)
    assessment_date = Column(DateTime, default=datetime.utcnow)
    source = Column(String(100), nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    pregnancy = relationship('Pregnancy', back_populates='fetal_assessments')
    ultrasound_records = relationship('UltrasoundRecord', back_populates='assessment')
    lab_results = relationship('LabResult', back_populates='assessment')
    doppler_results = relationship('DopplerResult', back_populates='assessment')
    predictions = relationship('Prediction', back_populates='assessment')


class UltrasoundRecord(Base):
    __tablename__ = 'ultrasound_records'

    id = Column(Integer, primary_key=True, index=True)
    pregnancy_id = Column(Integer, ForeignKey('pregnancies.id'), index=True)
    assessment_id = Column(Integer, ForeignKey('fetal_assessments.id'), nullable=True)
    ultrasound_date = Column(DateTime, default=datetime.utcnow)
    gestational_age = Column(Float, nullable=True)
    image_reference = Column(String(255), nullable=True)
    findings = Column(Text, nullable=True)
    source_dataset = Column(String(100), nullable=True)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    assessment = relationship('FetalAssessment', back_populates='ultrasound_records')


class LabResult(Base):
    __tablename__ = 'lab_results'

    id = Column(Integer, primary_key=True, index=True)
    pregnancy_id = Column(Integer, ForeignKey('pregnancies.id'), index=True)
    assessment_id = Column(Integer, ForeignKey('fetal_assessments.id'), nullable=True)
    papp_a = Column(Float, nullable=True)
    plgf = Column(Float, nullable=True)
    free_beta_hcg = Column(Float, nullable=True)
    test_date = Column(DateTime, default=datetime.utcnow)
    gestational_age = Column(Float, nullable=True)
    status = Column(String(50), nullable=True) # normal/low/high
    source = Column(String(100), nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    assessment = relationship('FetalAssessment', back_populates='lab_results')


class DopplerResult(Base):
    __tablename__ = 'doppler_results'

    id = Column(Integer, primary_key=True, index=True)
    pregnancy_id = Column(Integer, ForeignKey('pregnancies.id'), index=True)
    assessment_id = Column(Integer, ForeignKey('fetal_assessments.id'), nullable=True)
    gestational_age = Column(Float, nullable=True)
    uterine_artery_pi = Column(Float, nullable=True)
    uterine_artery_status = Column(String(50), nullable=True)
    umbilical_artery_status = Column(String(50), nullable=True)
    other_values = Column(Text, nullable=True)
    test_date = Column(DateTime, default=datetime.utcnow)
    source = Column(String(100), nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    assessment = relationship('FetalAssessment', back_populates='doppler_results')


class Prediction(Base):
    __tablename__ = 'predictions'

    id = Column(Integer, primary_key=True, index=True)
    # Support old patient_id and new pregnancy_id/assessment_id
    patient_id = Column(String(50), ForeignKey('patients.id'), nullable=True)
    pregnancy_id = Column(Integer, ForeignKey('pregnancies.id'), nullable=True, index=True)
    assessment_id = Column(Integer, ForeignKey('fetal_assessments.id'), nullable=True)
    
    prediction_type = Column(String(100), nullable=True)
    target = Column(String(100), nullable=True)
    predicted_value = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    model_name = Column(String(100), nullable=True)
    model_version = Column(String(50), nullable=True)
    prediction_horizon = Column(String(50), nullable=True)
    
    # Old fields for compatibility
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    risk_score = Column(Float, nullable=True)
    risk_level = Column(String(50), nullable=True)
    xgb_score = Column(Float, nullable=True)
    cnn_lstm_score = Column(Float, nullable=True)
    ae_score = Column(Float, nullable=True)
    transformer_score = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship('Patient', back_populates='predictions')
    pregnancy = relationship('Pregnancy', back_populates='predictions')
    assessment = relationship('FetalAssessment', back_populates='predictions')


class GrowthAnalysis(Base):
    __tablename__ = 'growth_analysis'

    id = Column(Integer, primary_key=True, index=True)
    pregnancy_id = Column(Integer, ForeignKey('pregnancies.id'), index=True)
    predicted_efw_percentile = Column(Float, nullable=True)
    actual_efw_percentile = Column(Float, nullable=True)
    growth_variance = Column(Float, nullable=True)
    evaluation_status = Column(String(100), nullable=True)
    contributing_patterns = Column(Text, nullable=True)
    model_version = Column(String(50), nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)

    pregnancy = relationship('Pregnancy', back_populates='growth_analysis')


class Newborn(Base):
    __tablename__ = 'newborns'

    id = Column(Integer, primary_key=True, index=True)
    pregnancy_id = Column(Integer, ForeignKey('pregnancies.id'), index=True)
    newborn_code = Column(String(100), nullable=True)
    name = Column(String(255), nullable=True)
    birth_date = Column(DateTime, nullable=True)
    gestational_age_at_birth = Column(Float, nullable=True)
    birth_weight = Column(Float, nullable=True)
    birth_length = Column(Float, nullable=True)
    birth_status = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    pregnancy = relationship('Pregnancy', back_populates='newborns')
    nicu_admissions = relationship('NicuAdmission', back_populates='newborn', cascade='all, delete-orphan')
    model_outputs = relationship('ModelOutput', back_populates='newborn')
    alerts = relationship('Alert', back_populates='newborn')
    chat_history = relationship('ChatHistory', back_populates='newborn')


class NicuAdmission(Base):
    __tablename__ = 'nicu_admissions'

    id = Column(Integer, primary_key=True, index=True)
    newborn_id = Column(Integer, ForeignKey('newborns.id'), index=True)
    admission_date = Column(DateTime, default=datetime.utcnow)
    discharge_date = Column(DateTime, nullable=True)
    admission_reason = Column(Text, nullable=True)
    status = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    newborn = relationship('Newborn', back_populates='nicu_admissions')
    nicu_vitals = relationship('NicuVital', back_populates='nicu_admission', cascade='all, delete-orphan')
    model_outputs = relationship('ModelOutput', back_populates='nicu_admission')
    alerts = relationship('Alert', back_populates='nicu_admission')


class NicuVital(Base):
    __tablename__ = 'nicu_vitals'

    id = Column(Integer, primary_key=True, index=True)
    nicu_admission_id = Column(Integer, ForeignKey('nicu_admissions.id'), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    heart_rate = Column(Float, nullable=True)
    spo2 = Column(Float, nullable=True)
    respiratory_rate = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    source = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    nicu_admission = relationship('NicuAdmission', back_populates='nicu_vitals')

# Preserve old VitalSign for backward compatibility
class VitalSign(Base):
    __tablename__ = 'vital_signs'

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), ForeignKey('patients.id'))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    heart_rate = Column(Float, nullable=True)
    spo2 = Column(Float, nullable=True)
    respiratory_rate = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    systolic_bp = Column(Float, nullable=True)
    diastolic_bp = Column(Float, nullable=True)

    patient = relationship('Patient', back_populates='vitals')


class ModelOutput(Base):
    __tablename__ = 'model_outputs'

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), ForeignKey('patients.id'), nullable=True)
    pregnancy_id = Column(Integer, ForeignKey('pregnancies.id'), nullable=True)
    newborn_id = Column(Integer, ForeignKey('newborns.id'), nullable=True)
    nicu_admission_id = Column(Integer, ForeignKey('nicu_admissions.id'), nullable=True)
    
    model_name = Column(String(100), nullable=True)
    model_version = Column(String(50), nullable=True)
    input_reference = Column(Text, nullable=True)
    output_type = Column(String(100), nullable=True)
    output_value = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    explanation_reference = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship('Patient', back_populates='model_outputs')
    pregnancy = relationship('Pregnancy', back_populates='model_outputs')
    newborn = relationship('Newborn', back_populates='model_outputs')
    nicu_admission = relationship('NicuAdmission', back_populates='model_outputs')


class ClinicalEvent(Base):
    __tablename__ = 'clinical_events'

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), ForeignKey('patients.id'), nullable=True)
    pregnancy_id = Column(Integer, ForeignKey('pregnancies.id'), nullable=True)
    event_type = Column(String(100), nullable=True)
    event_date = Column(DateTime, default=datetime.utcnow)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship('Patient', back_populates='clinical_events')
    pregnancy = relationship('Pregnancy', back_populates='clinical_events')


class DoctorReview(Base):
    __tablename__ = 'doctor_reviews'

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), ForeignKey('patients.id'), nullable=True)
    pregnancy_id = Column(Integer, ForeignKey('pregnancies.id'), nullable=True)
    clinician_id = Column(String(100), nullable=True)
    review_date = Column(DateTime, default=datetime.utcnow)
    findings = Column(Text, nullable=True)
    assessment = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship('Patient', back_populates='doctor_reviews')
    pregnancy = relationship('Pregnancy', back_populates='doctor_reviews')


class Prescription(Base):
    __tablename__ = 'prescriptions'

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), ForeignKey('patients.id'), nullable=True)
    pregnancy_id = Column(Integer, ForeignKey('pregnancies.id'), nullable=True)
    clinician_id = Column(String(100), nullable=True)
    medication_name = Column(String(255), nullable=True)
    dosage = Column(String(255), nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship('Patient', back_populates='prescriptions')
    pregnancy = relationship('Pregnancy', back_populates='prescriptions')


class Alert(Base):
    __tablename__ = 'alerts'

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), ForeignKey('patients.id'), nullable=True)
    newborn_id = Column(Integer, ForeignKey('newborns.id'), nullable=True)
    nicu_admission_id = Column(Integer, ForeignKey('nicu_admissions.id'), nullable=True)
    alert_type = Column(String(100), nullable=True)
    severity = Column(String(50), nullable=True)
    risk_score = Column(Float, nullable=True)
    triggering_factors = Column(Text, nullable=True)
    model_version = Column(String(50), nullable=True)
    status = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String(100), nullable=True)

    patient = relationship('Patient', back_populates='alerts')
    newborn = relationship('Newborn', back_populates='alerts')
    nicu_admission = relationship('NicuAdmission', back_populates='alerts')


class ChatHistory(Base):
    __tablename__ = 'chat_history'

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), ForeignKey('patients.id'), nullable=True)
    pregnancy_id = Column(Integer, ForeignKey('pregnancies.id'), nullable=True)
    newborn_id = Column(Integer, ForeignKey('newborns.id'), nullable=True)
    user_role = Column(String(50), nullable=True)
    question = Column(Text, nullable=True)
    response = Column(Text, nullable=True)
    model_used = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship('Patient', back_populates='chat_history')
    pregnancy = relationship('Pregnancy', back_populates='chat_history')
    newborn = relationship('Newborn', back_populates='chat_history')


class DatasetSource(Base):
    __tablename__ = 'dataset_sources'

    id = Column(Integer, primary_key=True, index=True)
    dataset_name = Column(String(255), nullable=True)
    source_url = Column(String(255), nullable=True)
    license = Column(String(100), nullable=True)
    data_type = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    imported_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)

    import_jobs = relationship('ImportJob', back_populates='dataset')


class ImportJob(Base):
    __tablename__ = 'import_jobs'

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey('dataset_sources.id'), nullable=True)
    file_name = Column(String(255), nullable=True)
    rows_detected = Column(Integer, default=0)
    rows_imported = Column(Integer, default=0)
    rows_rejected = Column(Integer, default=0)
    status = Column(String(50), nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    dataset = relationship('DatasetSource', back_populates='import_jobs')
    import_errors = relationship('ImportErrorLog', back_populates='job')


class ImportErrorLog(Base):
    __tablename__ = 'import_errors'

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey('import_jobs.id'), nullable=True)
    row_data = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship('ImportJob', back_populates='import_errors')

