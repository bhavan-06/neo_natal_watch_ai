"""
scripts/seed_additional_patients.py
-----------------------------------
Seeds additional comprehensive longitudinal patient records into the production
MySQL database `neonatal_watch_ai` without altering existing records:

1. P-SYN-007: Clara Vance (Age 29)
   - Twin Gestation / Selective Fetal Growth Restriction (sFGR)
   - Complete chain: Patient -> Pregnancy -> MaternalProfile -> FetalAssessments ->
     Ultrasounds -> Labs -> Dopplers -> Prediction -> GrowthAnalysis ->
     DoctorReview -> Prescription -> Newborn -> NicuAdmission -> NicuVitals ->
     ClinicalEvent -> Alert

2. P-SYN-008: Aisha Patel (Age 34)
   - Acute Placental Abruption, early emergency preterm delivery at 28w,
     active respiratory distress & telemetry in NICU.
"""

import os
import sys
from datetime import datetime, timedelta

# Ensure backend can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.db.database import SessionLocal
from backend.app.db.models import (
    Patient, Pregnancy, MaternalProfile, FetalAssessment,
    UltrasoundRecord, LabResult, DopplerResult, Prediction,
    GrowthAnalysis, DoctorReview, Prescription, Newborn,
    NicuAdmission, NicuVital, ClinicalEvent, Alert
)

def seed_patients():
    db = SessionLocal()
    print("=" * 60)
    print("SEEDING ADDITIONAL LONGITUDINAL PATIENT PROFILES")
    print("=" * 60)

    try:
        # ─────────────────────────────────────────────────────────────────
        # Patient 1: P-SYN-007 — Clara Vance
        # ─────────────────────────────────────────────────────────────────
        p7 = db.query(Patient).filter(Patient.id == "P-SYN-007").first()
        if not p7:
            print("Creating Patient P-SYN-007 (Clara Vance)...")
            p7 = Patient(
                id="P-SYN-007",
                patient_code="PT-SYN-007",
                name="Clara Vance",
                date_of_birth=datetime(1995, 3, 14),
                contact_info="+1-555-0107"
            )
            db.add(p7)
            db.flush()

            preg7 = Pregnancy(
                id=701,
                patient_id=p7.id,
                pregnancy_code="PREG-SYN-007",
                pregnancy_status="admitted",
                conception_date=datetime(2025, 8, 10),
                estimated_due_date=datetime(2026, 5, 17),
                pregnancy_start=datetime(2025, 8, 10)
            )
            db.add(preg7)
            db.flush()

            mp7 = MaternalProfile(
                pregnancy_id=preg7.id,
                maternal_age=29.0,
                bmi=26.2,
                map_value=96.0,
                chronic_hypertension=False,
                diabetes=False,
                other_conditions="Monochorionic diamniotic twin gestation, selective FGR Twin B"
            )
            db.add(mp7)

            fa7_t1 = FetalAssessment(
                id=7011,
                pregnancy_id=preg7.id,
                gestational_age_weeks=12.2,
                trimester=1,
                crl=58.0,
                nt=1.4,
                nasal_bone="present",
                efw=60.0,
                efw_percentile=52.0,
                assessment_date=datetime(2025, 11, 4),
                source="High-Resolution Ultrasound"
            )
            db.add(fa7_t1)

            fa7_t2 = FetalAssessment(
                id=7012,
                pregnancy_id=preg7.id,
                gestational_age_weeks=22.5,
                trimester=2,
                efw=460.0,
                efw_percentile=8.5,
                assessment_date=datetime(2026, 1, 15),
                source="Fetal Medicine Unit"
            )
            db.add(fa7_t2)
            db.flush()

            pred7 = Prediction(
                id=70101,
                patient_id=p7.id,
                pregnancy_id=preg7.id,
                assessment_id=fa7_t1.id,
                prediction_type="fetal_growth_restriction",
                target="EFW_PERCENTILE_T2",
                predicted_value=46.0,
                confidence=0.89,
                model_name="PrenatalGrowthPredictor",
                model_version="1.0.0",
                risk_score=0.46,
                risk_level="MODERATE"
            )
            db.add(pred7)

            ga7 = GrowthAnalysis(
                id=701,
                pregnancy_id=preg7.id,
                predicted_efw_percentile=46.0,
                actual_efw_percentile=8.5,
                growth_variance=-37.5,
                evaluation_status="CRITICAL_ADAPTIVE_DEVIATION_DETECTED",
                contributing_patterns="placental_insufficiency",
                model_version="1.0.0"
            )
            db.add(ga7)

            us7 = UltrasoundRecord(
                pregnancy_id=preg7.id,
                assessment_id=fa7_t1.id,
                ultrasound_date=datetime(2025, 11, 4),
                gestational_age=12.2,
                findings="Twin A EFW 50th %ile; Twin B EFW 8th %ile with unequal placental sharing",
                source_dataset="Clinical Fetal Imaging"
            )
            db.add(us7)

            lab7 = LabResult(
                pregnancy_id=preg7.id,
                assessment_id=fa7_t1.id,
                papp_a=0.41,
                plgf=28.5,
                gestational_age=12.2,
                test_date=datetime(2025, 11, 4)
            )
            db.add(lab7)

            dop7 = DopplerResult(
                pregnancy_id=preg7.id,
                assessment_id=fa7_t2.id,
                gestational_age=22.5,
                uterine_artery_pi=1.62,
                uterine_artery_status="unilateral_notch",
                umbilical_artery_status="intermittent_absent_end_diastolic",
                test_date=datetime(2026, 1, 15)
            )
            db.add(dop7)

            dr7 = DoctorReview(
                patient_id=p7.id,
                pregnancy_id=preg7.id,
                clinician_id="DR-MFM-02",
                review_date=datetime(2026, 1, 16),
                findings="Selective FGR in Twin B with intermittent absent umbilical artery diastolic flow",
                assessment="High risk of acute fetal deterioration in smaller twin",
                recommendations="Bi-weekly Doppler velocimetry, administer antenatal corticosteroids at 26w"
            )
            db.add(dr7)

            rx7 = Prescription(
                patient_id=p7.id,
                pregnancy_id=preg7.id,
                clinician_id="DR-MFM-02",
                medication_name="Betamethasone",
                dosage="12mg IM q24h x 2 doses",
                start_date=datetime(2026, 2, 10)
            )
            db.add(rx7)

            nb7 = Newborn(
                id=701,
                pregnancy_id=preg7.id,
                newborn_code="NB-SYN-007-B",
                birth_date=datetime(2026, 2, 22),
                gestational_age_at_birth=28.0,
                birth_weight=890.0,
                birth_length=34.0,
                birth_status="live_birth"
            )
            db.add(nb7)
            db.flush()

            adm7 = NicuAdmission(
                id=701,
                newborn_id=nb7.id,
                admission_date=datetime(2026, 2, 22),
                admission_reason="Severe sFGR, Twin B prematurity (28w), CPAP respiratory support",
                status="admitted"
            )
            db.add(adm7)
            db.flush()

            # Add recent 60 NICU vitals
            now = datetime.utcnow()
            for i in range(60):
                t = now - timedelta(minutes=60 - i)
                db.add(NicuVital(
                    nicu_admission_id=adm7.id,
                    timestamp=t,
                    heart_rate=148.0 + (i % 6) - 3,
                    spo2=94.0 + (i % 4) * 0.5,
                    respiratory_rate=52.0 + (i % 5),
                    temperature=36.7,
                    source="Drager Infinity Delta Telemetry"
                ))

            ce7 = ClinicalEvent(
                patient_id=p7.id,
                pregnancy_id=preg7.id,
                event_type="urgent_cesarean",
                event_date=datetime(2026, 2, 22),
                details="Delivered via urgent cesarean due to persistent absent end-diastolic velocity in Twin B"
            )
            db.add(ce7)

            al7 = Alert(
                patient_id=p7.id,
                newborn_id=nb7.id,
                nicu_admission_id=adm7.id,
                alert_type="tachycardia_surveillance",
                severity="medium",
                risk_score=0.58,
                status="active"
            )
            db.add(al7)
            print("  -> Clara Vance (P-SYN-007) seeded successfully.")
        else:
            print("  -> Clara Vance (P-SYN-007) already exists.")

        # ─────────────────────────────────────────────────────────────────
        # Patient 2: P-SYN-008 — Aisha Patel
        # ─────────────────────────────────────────────────────────────────
        p8 = db.query(Patient).filter(Patient.id == "P-SYN-008").first()
        if not p8:
            print("Creating Patient P-SYN-008 (Aisha Patel)...")
            p8 = Patient(
                id="P-SYN-008",
                patient_code="PT-SYN-008",
                name="Aisha Patel",
                date_of_birth=datetime(1991, 7, 25),
                contact_info="+1-555-0108"
            )
            db.add(p8)
            db.flush()

            preg8 = Pregnancy(
                id=801,
                patient_id=p8.id,
                pregnancy_code="PREG-SYN-008",
                pregnancy_status="admitted",
                conception_date=datetime(2025, 8, 15),
                estimated_due_date=datetime(2026, 5, 22),
                pregnancy_start=datetime(2025, 8, 15)
            )
            db.add(preg8)
            db.flush()

            mp8 = MaternalProfile(
                pregnancy_id=preg8.id,
                maternal_age=34.0,
                bmi=31.5,
                map_value=118.0,
                chronic_hypertension=True,
                diabetes=False,
                other_conditions="Sudden onset vaginal bleeding, placental abruption Grade II"
            )
            db.add(mp8)

            fa8_t1 = FetalAssessment(
                id=8011,
                pregnancy_id=preg8.id,
                gestational_age_weeks=11.8,
                trimester=1,
                crl=54.0,
                nt=1.2,
                nasal_bone="present",
                efw=58.0,
                efw_percentile=50.0,
                assessment_date=datetime(2025, 11, 6)
            )
            db.add(fa8_t1)

            fa8_t2 = FetalAssessment(
                id=8012,
                pregnancy_id=preg8.id,
                gestational_age_weeks=26.0,
                trimester=2,
                efw=690.0,
                efw_percentile=7.0,
                assessment_date=datetime(2026, 2, 14)
            )
            db.add(fa8_t2)
            db.flush()

            pred8 = Prediction(
                id=80101,
                patient_id=p8.id,
                pregnancy_id=preg8.id,
                assessment_id=fa8_t1.id,
                prediction_type="fetal_growth_restriction",
                target="EFW_PERCENTILE_T2",
                predicted_value=48.0,
                confidence=0.91,
                model_name="PrenatalGrowthPredictor",
                model_version="1.0.0",
                risk_score=0.52,
                risk_level="MODERATE"
            )
            db.add(pred8)

            ga8 = GrowthAnalysis(
                id=801,
                pregnancy_id=preg8.id,
                predicted_efw_percentile=48.0,
                actual_efw_percentile=7.0,
                growth_variance=-41.0,
                evaluation_status="CRITICAL_ADAPTIVE_DEVIATION_DETECTED",
                contributing_patterns="placental_insufficiency",
                model_version="1.0.0"
            )
            db.add(ga8)

            us8 = UltrasoundRecord(
                pregnancy_id=preg8.id,
                assessment_id=fa8_t2.id,
                ultrasound_date=datetime(2026, 2, 14),
                gestational_age=26.0,
                findings="Retroplacental hematoma (4.5 x 2.8 cm), reduced amniotic fluid volume",
                source_dataset="Emergency Obstetrical Scan"
            )
            db.add(us8)

            lab8 = LabResult(
                pregnancy_id=preg8.id,
                assessment_id=fa8_t1.id,
                papp_a=0.29,
                plgf=19.4,
                gestational_age=11.8,
                test_date=datetime(2025, 11, 6)
            )
            db.add(lab8)

            dop8 = DopplerResult(
                pregnancy_id=preg8.id,
                assessment_id=fa8_t2.id,
                gestational_age=26.0,
                uterine_artery_pi=1.95,
                uterine_artery_status="bilateral_notch",
                umbilical_artery_status="reverse_end_diastolic",
                test_date=datetime(2026, 2, 14)
            )
            db.add(dop8)

            dr8 = DoctorReview(
                patient_id=p8.id,
                pregnancy_id=preg8.id,
                clinician_id="DR-EMERG-09",
                review_date=datetime(2026, 2, 14),
                findings="Placental abruption with acute fetal bradycardia and reverse end-diastolic umbilical flow",
                assessment="Immediate threat to maternal and fetal life",
                recommendations="Crash cesarean section, prepare Level IV NICU resuscitation team"
            )
            db.add(dr8)

            rx8 = Prescription(
                patient_id=p8.id,
                pregnancy_id=preg8.id,
                clinician_id="DR-EMERG-09",
                medication_name="Magnesium Sulfate",
                dosage="4g IV loading dose, then 1g/hr neuroprotection",
                start_date=datetime(2026, 2, 14)
            )
            db.add(rx8)

            nb8 = Newborn(
                id=801,
                pregnancy_id=preg8.id,
                newborn_code="NB-SYN-008",
                birth_date=datetime(2026, 2, 14),
                gestational_age_at_birth=26.0,
                birth_weight=710.0,
                birth_length=32.0,
                birth_status="live_birth"
            )
            db.add(nb8)
            db.flush()

            adm8 = NicuAdmission(
                id=801,
                newborn_id=nb8.id,
                admission_date=datetime(2026, 2, 14),
                admission_reason="Extreme prematurity (26w), birth asphyxia post-abruption, HFOV ventilation",
                status="admitted"
            )
            db.add(adm8)
            db.flush()

            # Add recent 60 NICU vitals
            now = datetime.utcnow()
            for i in range(60):
                t = now - timedelta(minutes=60 - i)
                # Trend showing stabilization from critical bradycardia
                db.add(NicuVital(
                    nicu_admission_id=adm8.id,
                    timestamp=t,
                    heart_rate=158.0 + (i % 8) - 4,
                    spo2=91.0 + (i * 0.08) - (i % 3),
                    respiratory_rate=62.0 - (i * 0.1) + (i % 4),
                    temperature=36.4 + (i * 0.005),
                    source="GE Solar 8000i Telemetry"
                ))

            ce8 = ClinicalEvent(
                patient_id=p8.id,
                pregnancy_id=preg8.id,
                event_type="emergency_crash_cesarean",
                event_date=datetime(2026, 2, 14),
                details="Emergency crash C-section under general anesthesia due to acute placental abruption"
            )
            db.add(ce8)

            al8 = Alert(
                patient_id=p8.id,
                newborn_id=nb8.id,
                nicu_admission_id=adm8.id,
                alert_type="desaturation_apnea_alert",
                severity="high",
                risk_score=0.88,
                status="active"
            )
            db.add(al8)
            print("  -> Aisha Patel (P-SYN-008) seeded successfully.")
        else:
            print("  -> Aisha Patel (P-SYN-008) already exists.")

        db.commit()
        print("\nAll additional patients successfully populated in MySQL database!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding additional patients: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_patients()

