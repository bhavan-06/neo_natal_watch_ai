"""
tests/test_phase_q_e2e.py
--------------------------
Phase Q — Final End-to-End Integration & Validation Test Suite.

Validates the complete patient workflow from maternal pregnancy to NICU monitoring:
1. Patient retrieval
2. Pregnancy retrieval
3. Prenatal assessments & diagnostics
4. Prenatal decision-support analysis
5. Chronological longitudinal timeline
6. Doctor reviews & prescriptions
7. Newborn delivery linkage
8. NICU admission linkage
9. NICU telemetry vitals
10. ML Prediction inference
11. TreeSHAP feature contribution explainability
12. Autoencoder reconstruction anomaly explainability
13. Transformer Multi-Head Self-Attention explainability
14. Multi-horizon forecasting limitation audit
15. Clinical alert system & deduplication
16. Cross-patient isolation guarantees
17. MySQL persistence integrity
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from backend.app.schemas.predict_schema import VitalSignRecord
from backend.app.db.models import (
    Patient, Pregnancy, MaternalProfile, FetalAssessment,
    UltrasoundRecord, LabResult, DopplerResult, Prediction,
    GrowthAnalysis, DoctorReview, Prescription, Newborn,
    NicuAdmission, NicuVital, ClinicalEvent, Alert, VitalSign
)
from tests.conftest import TestSessionLocal, client


def create_60_vitals(patient_id: str = "P-SYN-002") -> list:
    now = datetime.utcnow()
    return [
        VitalSignRecord(
            timestamp=(now - timedelta(minutes=60 - i)).isoformat(),
            patient_id=patient_id,
            heart_rate=140.0 + (i * 0.1),
            spo2=96.0 - (i * 0.05),
            respiratory_rate=45.0,
            temperature=36.8,
            systolic_bp=70.0 + (i * 0.1),
            diastolic_bp=40.0
        )
        for i in range(60)
    ]


@pytest.fixture(scope="class", autouse=True)
def seed_phase_q_database():
    """Populates complete longitudinal records for Phase Q E2E validation in test DB."""
    db = TestSessionLocal()
    try:
        # Clean up any existing records for test isolation
        for old_pid in ["P-SYN-002", "P-SYN-001"]:
            db.query(Alert).filter(Alert.patient_id == old_pid).delete()
            db.query(ClinicalEvent).filter(ClinicalEvent.patient_id == old_pid).delete()
            db.query(DoctorReview).filter(DoctorReview.patient_id == old_pid).delete()
            db.query(Prescription).filter(Prescription.patient_id == old_pid).delete()
            existing_p = db.query(Patient).filter(Patient.id == old_pid).first()
            if existing_p:
                db.delete(existing_p)
        db.commit()

        # 1. Patient P-SYN-002 (Elena Rostova)
        p2 = Patient(
            id="P-SYN-002",
            patient_code="PT-SYN-002",
            name="Elena Rostova",
            date_of_birth=datetime(1993, 4, 12),
            contact_info="+1-555-0102"
        )
        db.add(p2)

        # 2. Patient P-SYN-001 (Maya Lin for isolation checks)
        p1 = Patient(
            id="P-SYN-001",
            patient_code="PT-SYN-001",
            name="Maya Lin",
            date_of_birth=datetime(1996, 8, 22),
            contact_info="+1-555-0101"
        )
        db.add(p1)
        db.flush()

        # Pregnancy for P-SYN-002
        preg2 = Pregnancy(
            id=2001,
            patient_id="P-SYN-002",
            pregnancy_code="PREG-SYN-002",
            pregnancy_status="admitted",
            conception_date=datetime(2025, 9, 1),
            estimated_due_date=datetime(2026, 6, 8),
            pregnancy_start=datetime(2025, 9, 1)
        )
        db.add(preg2)
        db.flush()

        # Maternal Profile
        mp2 = MaternalProfile(
            pregnancy_id=preg2.id,
            maternal_age=32.0,
            bmi=28.4,
            map_value=112.0,
            chronic_hypertension=True,
            diabetes=False,
            other_conditions="Early placental insufficiency suspected"
        )
        db.add(mp2)

        # Fetal Assessments: T1 and T2
        fa1 = FetalAssessment(
            id=20011,
            pregnancy_id=preg2.id,
            gestational_age_weeks=12.5,
            trimester=1,
            crl=60.0,
            efw=65.0,
            efw_percentile=55.0,
            assessment_date=datetime(2025, 11, 28)
        )
        db.add(fa1)

        fa2 = FetalAssessment(
            id=20012,
            pregnancy_id=preg2.id,
            gestational_age_weeks=24.0,
            trimester=2,
            efw=510.0,
            efw_percentile=6.0,
            assessment_date=datetime(2026, 2, 18)
        )
        db.add(fa2)
        db.flush()

        # T1 Prenatal Prediction
        pred1 = Prediction(
            id=200101,
            patient_id="P-SYN-002",
            pregnancy_id=preg2.id,
            assessment_id=fa1.id,
            prediction_type="fetal_growth_restriction",
            target="EFW_PERCENTILE_T2",
            predicted_value=48.0,
            confidence=0.88,
            model_name="PrenatalGrowthPredictor",
            model_version="1.0.0",
            risk_score=0.48,
            risk_level="MODERATE"
        )
        db.add(pred1)

        # Growth Analysis
        ga = GrowthAnalysis(
            id=2001,
            pregnancy_id=preg2.id,
            predicted_efw_percentile=48.0,
            actual_efw_percentile=6.0,
            growth_variance=-42.0,
            evaluation_status="CRITICAL_ADAPTIVE_DEVIATION_DETECTED",
            contributing_patterns="placental_insufficiency",
            model_version="1.0.0"
        )
        db.add(ga)

        # Ultrasound Record
        us = UltrasoundRecord(
            pregnancy_id=preg2.id,
            assessment_id=fa1.id,
            ultrasound_date=datetime(2025, 11, 28),
            gestational_age=12.5,
            findings="Normal nuchal translucency"
        )
        db.add(us)

        # Lab Result
        lab = LabResult(
            pregnancy_id=preg2.id,
            assessment_id=fa1.id,
            papp_a=0.32,
            plgf=24.0,
            gestational_age=12.5,
            test_date=datetime(2025, 11, 28)
        )
        db.add(lab)

        # Doppler Result
        dop = DopplerResult(
            pregnancy_id=preg2.id,
            assessment_id=fa2.id,
            gestational_age=24.0,
            uterine_artery_pi=1.85,
            uterine_artery_status="bilateral_notching",
            umbilical_artery_status="elevated_resistance",
            test_date=datetime(2026, 2, 18)
        )
        db.add(dop)

        # Doctor Review
        dr = DoctorReview(
            patient_id="P-SYN-002",
            pregnancy_id=preg2.id,
            clinician_id="DR-OBGYN-04",
            review_date=datetime(2026, 2, 19),
            assessment="Severe FGR with placental vascular resistance",
            recommendations="Initiate close fetal surveillance and prepare for early delivery"
        )
        db.add(dr)

        # Prescription
        rx = Prescription(
            patient_id="P-SYN-002",
            pregnancy_id=preg2.id,
            clinician_id="DR-OBGYN-04",
            medication_name="Labetalol",
            dosage="100mg BID",
            start_date=datetime(2026, 2, 19)
        )
        db.add(rx)

        # Newborn
        nb = Newborn(
            id=2001,
            pregnancy_id=preg2.id,
            newborn_code="NB-SYN-002",
            birth_date=datetime(2026, 3, 1),
            gestational_age_at_birth=25.5,
            birth_weight=680.0,
            birth_length=31.0,
            birth_status="live_birth"
        )
        db.add(nb)
        db.flush()

        # NICU Admission
        adm = NicuAdmission(
            id=2001,
            newborn_id=nb.id,
            admission_date=datetime(2026, 3, 1),
            admission_reason="Extreme prematurity, severe FGR",
            status="admitted"
        )
        db.add(adm)
        db.flush()

        # NICU Vitals
        nv = NicuVital(
            nicu_admission_id=adm.id,
            timestamp=datetime(2026, 3, 1, 12, 0),
            heart_rate=155.0,
            spo2=91.0,
            respiratory_rate=58.0,
            temperature=36.4
        )
        db.add(nv)

        # Clinical Event
        ce = ClinicalEvent(
            patient_id="P-SYN-002",
            pregnancy_id=preg2.id,
            event_type="emergency_cesarean",
            event_date=datetime(2026, 3, 1),
            details="Emergency C-section due to non-reassuring fetal status"
        )
        db.add(ce)

        # Alert
        al = Alert(
            patient_id="P-SYN-002",
            newborn_id=nb.id,
            nicu_admission_id=adm.id,
            alert_type="desaturation_warning",
            severity="high",
            risk_score=0.82,
            status="active"
        )
        db.add(al)

        db.commit()
    finally:
        db.close()


class TestPhaseQEndToEndWorkflow:
    """Comprehensive end-to-end integration test validating the entire healthcare journey."""

    def test_complete_patient_journey(self, client):
        """Validates all 17 stages of the maternal-fetal-neonatal pipeline."""
        pid = "P-SYN-002"  # Elena Rostova: Scenario B (Preeclampsia, NICU admission)

        # 1. Retrieve Patient
        resp_p = client.get(f"/api/v1/patients/{pid}")
        assert resp_p.status_code == 200
        p_data = resp_p.json()
        assert p_data["id"] == pid

        # 2. Retrieve Pregnancy
        resp_preg = client.get(f"/api/v1/patients/{pid}/pregnancy")
        assert resp_preg.status_code == 200
        pregs = resp_preg.json()
        assert len(pregs) >= 1
        preg_id = pregs[0]["id"]

        # 3. Retrieve Prenatal Data (Maternal Profile, Ultrasound, Labs, Doppler)
        resp_mp = client.get(f"/api/v1/patients/{pid}/maternal-profile")
        assert resp_mp.status_code == 200
        assert len(resp_mp.json()) >= 1

        resp_us = client.get(f"/api/v1/patients/{pid}/ultrasounds")
        assert resp_us.status_code == 200
        assert len(resp_us.json()) >= 1

        resp_lab = client.get(f"/api/v1/patients/{pid}/labs")
        assert resp_lab.status_code == 200
        assert len(resp_lab.json()) >= 1

        resp_dop = client.get(f"/api/v1/patients/{pid}/doppler")
        assert resp_dop.status_code == 200
        assert len(resp_dop.json()) >= 1

        # 4. Run Prenatal Analysis
        resp_pn = client.get(f"/api/v1/patients/{pid}/prenatal-analysis")
        assert resp_pn.status_code == 200
        pn_data = resp_pn.json()
        assert "evaluation_status" in pn_data
        assert "growth_variance" in pn_data
        assert "contributing_pattern" in pn_data
        assert pn_data["evaluation_status"] == "CRITICAL_ADAPTIVE_DEVIATION_DETECTED"

        # 5. Retrieve Longitudinal Timeline
        resp_tl = client.get(f"/api/v1/patients/{pid}/longitudinal-timeline")
        assert resp_tl.status_code == 200
        tl_data = resp_tl.json()
        assert "timeline" in tl_data
        assert len(tl_data["timeline"]) >= 1

        # 6. Retrieve Doctor Reviews & Prescriptions
        resp_dr = client.get(f"/api/v1/patients/{pid}/doctor-reviews")
        assert resp_dr.status_code == 200
        assert len(resp_dr.json()) >= 1

        resp_rx = client.get(f"/api/v1/patients/{pid}/prescriptions")
        assert resp_rx.status_code == 200
        assert len(resp_rx.json()) >= 1

        # 7. Newborn Linkage
        resp_nb = client.get(f"/api/v1/patients/{pid}/newborn")
        assert resp_nb.status_code == 200
        newborns = resp_nb.json()
        assert len(newborns) >= 1
        assert newborns[0]["pregnancy_id"] == preg_id

        # 8. NICU Admission Linkage
        resp_nicu = client.get(f"/api/v1/patients/{pid}/nicu")
        assert resp_nicu.status_code == 200
        nicu_adm = resp_nicu.json()
        assert len(nicu_adm) >= 1
        assert nicu_adm[0]["newborn_id"] == newborns[0]["id"]

        # 9. NICU Vitals
        resp_vit = client.get(f"/api/v1/patients/{pid}/vitals")
        assert resp_vit.status_code == 200
        assert len(resp_vit.json()) >= 1

        # 10. Real-time ML Prediction
        records = [r.model_dump() for r in create_60_vitals(patient_id=pid)]
        resp_pred = client.post("/api/v1/predict/", json={"records": records})
        assert resp_pred.status_code == 200
        pred_data = resp_pred.json()
        assert "risk_score" in pred_data
        assert "individual_models" in pred_data
        assert "xgboost" in pred_data["individual_models"]
        assert "autoencoder" in pred_data["individual_models"]
        assert "transformer" in pred_data["individual_models"]

        # 11. SHAP Explanation
        resp_shap = client.post("/api/v1/predict/explain", json={"records": records})
        assert resp_shap.status_code == 200
        shap_data = resp_shap.json()
        assert shap_data["model_name"] == "XGBoost"
        assert len(shap_data["top_features"]) == 5

        # 12. Autoencoder Reconstruction Explanation
        resp_ae = client.post("/api/v1/predict/anomaly-explain", json={"records": records})
        assert resp_ae.status_code == 200
        ae_data = resp_ae.json()
        assert ae_data["model_name"] == "Autoencoder"
        assert len(ae_data["top_contributing_vitals"]) == 5

        # 13. Transformer Attention Explanation
        resp_attn = client.post("/api/v1/predict/attention-explain", json={"records": records})
        assert resp_attn.status_code == 200
        attn_data = resp_attn.json()
        assert attn_data["model_name"] == "Transformer"
        assert "temporal_attention_sequence" in attn_data

        # 14. Forecast Limitation Audit
        resp_fc = client.post("/api/v1/predict/forecast", json={"records": records})
        assert resp_fc.status_code == 200
        fc_data = resp_fc.json()
        assert fc_data["forecasting_supported"] is False
        assert "Multi-horizon forecasting requires a forecasting-capable model" in fc_data["technical_limitation"]

        # 15. Verify Alerts
        resp_al = client.get(f"/api/v1/patients/{pid}/alerts")
        assert resp_al.status_code == 200
        assert len(resp_al.json()) >= 1

        # 16. Multi-Patient Isolation (Patient A vs Patient B)
        pid_b = "P-SYN-001"
        resp_pb = client.get(f"/api/v1/patients/{pid_b}")
        assert resp_pb.status_code == 200
        assert resp_pb.json()["id"] == pid_b
        assert resp_pb.json()["id"] != pid

        # 17. Database Persistence
        resp_preds_db = client.get(f"/api/v1/patients/{pid}/predictions")
        assert resp_preds_db.status_code == 200
        assert len(resp_preds_db.json()) >= 1

