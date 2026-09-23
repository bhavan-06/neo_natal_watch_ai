"""
tests/test_patient_endpoints.py
---------------------------------
Comprehensive tests for Phase A API Serialization.
Verifies all patient endpoints, response_model validation,
ORM serialization, nullable handling, and 404 handling.
"""

import pytest
from datetime import datetime
from backend.app.db.models import (
    Patient,
    Pregnancy,
    FetalAssessment,
    Prediction,
    GrowthAnalysis,
    Newborn,
    NicuAdmission,
    NicuVital,
    ClinicalEvent,
    Alert,
    MaternalProfile,
    DoctorReview,
    Prescription,
    ModelOutput,
    ChatHistory,
    UltrasoundRecord,
    LabResult,
    DopplerResult,
    VitalSign,
)
from backend.app.schemas import (
    PatientSchema,
    MaternalProfileSchema,
    PregnancySchema,
    FetalAssessmentSchema,
    PredictionSchema,
    GrowthAnalysisSchema,
    NewbornSchema,
    NicuAdmissionSchema,
    NicuVitalSchema,
    AlertSchema,
    ChatHistorySchema,
    ClinicalEventSchema,
    DoctorReviewSchema,
    PrescriptionSchema,
    ModelOutputSchema,
    UltrasoundRecordSchema,
    LabResultSchema,
    DopplerResultSchema,
    VitalSignSchema,
    TimelineEntrySchema,
)


@pytest.fixture(scope="class")
def sample_patient_id():
    """
    Populate a single complete patient hierarchy in the test database once
    for the test class.
    """
    from tests.conftest import TestSessionLocal
    db = TestSessionLocal()

    existing = db.query(Patient).filter(Patient.id == "P-PHASEA-001").first()
    if not existing:
        patient = Patient(
            id="P-PHASEA-001",
            patient_code="PC-PHASEA-001",
            name="Jane Doe",
            date_of_birth=datetime(1995, 5, 20),
            contact_info="+1234567890",
        )
        db.add(patient)

        pregnancy = Pregnancy(
            patient_id=patient.id,
            pregnancy_code="PREG-001",
            pregnancy_status="active",
            conception_date=datetime(2026, 1, 15),
            estimated_due_date=datetime(2026, 10, 22),
        )
        db.add(pregnancy)
        db.flush()

        fetal = FetalAssessment(
            pregnancy_id=pregnancy.id,
            gestational_age_weeks=34.5,
            trimester=3,
            crl=120.0,
            efw=2200.0,
            efw_percentile=45.0,
            assessment_date=datetime(2026, 9, 15),
        )
        db.add(fetal)

        pred = Prediction(
            patient_id=patient.id,
            pregnancy_id=pregnancy.id,
            prediction_type="fetal_growth_restriction",
            target="FGR",
            predicted_value=0.12,
            confidence=0.94,
            model_name="FGRNet",
            model_version="1.0.0",
            prediction_horizon="2_weeks",
            risk_score=0.12,
            risk_level="LOW",
            xgb_score=0.10,
            cnn_lstm_score=0.12,
            ae_score=0.11,
            transformer_score=0.13,
        )
        db.add(pred)

        growth = GrowthAnalysis(
            pregnancy_id=pregnancy.id,
            predicted_efw_percentile=44.0,
            actual_efw_percentile=45.0,
            growth_variance=1.0,
            evaluation_status="normal",
            contributing_patterns="steady_growth",
            model_version="1.0.0",
        )
        db.add(growth)

        newborn = Newborn(
            pregnancy_id=pregnancy.id,
            newborn_code="NB-001",
            birth_date=datetime(2026, 9, 20),
            gestational_age_at_birth=35.0,
            birth_weight=2300.0,
            birth_length=46.0,
            birth_status="live_birth",
        )
        db.add(newborn)
        db.flush()

        admission = NicuAdmission(
            newborn_id=newborn.id,
            admission_date=datetime(2026, 9, 20),
            admission_reason="Preterm observation",
            status="admitted",
        )
        db.add(admission)
        db.flush()

        event = ClinicalEvent(
            patient_id=patient.id,
            pregnancy_id=pregnancy.id,
            event_type="ultrasound_scan",
            event_date=datetime(2026, 9, 15),
            details="Routine 34w growth scan completed",
        )
        db.add(event)

        alert = Alert(
            patient_id=patient.id,
            newborn_id=newborn.id,
            alert_type="tachycardia_warning",
            severity="medium",
            risk_score=0.65,
            status="active",
        )
        db.add(alert)
        db.commit()

    db.close()
    return "P-PHASEA-001"


class TestPatientEndpointsSerialization:
    """Test all patient endpoints for correct response_model serialization."""

    def test_get_patients_list(self, client, sample_patient_id):
        response = client.get("/api/v1/patients/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        first = data[0]
        PatientSchema.model_validate(first)
        assert "id" in first
        assert "name" in first

    def test_get_patient_by_id(self, client, sample_patient_id):
        response = client.get(f"/api/v1/patients/{sample_patient_id}")
        assert response.status_code == 200
        data = response.json()
        validated = PatientSchema.model_validate(data)
        assert validated.id == sample_patient_id
        assert validated.name == "Jane Doe"

    def test_get_patient_not_found_returns_404(self, client):
        response = client.get("/api/v1/patients/NON-EXISTENT-ID-999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Patient not found"

    def test_get_patient_timeline(self, client, sample_patient_id):
        response = client.get(f"/api/v1/patients/{sample_patient_id}/timeline")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # Has clinical_event and alert
        for item in data:
            entry = TimelineEntrySchema.model_validate(item)
            assert entry.type in ["clinical_event", "alert"]

    def test_get_patient_pregnancy(self, client, sample_patient_id):
        response = client.get(f"/api/v1/patients/{sample_patient_id}/pregnancy")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        validated = PregnancySchema.model_validate(data[0])
        assert validated.patient_id == sample_patient_id
        assert validated.pregnancy_code == "PREG-001"

    def test_get_patient_fetal_assessments(self, client, sample_patient_id):
        response = client.get(f"/api/v1/patients/{sample_patient_id}/fetal-assessments")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        validated = FetalAssessmentSchema.model_validate(data[0])
        assert validated.efw == 2200.0

    def test_get_patient_predictions(self, client, sample_patient_id):
        response = client.get(f"/api/v1/patients/{sample_patient_id}/predictions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        validated = PredictionSchema.model_validate(data[0])
        assert validated.prediction_type == "fetal_growth_restriction"
        assert validated.risk_score == 0.12

    def test_get_patient_growth_analysis(self, client, sample_patient_id):
        response = client.get(f"/api/v1/patients/{sample_patient_id}/growth-analysis")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        validated = GrowthAnalysisSchema.model_validate(data[0])
        assert validated.actual_efw_percentile == 45.0

    def test_get_patient_newborn(self, client, sample_patient_id):
        response = client.get(f"/api/v1/patients/{sample_patient_id}/newborn")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        validated = NewbornSchema.model_validate(data[0])
        assert validated.newborn_code == "NB-001"
        assert validated.birth_weight == 2300.0

    def test_get_patient_nicu(self, client, sample_patient_id):
        response = client.get(f"/api/v1/patients/{sample_patient_id}/nicu")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        validated = NicuAdmissionSchema.model_validate(data[0])
        assert validated.admission_reason == "Preterm observation"
        assert validated.status == "admitted"


class TestAllDomainSchemasDirectValidation:
    """Test every newly created schema directly with model_validate."""

    def test_ultrasound_record_schema(self):
        obj = UltrasoundRecordSchema(
            id=1,
            pregnancy_id=1,
            assessment_id=2,
            ultrasound_date=datetime(2026, 9, 10),
            gestational_age=32.0,
            findings="Normal anatomy",
        )
        assert obj.id == 1
        assert obj.findings == "Normal anatomy"

    def test_lab_result_schema(self):
        obj = LabResultSchema(
            id=1,
            papp_a=1.2,
            plgf=85.0,
            status="normal",
        )
        assert obj.plgf == 85.0

    def test_doppler_result_schema(self):
        obj = DopplerResultSchema(
            id=1,
            uterine_artery_pi=1.1,
            uterine_artery_status="normal",
        )
        assert obj.uterine_artery_pi == 1.1

    def test_maternal_profile_schema(self):
        obj = MaternalProfileSchema(
            id=1,
            pregnancy_id=1,
            chronic_hypertension=False,
            diabetes=False,
        )
        assert obj.pregnancy_id == 1

    def test_doctor_review_schema(self):
        obj = DoctorReviewSchema(
            id=1,
            patient_id="P-001",
            clinician_id="DOC-01",
            assessment="Stable condition",
        )
        assert obj.clinician_id == "DOC-01"

    def test_prescription_schema(self):
        obj = PrescriptionSchema(
            id=1,
            patient_id="P-001",
            medication_name="Aspirin",
            dosage="75mg daily",
        )
        assert obj.medication_name == "Aspirin"

    def test_model_output_schema(self):
        obj = ModelOutputSchema(
            id=1,
            model_name="XGBoost",
            model_version="1.0.0",
            output_value=0.78,
            confidence=0.92,
        )
        assert obj.output_value == 0.78

    def test_alert_schema(self):
        obj = AlertSchema(
            id=1,
            patient_id="P-001",
            alert_type="hypoxia",
            severity="high",
            risk_score=0.91,
        )
        assert obj.severity == "high"

    def test_chat_history_schema(self):
        obj = ChatHistorySchema(
            id=1,
            patient_id="P-001",
            question="What is baby heart rate?",
            response="Heart rate is 142 bpm.",
            model_used="gemini",
        )
        assert obj.question == "What is baby heart rate?"

    def test_nicu_vital_schema(self):
        obj = NicuVitalSchema(
            id=1,
            heart_rate=145.0,
            spo2=98.0,
            temperature=37.1,
        )
        assert obj.heart_rate == 145.0

    def test_vital_sign_schema(self):
        obj = VitalSignSchema(
            id=1,
            patient_id="P-001",
            heart_rate=140.0,
            systolic_bp=65.0,
            diastolic_bp=42.0,
        )
        assert obj.systolic_bp == 65.0

