"""
tests/test_prenatal_pipeline.py
--------------------------------
Phase M — Controlled Prenatal & Longitudinal Pregnancy Integration Tests

Comprehensive test suite verifying:
- Normal pregnancy trajectory
- Growth deviation >= 30 pp
- Actual EFW < 10th percentile
- All 4 potential contributing patterns (Placental, FGR vascular, Maternal risk, Constitutional/Idiopathic)
- Missing T1 prediction / Missing T2 actual handling
- Invalid percentile values
- Multi-patient isolation
- Longitudinal timeline ordering
- Pregnancy -> Newborn -> NICU linkage
- Safety disclaimers and non-clinical labeling
"""

import pytest
from datetime import datetime
from backend.app.services.prenatal_service import (
    analyze_prenatal_status,
    analyze_growth_variance,
    _validate_percentile,
    _route_contributing_pattern,
)
from backend.app.db.models import (
    Patient, Pregnancy, MaternalProfile, FetalAssessment,
    Prediction, GrowthAnalysis, Newborn, NicuAdmission,
    LabResult, DopplerResult
)
from tests.conftest import TestSessionLocal


@pytest.fixture(scope="class")
def db_session(request):
    session = TestSessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="class")
def populated_pregnancy(request, db_session):
    """
    Creates a dedicated test patient and complete pregnancy record
    with T1 (predicted) and T2 (actual) data for unit tests.
    """
    pid = "TEST-PRENATAL-P01"
    existing = db_session.query(Patient).filter(Patient.id == pid).first()
    if not existing:
        p = Patient(id=pid, name="Test Prenatal Patient")
        db_session.add(p)
        db_session.flush()

        preg = Pregnancy(
            id=9901,
            patient_id=pid,
            pregnancy_code="TEST-PREG-9901",
            pregnancy_status="active",
            conception_date=datetime(2026, 1, 1),
            pregnancy_start=datetime(2026, 1, 1),
        )
        db_session.add(preg)
        db_session.flush()

        mp = MaternalProfile(
            pregnancy_id=preg.id,
            maternal_age=29.0,
            bmi=23.5,
            map_value=84.0,
            chronic_hypertension=False,
            diabetes=False,
        )
        db_session.add(mp)

        # T1 Assessment
        fa1 = FetalAssessment(
            pregnancy_id=preg.id,
            trimester=1,
            gestational_age_weeks=12.0,
            efw_percentile=50.0,
            nt=1.3,
            crl=55.0,
            nasal_bone="present",
            assessment_date=datetime(2026, 3, 26),
        )
        db_session.add(fa1)

        # T1 Prediction: predicts T2 EFW percentile = 50.0
        pred = Prediction(
            patient_id=pid,
            pregnancy_id=preg.id,
            target="EFW_PERCENTILE_T2",
            predicted_value=50.0,
            risk_level="LOW",
            created_at=datetime(2026, 3, 26),
        )
        db_session.add(pred)

        # T2 Assessment: actual EFW percentile = 48.0 (delta = 2.0 pp -> Normal)
        fa2 = FetalAssessment(
            pregnancy_id=preg.id,
            trimester=2,
            gestational_age_weeks=20.0,
            efw_percentile=48.0,
            assessment_date=datetime(2026, 5, 21),
        )
        db_session.add(fa2)

        # Labs
        lab = LabResult(
            pregnancy_id=preg.id,
            papp_a=1.1,
            plgf=60.0,
            free_beta_hcg=1.0,
            status="normal",
        )
        db_session.add(lab)

        # Doppler
        dop = DopplerResult(
            pregnancy_id=preg.id,
            uterine_artery_pi=1.0,
            uterine_artery_status="normal",
            umbilical_artery_status="normal_flow",
        )
        db_session.add(dop)

        db_session.commit()

    return 9901


class TestPrenatalAnalysisService:
    """Test 1-7: Core growth variance calculation and pattern routing."""

    def test_normal_pregnancy_trajectory(self, db_session, populated_pregnancy):
        """TEST 1: Normal pregnancy produces NORMAL_GROWTH_TRAJECTORY."""
        result = analyze_prenatal_status(db_session, populated_pregnancy)
        assert result["evaluation_status"] == "NORMAL_GROWTH_TRAJECTORY"
        assert result["growth_variance"] == 2.0  # 50.0 - 48.0
        assert result["predicted_efw_percentile"] == 50.0
        assert result["actual_efw_percentile"] == 48.0
        assert "NO_CRITICAL_DEVIATION" in result["contributing_pattern"]["label"]
        assert "SYNTHETIC / ACADEMIC DEMO DATA" in result["safety_disclaimer"]

    def test_growth_deviation_ge_30_triggers_critical(self, db_session):
        """TEST 2: Growth deviation >= 30 pp triggers CRITICAL flag."""
        # Setup: predicted 60, actual 25 -> delta = 35 pp
        p_id = "TEST-DEV-30"
        p = db_session.query(Patient).filter(Patient.id == p_id).first()
        if not p:
            db_session.add(Patient(id=p_id, name="Delta Test Patient"))
            preg = Pregnancy(id=9902, patient_id=p_id, pregnancy_status="active")
            db_session.add(preg)
            db_session.add(Prediction(pregnancy_id=preg.id, target="EFW_PERCENTILE_T2", predicted_value=60.0, risk_level="LOW"))
            db_session.add(FetalAssessment(pregnancy_id=preg.id, trimester=2, efw_percentile=25.0, assessment_date=datetime(2026, 5, 1)))
            db_session.commit()

        result = analyze_prenatal_status(db_session, 9902)
        assert result["evaluation_status"] == "CRITICAL_ADAPTIVE_DEVIATION_DETECTED"
        assert result["growth_variance"] == 35.0
        assert result["clinician_review_required"] is True

    def test_actual_efw_below_10_triggers_critical(self, db_session):
        """TEST 3: Actual EFW percentile < 10 triggers CRITICAL flag even if delta < 30."""
        p_id = "TEST-EFW-LOW"
        p = db_session.query(Patient).filter(Patient.id == p_id).first()
        if not p:
            db_session.add(Patient(id=p_id, name="Low EFW Patient"))
            preg = Pregnancy(id=9903, patient_id=p_id, pregnancy_status="active")
            db_session.add(preg)
            # Predicted 20, Actual 8 -> delta = 12 pp (<30), but actual < 10
            db_session.add(Prediction(pregnancy_id=preg.id, target="EFW_PERCENTILE_T2", predicted_value=20.0, risk_level="WATCH"))
            db_session.add(FetalAssessment(pregnancy_id=preg.id, trimester=2, efw_percentile=8.0, assessment_date=datetime(2026, 5, 1)))
            db_session.commit()

        result = analyze_prenatal_status(db_session, 9903)
        assert result["evaluation_status"] == "CRITICAL_ADAPTIVE_DEVIATION_DETECTED"
        assert result["actual_efw_percentile"] == 8.0

    def test_placental_insufficiency_pattern_routing(self):
        """TEST 4: Low PlGF / high UtA Doppler routes to PLACENTAL_INSUFFICIENCY."""
        pattern = _route_contributing_pattern(
            actual_efw=20.0,
            delta=35.0,
            lab_data={"plgf": 22.0, "papp_a": 0.4},   # Low PlGF (<38) and low PAPP-A (<0.5)
            doppler_data={"uterine_artery_status": "high_resistance_bilateral_notches"},
            maternal_ctx={"map_value": 85.0, "chronic_hypertension": False}
        )
        assert pattern["label"] == "POTENTIAL_PLACENTAL_INSUFFICIENCY_PATTERN"
        assert pattern["requires_clinician_review"] is True
        assert len(pattern["supporting_evidence"]) >= 1

    def test_fgr_with_vascular_adaptation_pattern_routing(self):
        """TEST 5: Abnormal umbilical artery + actual EFW < 10 routes to FGR_WITH_VASCULAR_ADAPTATION."""
        pattern = _route_contributing_pattern(
            actual_efw=7.0,   # < 10
            delta=25.0,
            lab_data={"plgf": 50.0, "papp_a": 1.0},   # Normal labs
            doppler_data={"uterine_artery_status": "normal", "umbilical_artery_status": "reduced_end_diastolic_velocity"},
            maternal_ctx={"map_value": 85.0, "chronic_hypertension": False}
        )
        assert pattern["label"] == "POTENTIAL_FGR_WITH_VASCULAR_ADAPTATION_PATTERN"
        assert pattern["requires_clinician_review"] is True

    def test_maternal_vascular_risk_pattern_routing(self):
        """TEST 6: MAP >= 105 or chronic HTN routes to MATERNAL_VASCULAR_RISK."""
        pattern = _route_contributing_pattern(
            actual_efw=15.0,
            delta=32.0,
            lab_data={"plgf": 55.0, "papp_a": 1.0},
            doppler_data={"uterine_artery_status": "normal", "umbilical_artery_status": "normal_flow"},
            maternal_ctx={"map_value": 110.0, "chronic_hypertension": True}  # High MAP
        )
        assert pattern["label"] == "POTENTIAL_MATERNAL_VASCULAR_RISK_PATTERN"
        assert pattern["requires_clinician_review"] is True

    def test_constitutional_idiopathic_pattern_routing(self):
        """TEST 7: Growth deviation without specific vascular/lab markers routes to CONSTITUTIONAL/IDIOPATHIC."""
        pattern = _route_contributing_pattern(
            actual_efw=20.0,
            delta=35.0,
            lab_data={"plgf": 65.0, "papp_a": 1.2},   # Normal
            doppler_data={"uterine_artery_status": "normal", "umbilical_artery_status": "normal_flow"},  # Normal
            maternal_ctx={"map_value": 82.0, "chronic_hypertension": False}  # Normal
        )
        assert pattern["label"] == "POTENTIAL_CONSTITUTIONAL_SMALL_OR_IDIOPATHIC_PATTERN"
        assert pattern["requires_clinician_review"] is True


class TestMissingDataAndValidation:
    """Test 8-10: Missing data handling and percentile validation."""

    def test_missing_t1_prediction_handled_gracefully(self, db_session):
        """TEST 8: Missing T1 prediction sets INSUFFICIENT_DATA_FOR_ANALYSIS."""
        p_id = "TEST-NO-PRED"
        p = db_session.query(Patient).filter(Patient.id == p_id).first()
        if not p:
            db_session.add(Patient(id=p_id, name="No Pred Patient"))
            preg = Pregnancy(id=9904, patient_id=p_id, pregnancy_status="active")
            db_session.add(preg)
            db_session.add(FetalAssessment(pregnancy_id=preg.id, trimester=2, efw_percentile=45.0, assessment_date=datetime(2026, 5, 1)))
            db_session.commit()

        result = analyze_prenatal_status(db_session, 9904)
        assert result["evaluation_status"] == "INSUFFICIENT_DATA_FOR_ANALYSIS"
        assert result["growth_variance"] is None
        assert any("predicted" in g.lower() for g in result["data_gaps"])

    def test_missing_t2_actual_handled_gracefully(self, db_session):
        """TEST 9: Missing T2 actual assessment sets INSUFFICIENT_DATA_FOR_ANALYSIS."""
        p_id = "TEST-NO-ACTUAL"
        p = db_session.query(Patient).filter(Patient.id == p_id).first()
        if not p:
            db_session.add(Patient(id=p_id, name="No Actual Patient"))
            preg = Pregnancy(id=9905, patient_id=p_id, pregnancy_status="active")
            db_session.add(preg)
            db_session.add(Prediction(pregnancy_id=preg.id, target="EFW_PERCENTILE_T2", predicted_value=55.0, risk_level="LOW"))
            db_session.commit()

        result = analyze_prenatal_status(db_session, 9905)
        assert result["evaluation_status"] == "INSUFFICIENT_DATA_FOR_ANALYSIS"
        assert result["growth_variance"] is None
        assert any("trimester 2" in g.lower() for g in result["data_gaps"])

    def test_invalid_percentile_range_validation(self):
        """TEST 10: Out-of-bounds percentiles (< 0 or > 100) detected by validation."""
        assert _validate_percentile(-5.0, "EFW") is not None
        assert _validate_percentile(105.0, "EFW") is not None
        assert _validate_percentile(50.0, "EFW") is None
        assert _validate_percentile(None, "EFW") is None


class TestMultiPatientAndLinkage:
    """Test 11-14: Multi-patient isolation, timeline ordering, and newborn/NICU linkage."""

    @pytest.fixture(autouse=True)
    def setup_isolation_patients(self, db_session):
        # Patient A
        p_a = db_session.query(Patient).filter(Patient.id == "P-TEST-ISO-A").first()
        if not p_a:
            p_a = Patient(id="P-TEST-ISO-A", name="Patient Iso A")
            db_session.add(p_a)
            preg_a = Pregnancy(id=9910, patient_id="P-TEST-ISO-A", pregnancy_code="PREG-A", pregnancy_status="delivered")
            db_session.add(preg_a)
            db_session.add(Prediction(patient_id="P-TEST-ISO-A", pregnancy_id=9910, target="EFW_PERCENTILE_T2", predicted_value=50.0, risk_level="LOW", created_at=datetime(2026, 3, 1)))
            db_session.add(FetalAssessment(pregnancy_id=9910, trimester=1, efw_percentile=50.0, assessment_date=datetime(2026, 3, 1)))
            db_session.add(FetalAssessment(pregnancy_id=9910, trimester=2, efw_percentile=48.0, assessment_date=datetime(2026, 5, 1)))
            nb_a = Newborn(id=99100, pregnancy_id=9910, newborn_code="NB-ISO-A", birth_date=datetime(2026, 9, 1), birth_status="live_birth")
            db_session.add(nb_a)
            db_session.commit()

        # Patient B
        p_b = db_session.query(Patient).filter(Patient.id == "P-TEST-ISO-B").first()
        if not p_b:
            p_b = Patient(id="P-TEST-ISO-B", name="Patient Iso B")
            db_session.add(p_b)
            preg_b = Pregnancy(id=9920, patient_id="P-TEST-ISO-B", pregnancy_code="PREG-B", pregnancy_status="delivered")
            db_session.add(preg_b)
            db_session.add(Prediction(patient_id="P-TEST-ISO-B", pregnancy_id=9920, target="EFW_PERCENTILE_T2", predicted_value=55.0, risk_level="WATCH", created_at=datetime(2026, 3, 1)))
            db_session.add(FetalAssessment(pregnancy_id=9920, trimester=1, efw_percentile=55.0, assessment_date=datetime(2026, 3, 1)))
            db_session.add(FetalAssessment(pregnancy_id=9920, trimester=2, efw_percentile=20.0, assessment_date=datetime(2026, 5, 1)))
            nb_b = Newborn(id=99200, pregnancy_id=9920, newborn_code="NB-ISO-B", birth_date=datetime(2026, 9, 1), birth_status="preterm")
            db_session.add(nb_b)
            adm_b = NicuAdmission(id=992000, newborn_id=99200, admission_date=datetime(2026, 9, 1), status="admitted")
            db_session.add(adm_b)
            db_session.commit()

    def test_multi_patient_isolation(self, client):
        """TEST 11: Patient A and Patient B prenatal analyses remain strictly isolated."""
        resp_a = client.get("/api/v1/patients/P-TEST-ISO-A/prenatal-analysis")
        resp_b = client.get("/api/v1/patients/P-TEST-ISO-B/prenatal-analysis")

        assert resp_a.status_code == 200
        assert resp_b.status_code == 200

        data_a = resp_a.json()
        data_b = resp_b.json()

        assert data_a["patient_id"] == "P-TEST-ISO-A"
        assert data_b["patient_id"] == "P-TEST-ISO-B"
        assert data_a["pregnancy_id"] == 9910
        assert data_b["pregnancy_id"] == 9920
        assert data_a["growth_variance"] == 2.0
        assert data_b["growth_variance"] == 35.0

    def test_longitudinal_timeline_chronological_order(self, client):
        """TEST 12: Longitudinal timeline returned in strictly ascending chronological order."""
        resp = client.get("/api/v1/patients/P-TEST-ISO-A/longitudinal-timeline")
        assert resp.status_code == 200
        data = resp.json()
        assert "timeline" in data
        assert len(data["timeline"]) >= 3

        dates = [e["date"] for e in data["timeline"] if e.get("date")]
        parsed = [datetime.fromisoformat(d.replace("Z", "+00:00")) for d in dates]
        assert parsed == sorted(parsed), "Timeline events are not chronologically sorted!"

    def test_pregnancy_to_newborn_linkage(self, db_session):
        """TEST 13: Pregnancy -> Newborn linkage verified via foreign key."""
        nb = db_session.query(Newborn).filter(Newborn.pregnancy_id == 9910).first()
        assert nb is not None
        assert nb.newborn_code == "NB-ISO-A"
        assert nb.pregnancy.patient_id == "P-TEST-ISO-A"

    def test_pregnancy_to_nicu_linkage(self, db_session):
        """TEST 14: Pregnancy -> Newborn -> NICU Admission linkage verified."""
        nb = db_session.query(Newborn).filter(Newborn.pregnancy_id == 9920).first()
        assert nb is not None
        assert nb.newborn_code == "NB-ISO-B"
        assert len(nb.nicu_admissions) >= 1
        assert nb.nicu_admissions[0].id == 992000

    def test_legacy_growth_variance_compatibility(self, db_session, populated_pregnancy):
        """TEST 15: Legacy analyze_growth_variance wrapper persists record to DB correctly."""
        record = analyze_growth_variance(db_session, populated_pregnancy)
        assert record is not None
        assert record.pregnancy_id == populated_pregnancy
        assert record.growth_variance == pytest.approx(2.0, abs=0.1)
        assert record.evaluation_status == "NORMAL_GROWTH_TRAJECTORY"

