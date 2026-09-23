"""
scripts/generate_synthetic_data.py
----------------------------------
Generates a realistic, longitudinal, academic synthetic demonstration dataset.
Adheres strictly to the existing schema definitions in models.py and MySQL.
Outputs 17 clean CSV files under data/synthetic/.
"""

import os
import csv
from datetime import datetime, timedelta

SYNTHETIC_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "synthetic")
os.makedirs(SYNTHETIC_DIR, exist_ok=True)

ACADEMIC_TAG = "SYNTHETIC_DEMO"


def generate_all():
    print(f"Generating synthetic CSV files in {SYNTHETIC_DIR}...")

    # -------------------------------------------------------------
    # 1. PATIENTS (patients.csv)
    # columns: id, patient_code, name, date_of_birth, contact_info, created_at, updated_at
    # -------------------------------------------------------------
    patients = [
        {
            "id": "P-SYN-001",
            "patient_code": "SYN-PAT-001",
            "name": "Sarah Miller (Demo)",
            "date_of_birth": "1997-04-12 00:00:00",
            "contact_info": "demo-contact-001@synthetic.local",
            "created_at": "2025-09-01 09:00:00",
            "updated_at": "2026-07-15 10:00:00",
        },
        {
            "id": "P-SYN-002",
            "patient_code": "SYN-PAT-002",
            "name": "Elena Rostova (Demo)",
            "date_of_birth": "1993-08-23 00:00:00",
            "contact_info": "demo-contact-002@synthetic.local",
            "created_at": "2025-08-15 08:30:00",
            "updated_at": "2026-06-30 11:00:00",
        },
        {
            "id": "P-SYN-003",
            "patient_code": "SYN-PAT-003",
            "name": "Amina Patel (Demo)",
            "date_of_birth": "1991-11-05 00:00:00",
            "contact_info": "demo-contact-003@synthetic.local",
            "created_at": "2025-07-20 14:00:00",
            "updated_at": "2026-06-05 09:15:00",
        },
        {
            "id": "P-SYN-004",
            "patient_code": "SYN-PAT-004",
            "name": "Maria Garcia (Demo)",
            "date_of_birth": "1988-02-17 00:00:00",
            "contact_info": "demo-contact-004@synthetic.local",
            "created_at": "2025-10-01 10:45:00",
            "updated_at": "2026-08-15 16:30:00",
        },
        {
            "id": "P-SYN-005",
            "patient_code": "SYN-PAT-005",
            "name": "Chloe Dupont (Demo)",
            "date_of_birth": "1996-06-30 00:00:00",
            "contact_info": "demo-contact-005@synthetic.local",
            "created_at": "2025-06-15 11:00:00",
            "updated_at": "2026-04-30 14:20:00",
        },
        {
            "id": "P-SYN-006",
            "patient_code": "SYN-PAT-006",
            "name": "Grace Tan (Demo)",
            "date_of_birth": "1995-10-14 00:00:00",
            "contact_info": "demo-contact-006@synthetic.local",
            "created_at": "2026-04-15 09:30:00",
            "updated_at": "2026-09-20 10:00:00",
        },
    ]

    # -------------------------------------------------------------
    # 2. PREGNANCIES (pregnancies.csv)
    # columns: id, patient_id, pregnancy_code, pregnancy_status, conception_date, estimated_due_date, pregnancy_start, created_at, updated_at
    # -------------------------------------------------------------
    pregnancies = [
        {
            "id": 101,
            "patient_id": "P-SYN-001",
            "pregnancy_code": "SYN-PREG-101",
            "pregnancy_status": "delivered",
            "conception_date": "2025-10-01 00:00:00",
            "estimated_due_date": "2026-07-08 00:00:00",
            "pregnancy_start": "2025-09-17 00:00:00",
            "created_at": "2025-10-05 09:00:00",
            "updated_at": "2026-07-10 12:00:00",
        },
        {
            "id": 102,
            "patient_id": "P-SYN-002",
            "pregnancy_code": "SYN-PREG-102",
            "pregnancy_status": "delivered",
            "conception_date": "2025-09-15 00:00:00",
            "estimated_due_date": "2026-06-22 00:00:00",
            "pregnancy_start": "2025-09-01 00:00:00",
            "created_at": "2025-09-20 08:30:00",
            "updated_at": "2026-06-25 15:00:00",
        },
        {
            "id": 103,
            "patient_id": "P-SYN-003",
            "pregnancy_code": "SYN-PREG-103",
            "pregnancy_status": "delivered",
            "conception_date": "2025-08-20 00:00:00",
            "estimated_due_date": "2026-05-27 00:00:00",
            "pregnancy_start": "2025-08-06 00:00:00",
            "created_at": "2025-08-25 14:00:00",
            "updated_at": "2026-05-30 11:30:00",
        },
        {
            "id": 104,
            "patient_id": "P-SYN-004",
            "pregnancy_code": "SYN-PREG-104",
            "pregnancy_status": "delivered",
            "conception_date": "2025-11-01 00:00:00",
            "estimated_due_date": "2026-08-08 00:00:00",
            "pregnancy_start": "2025-10-18 00:00:00",
            "created_at": "2025-11-05 10:45:00",
            "updated_at": "2026-08-10 14:00:00",
        },
        {
            "id": 105,
            "patient_id": "P-SYN-005",
            "pregnancy_code": "SYN-PREG-105",
            "pregnancy_status": "delivered",
            "conception_date": "2025-07-10 00:00:00",
            "estimated_due_date": "2026-04-16 00:00:00",
            "pregnancy_start": "2025-06-26 00:00:00",
            "created_at": "2025-07-15 11:00:00",
            "updated_at": "2026-04-20 18:00:00",
        },
        {
            "id": 106,
            "patient_id": "P-SYN-006",
            "pregnancy_code": "SYN-PREG-106",
            "pregnancy_status": "active",
            "conception_date": "2026-05-01 00:00:00",
            "estimated_due_date": "2027-02-05 00:00:00",
            "pregnancy_start": "2026-04-17 00:00:00",
            "created_at": "2026-05-10 09:30:00",
            "updated_at": "2026-09-20 10:00:00",
        },
    ]

    # -------------------------------------------------------------
    # 3. MATERNAL PROFILES (maternal_profiles.csv)
    # columns: id, pregnancy_id, maternal_age, bmi, map_value, chronic_hypertension, diabetes, other_conditions, recorded_at
    # -------------------------------------------------------------
    maternal_profiles = [
        {
            "id": 201,
            "pregnancy_id": 101,
            "maternal_age": 28.0,
            "bmi": 22.4,
            "map_value": 82.0,
            "chronic_hypertension": 0,
            "diabetes": 0,
            "other_conditions": "None (Low-risk primigravida)",
            "recorded_at": "2025-10-15 10:00:00",
        },
        {
            "id": 202,
            "pregnancy_id": 102,
            "maternal_age": 32.0,
            "bmi": 24.1,
            "map_value": 88.0,
            "chronic_hypertension": 0,
            "diabetes": 0,
            "other_conditions": "Mild asthma in childhood",
            "recorded_at": "2025-10-02 09:30:00",
        },
        {
            "id": 203,
            "pregnancy_id": 103,
            "maternal_age": 34.0,
            "bmi": 26.8,
            "map_value": 96.0,
            "chronic_hypertension": 0,
            "diabetes": 0,
            "other_conditions": "Elevated baseline vascular resistance",
            "recorded_at": "2025-09-10 14:15:00",
        },
        {
            "id": 204,
            "pregnancy_id": 104,
            "maternal_age": 37.0,
            "bmi": 31.5,
            "map_value": 108.0,
            "chronic_hypertension": 1,
            "diabetes": 1,
            "other_conditions": "Essential chronic hypertension and Pre-gestational Type 2 Diabetes",
            "recorded_at": "2025-11-15 11:00:00",
        },
        {
            "id": 205,
            "pregnancy_id": 105,
            "maternal_age": 29.0,
            "bmi": 23.0,
            "map_value": 85.0,
            "chronic_hypertension": 0,
            "diabetes": 0,
            "other_conditions": "Prior elective cerclage",
            "recorded_at": "2025-07-28 11:30:00",
        },
        {
            "id": 206,
            "pregnancy_id": 106,
            "maternal_age": 30.0,
            "bmi": 21.8,
            "map_value": 84.0,
            "chronic_hypertension": 0,
            "diabetes": 0,
            "other_conditions": "None (Active cohort)",
            "recorded_at": "2026-05-20 10:00:00",
        },
    ]

    # -------------------------------------------------------------
    # 4. FETAL ASSESSMENTS (fetal_assessments.csv)
    # columns: id, pregnancy_id, gestational_age_weeks, trimester, crl, nt, nasal_bone, efw, efw_percentile, growth_measurements, assessment_date, source, recorded_at
    # -------------------------------------------------------------
    fetal_assessments = [
        # Patient 1: P-SYN-001 (Pregnancy 101)
        {
            "id": 301,
            "pregnancy_id": 101,
            "gestational_age_weeks": 12.2,
            "trimester": 1,
            "crl": 58.2,
            "nt": 1.4,
            "nasal_bone": "present",
            "efw": 62.0,
            "efw_percentile": 52.0,
            "growth_measurements": '{"bpd": 21.0, "hc": 78.0, "ac": 65.0, "fl": 9.5}',
            "assessment_date": "2025-12-10 10:30:00",
            "source": ACADEMIC_TAG,
            "recorded_at": "2025-12-10 11:00:00",
        },
        {
            "id": 302,
            "pregnancy_id": 101,
            "gestational_age_weeks": 20.5,
            "trimester": 2,
            "crl": None,
            "nt": None,
            "nasal_bone": "present",
            "efw": 365.0,
            "efw_percentile": 50.0,
            "growth_measurements": '{"bpd": 49.0, "hc": 182.0, "ac": 160.0, "fl": 34.0}',
            "assessment_date": "2026-02-06 14:00:00",
            "source": ACADEMIC_TAG,
            "recorded_at": "2026-02-06 14:30:00",
        },

        # Patient 2: P-SYN-002 (Pregnancy 102 - Growth Deviation)
        {
            "id": 303,
            "pregnancy_id": 102,
            "gestational_age_weeks": 12.0,
            "trimester": 1,
            "crl": 55.0,
            "nt": 1.6,
            "nasal_bone": "present",
            "efw": 58.0,
            "efw_percentile": 48.0,
            "growth_measurements": '{"bpd": 20.0, "hc": 75.0, "ac": 62.0, "fl": 9.0}',
            "assessment_date": "2025-11-24 09:30:00",
            "source": ACADEMIC_TAG,
            "recorded_at": "2025-11-24 10:00:00",
        },
        {
            "id": 304,
            "pregnancy_id": 102,
            "gestational_age_weeks": 22.0,
            "trimester": 2,
            "crl": None,
            "nt": None,
            "nasal_bone": "present",
            "efw": 410.0,
            "efw_percentile": 22.0,
            "growth_measurements": '{"bpd": 51.0, "hc": 188.0, "ac": 158.0, "fl": 35.0}',
            "assessment_date": "2026-02-02 11:00:00",
            "source": ACADEMIC_TAG,
            "recorded_at": "2026-02-02 11:30:00",
        },

        # Patient 3: P-SYN-003 (Pregnancy 103 - Vascular / Doppler Deviation)
        {
            "id": 305,
            "pregnancy_id": 103,
            "gestational_age_weeks": 12.4,
            "trimester": 1,
            "crl": 57.0,
            "nt": 1.8,
            "nasal_bone": "present",
            "efw": 56.0,
            "efw_percentile": 30.0,
            "growth_measurements": '{"bpd": 20.5, "hc": 76.0, "ac": 60.0, "fl": 9.0}',
            "assessment_date": "2025-11-01 15:00:00",
            "source": ACADEMIC_TAG,
            "recorded_at": "2025-11-01 15:30:00",
        },
        {
            "id": 306,
            "pregnancy_id": 103,
            "gestational_age_weeks": 21.0,
            "trimester": 2,
            "crl": None,
            "nt": None,
            "nasal_bone": "present",
            "efw": 340.0,
            "efw_percentile": 14.0,
            "growth_measurements": '{"bpd": 48.0, "hc": 178.0, "ac": 150.0, "fl": 33.0}',
            "assessment_date": "2026-01-05 10:30:00",
            "source": ACADEMIC_TAG,
            "recorded_at": "2026-01-05 11:00:00",
        },

        # Patient 4: P-SYN-004 (Pregnancy 104 - Maternal Risk Pattern)
        {
            "id": 307,
            "pregnancy_id": 104,
            "gestational_age_weeks": 11.8,
            "trimester": 1,
            "crl": 52.0,
            "nt": 2.1,
            "nasal_bone": "present",
            "efw": 52.0,
            "efw_percentile": 35.0,
            "growth_measurements": '{"bpd": 19.5, "hc": 73.0, "ac": 58.0, "fl": 8.5}',
            "assessment_date": "2026-01-10 11:15:00",
            "source": ACADEMIC_TAG,
            "recorded_at": "2026-01-10 11:45:00",
        },
        {
            "id": 308,
            "pregnancy_id": 104,
            "gestational_age_weeks": 20.0,
            "trimester": 2,
            "crl": None,
            "nt": None,
            "nasal_bone": "present",
            "efw": 320.0,
            "efw_percentile": 28.0,
            "growth_measurements": '{"bpd": 47.0, "hc": 175.0, "ac": 152.0, "fl": 32.0}',
            "assessment_date": "2026-03-10 14:00:00",
            "source": ACADEMIC_TAG,
            "recorded_at": "2026-03-10 14:30:00",
        },

        # Patient 5: P-SYN-005 (Pregnancy 105 - Preterm & NICU)
        {
            "id": 309,
            "pregnancy_id": 105,
            "gestational_age_weeks": 12.1,
            "trimester": 1,
            "crl": 57.5,
            "nt": 1.3,
            "nasal_bone": "present",
            "efw": 60.0,
            "efw_percentile": 50.0,
            "growth_measurements": '{"bpd": 20.8, "hc": 77.0, "ac": 64.0, "fl": 9.2}',
            "assessment_date": "2025-09-18 10:00:00",
            "source": ACADEMIC_TAG,
            "recorded_at": "2025-09-18 10:30:00",
        },
        {
            "id": 310,
            "pregnancy_id": 105,
            "gestational_age_weeks": 22.0,
            "trimester": 2,
            "crl": None,
            "nt": None,
            "nasal_bone": "present",
            "efw": 475.0,
            "efw_percentile": 48.0,
            "growth_measurements": '{"bpd": 53.0, "hc": 195.0, "ac": 172.0, "fl": 38.0}',
            "assessment_date": "2025-11-26 13:45:00",
            "source": ACADEMIC_TAG,
            "recorded_at": "2025-11-26 14:15:00",
        },

        # Patient 6: P-SYN-006 (Pregnancy 106 - Active Pregnancy)
        {
            "id": 311,
            "pregnancy_id": 106,
            "gestational_age_weeks": 12.3,
            "trimester": 1,
            "crl": 59.0,
            "nt": 1.3,
            "nasal_bone": "present",
            "efw": 63.0,
            "efw_percentile": 55.0,
            "growth_measurements": '{"bpd": 21.2, "hc": 79.0, "ac": 66.0, "fl": 9.6}',
            "assessment_date": "2026-07-10 09:30:00",
            "source": ACADEMIC_TAG,
            "recorded_at": "2026-07-10 10:00:00",
        },
        {
            "id": 312,
            "pregnancy_id": 106,
            "gestational_age_weeks": 20.2,
            "trimester": 2,
            "crl": None,
            "nt": None,
            "nasal_bone": "present",
            "efw": 355.0,
            "efw_percentile": 54.0,
            "growth_measurements": '{"bpd": 48.5, "hc": 180.0, "ac": 158.0, "fl": 33.5}',
            "assessment_date": "2026-09-04 11:00:00",
            "source": ACADEMIC_TAG,
            "recorded_at": "2026-09-04 11:30:00",
        },
    ]

    # -------------------------------------------------------------
    # 5. ULTRASOUND RECORDS (ultrasound_records.csv)
    # columns: id, pregnancy_id, assessment_id, ultrasound_date, gestational_age, image_reference, findings, source_dataset, metadata_json, created_at
    # -------------------------------------------------------------
    ultrasound_records = [
        {
            "id": 401,
            "pregnancy_id": 101,
            "assessment_id": 301,
            "ultrasound_date": "2025-12-10 10:30:00",
            "gestational_age": 12.2,
            "image_reference": "syn_us_101_t1.dcm",
            "findings": "Normal 1st trimester nuchal scan. Nasal bone visible. Anatomical survey normal for gestational age.",
            "source_dataset": ACADEMIC_TAG,
            "metadata_json": '{"transducer": "3.5MHz_convex", "quality": "optimal"}',
            "created_at": "2025-12-10 11:00:00",
        },
        {
            "id": 402,
            "pregnancy_id": 101,
            "assessment_id": 302,
            "ultrasound_date": "2026-02-06 14:00:00",
            "gestational_age": 20.5,
            "image_reference": "syn_us_101_t2.dcm",
            "findings": "Targeted mid-trimester structural survey complete. Normal cardiac 4-chamber view, normal spine and kidneys.",
            "source_dataset": ACADEMIC_TAG,
            "metadata_json": '{"transducer": "5.0MHz_curved", "quality": "optimal"}',
            "created_at": "2026-02-06 14:30:00",
        },
        {
            "id": 403,
            "pregnancy_id": 102,
            "assessment_id": 303,
            "ultrasound_date": "2025-11-24 09:30:00",
            "gestational_age": 12.0,
            "image_reference": "syn_us_102_t1.dcm",
            "findings": "Crown-rump length concordant with LMP. No cystic hygroma. Normal calvarium.",
            "source_dataset": ACADEMIC_TAG,
            "metadata_json": '{"transducer": "3.5MHz_convex", "quality": "optimal"}',
            "created_at": "2025-11-24 10:00:00",
        },
        {
            "id": 404,
            "pregnancy_id": 102,
            "assessment_id": 304,
            "ultrasound_date": "2026-02-02 11:00:00",
            "gestational_age": 22.0,
            "image_reference": "syn_us_102_t2.dcm",
            "findings": "Mild asymmetric abdominal circumference lag noted (AC at 18th percentile). Recommended interval growth scan in 3 weeks.",
            "source_dataset": ACADEMIC_TAG,
            "metadata_json": '{"transducer": "5.0MHz_curved", "quality": "adequate"}',
            "created_at": "2026-02-02 11:30:00",
        },
        {
            "id": 405,
            "pregnancy_id": 103,
            "assessment_id": 305,
            "ultrasound_date": "2025-11-01 15:00:00",
            "gestational_age": 12.4,
            "image_reference": "syn_us_103_t1.dcm",
            "findings": "First-trimester anatomy unremarkable, but uterine artery bilateral protodiastolic notches observed.",
            "source_dataset": ACADEMIC_TAG,
            "metadata_json": '{"transducer": "3.5MHz_convex", "quality": "adequate"}',
            "created_at": "2025-11-01 15:30:00",
        },
        {
            "id": 406,
            "pregnancy_id": 103,
            "assessment_id": 306,
            "ultrasound_date": "2026-01-05 10:30:00",
            "gestational_age": 21.0,
            "image_reference": "syn_us_103_t2.dcm",
            "findings": "Significant fetal biometric lag (EFW 14th percentile). Amniotic fluid index normal (AFI 11.2cm).",
            "source_dataset": ACADEMIC_TAG,
            "metadata_json": '{"transducer": "5.0MHz_curved", "quality": "optimal"}',
            "created_at": "2026-01-05 11:00:00",
        },
        {
            "id": 407,
            "pregnancy_id": 104,
            "assessment_id": 307,
            "ultrasound_date": "2026-01-10 11:15:00",
            "gestational_age": 11.8,
            "image_reference": "syn_us_104_t1.dcm",
            "findings": "Early dating ultrasound confirmed intrauterine singleton. Nuchal translucency slightly upper normal (2.1mm).",
            "source_dataset": ACADEMIC_TAG,
            "metadata_json": '{"transducer": "3.5MHz_convex", "quality": "adequate"}',
            "created_at": "2026-01-10 11:45:00",
        },
        {
            "id": 408,
            "pregnancy_id": 104,
            "assessment_id": 308,
            "ultrasound_date": "2026-03-10 14:00:00",
            "gestational_age": 20.0,
            "image_reference": "syn_us_104_t2.dcm",
            "findings": "Mid-trimester evaluation shows symmetrical mild biometry reduction. Placenta anterior, grade I maturity.",
            "source_dataset": ACADEMIC_TAG,
            "metadata_json": '{"transducer": "5.0MHz_curved", "quality": "optimal"}',
            "created_at": "2026-03-10 14:30:00",
        },
        {
            "id": 409,
            "pregnancy_id": 105,
            "assessment_id": 309,
            "ultrasound_date": "2025-09-18 10:00:00",
            "gestational_age": 12.1,
            "image_reference": "syn_us_105_t1.dcm",
            "findings": "Normal 12-week nuchal evaluation. Cervical length measured at 38mm (normal).",
            "source_dataset": ACADEMIC_TAG,
            "metadata_json": '{"transducer": "3.5MHz_convex", "quality": "optimal"}',
            "created_at": "2025-09-18 10:30:00",
        },
        {
            "id": 410,
            "pregnancy_id": 105,
            "assessment_id": 310,
            "ultrasound_date": "2025-11-26 13:45:00",
            "gestational_age": 22.0,
            "image_reference": "syn_us_105_t2.dcm",
            "findings": "Detailed anatomy scan unremarkable. Cervical length 34mm. Fetal somatic growth appropriate for GA.",
            "source_dataset": ACADEMIC_TAG,
            "metadata_json": '{"transducer": "5.0MHz_curved", "quality": "optimal"}',
            "created_at": "2025-11-26 14:15:00",
        },
        {
            "id": 411,
            "pregnancy_id": 106,
            "assessment_id": 311,
            "ultrasound_date": "2026-07-10 09:30:00",
            "gestational_age": 12.3,
            "image_reference": "syn_us_106_t1.dcm",
            "findings": "Active study cohort: First-trimester screening scan completely physiological.",
            "source_dataset": ACADEMIC_TAG,
            "metadata_json": '{"transducer": "3.5MHz_convex", "quality": "optimal"}',
            "created_at": "2026-07-10 10:00:00",
        },
        {
            "id": 412,
            "pregnancy_id": 106,
            "assessment_id": 312,
            "ultrasound_date": "2026-09-04 11:00:00",
            "gestational_age": 20.2,
            "image_reference": "syn_us_106_t2.dcm",
            "findings": "Active study cohort: 20-week anomaly scan within normal physiological limits. Normal growth tracking.",
            "source_dataset": ACADEMIC_TAG,
            "metadata_json": '{"transducer": "5.0MHz_curved", "quality": "optimal"}',
            "created_at": "2026-09-04 11:30:00",
        },
    ]

    # -------------------------------------------------------------
    # 6. LAB RESULTS (lab_results.csv)
    # columns: id, pregnancy_id, assessment_id, papp_a, plgf, free_beta_hcg, test_date, gestational_age, status, source, recorded_at
    # -------------------------------------------------------------
    lab_results = [
        {
            "id": 501,
            "pregnancy_id": 101,
            "assessment_id": 301,
            "papp_a": 1.15,
            "plgf": 62.0,
            "free_beta_hcg": 1.02,
            "test_date": "2025-12-10 11:30:00",
            "gestational_age": 12.2,
            "status": "normal",
            "source": ACADEMIC_TAG,
            "recorded_at": "2025-12-10 12:00:00",
        },
        {
            "id": 502,
            "pregnancy_id": 102,
            "assessment_id": 303,
            "papp_a": 0.85,
            "plgf": 44.0,
            "free_beta_hcg": 0.95,
            "test_date": "2025-11-24 10:30:00",
            "gestational_age": 12.0,
            "status": "borderline",
            "source": ACADEMIC_TAG,
            "recorded_at": "2025-11-24 11:00:00",
        },
        {
            "id": 503,
            "pregnancy_id": 103,
            "assessment_id": 305,
            "papp_a": 0.42,
            "plgf": 24.5,
            "free_beta_hcg": 0.72,
            "test_date": "2025-11-01 16:00:00",
            "gestational_age": 12.4,
            "status": "low_angiogenic_ratio",
            "source": ACADEMIC_TAG,
            "recorded_at": "2025-11-01 16:30:00",
        },
        {
            "id": 504,
            "pregnancy_id": 104,
            "assessment_id": 307,
            "papp_a": 0.58,
            "plgf": 31.0,
            "free_beta_hcg": 1.45,
            "test_date": "2026-01-10 12:00:00",
            "gestational_age": 11.8,
            "status": "high_preeclampsia_risk",
            "source": ACADEMIC_TAG,
            "recorded_at": "2026-01-10 12:30:00",
        },
        {
            "id": 505,
            "pregnancy_id": 105,
            "assessment_id": 309,
            "papp_a": 1.05,
            "plgf": 58.0,
            "free_beta_hcg": 1.10,
            "test_date": "2025-09-18 11:00:00",
            "gestational_age": 12.1,
            "status": "normal",
            "source": ACADEMIC_TAG,
            "recorded_at": "2025-09-18 11:30:00",
        },
        {
            "id": 506,
            "pregnancy_id": 106,
            "assessment_id": 311,
            "papp_a": 1.20,
            "plgf": 65.0,
            "free_beta_hcg": 0.98,
            "test_date": "2026-07-10 10:30:00",
            "gestational_age": 12.3,
            "status": "normal",
            "source": ACADEMIC_TAG,
            "recorded_at": "2026-07-10 11:00:00",
        },
    ]

    # -------------------------------------------------------------
    # 7. DOPPLER RESULTS (doppler_results.csv)
    # columns: id, pregnancy_id, assessment_id, gestational_age, uterine_artery_pi, uterine_artery_status, umbilical_artery_status, other_values, test_date, source, recorded_at
    # -------------------------------------------------------------
    doppler_results = [
        # Patient 1
        {
            "id": 601,
            "pregnancy_id": 101,
            "assessment_id": 301,
            "gestational_age": 12.2,
            "uterine_artery_pi": 1.12,
            "uterine_artery_status": "normal",
            "umbilical_artery_status": "not_applicable_t1",
            "other_values": '{"mean_pi": 1.12, "notch": false}',
            "test_date": "2025-12-10 10:45:00",
            "source": ACADEMIC_TAG,
            "recorded_at": "2025-12-10 11:00:00",
        },
        {
            "id": 602,
            "pregnancy_id": 101,
            "assessment_id": 302,
            "gestational_age": 20.5,
            "uterine_artery_pi": 0.88,
            "uterine_artery_status": "normal",
            "umbilical_artery_status": "normal_flow",
            "other_values": '{"umbilical_pi": 1.02, "ri": 0.65}',
            "test_date": "2026-02-06 14:15:00",
            "source": ACADEMIC_TAG,
            "recorded_at": "2026-02-06 14:30:00",
        },

        # Patient 2
        {
            "id": 603,
            "pregnancy_id": 102,
            "assessment_id": 303,
            "gestational_age": 12.0,
            "uterine_artery_pi": 1.45,
            "uterine_artery_status": "normal",
            "umbilical_artery_status": "not_applicable_t1",
            "other_values": '{"mean_pi": 1.45, "notch": false}',
            "test_date": "2025-11-24 09:45:00",
            "source": ACADEMIC_TAG,
            "recorded_at": "2025-11-24 10:00:00",
        },
        {
            "id": 604,
            "pregnancy_id": 102,
            "assessment_id": 304,
            "gestational_age": 22.0,
            "uterine_artery_pi": 1.18,
            "uterine_artery_status": "mildly_elevated",
            "umbilical_artery_status": "normal_positive_end_diastolic",
            "other_values": '{"umbilical_pi": 1.25, "ri": 0.72}',
            "test_date": "2026-02-02 11:15:00",
            "source": ACADEMIC_TAG,
            "recorded_at": "2026-02-02 11:30:00",
        },

        # Patient 3 (Vascular Scenario)
        {
            "id": 605,
            "pregnancy_id": 103,
            "assessment_id": 305,
            "gestational_age": 12.4,
            "uterine_artery_pi": 2.25,
            "uterine_artery_status": "high_resistance_bilateral_notches",
            "umbilical_artery_status": "not_applicable_t1",
            "other_values": '{"mean_pi": 2.25, "bilateral_notch": true}',
            "test_date": "2025-11-01 15:15:00",
            "source": ACADEMIC_TAG,
            "recorded_at": "2025-11-01 15:30:00",
        },
        {
            "id": 606,
            "pregnancy_id": 103,
            "assessment_id": 306,
            "gestational_age": 21.0,
            "uterine_artery_pi": 1.82,
            "uterine_artery_status": "persistently_high_resistance",
            "umbilical_artery_status": "reduced_end_diastolic_velocity",
            "other_values": '{"umbilical_pi": 1.48, "ri": 0.81}',
            "test_date": "2026-01-05 10:45:00",
            "source": ACADEMIC_TAG,
            "recorded_at": "2026-01-05 11:00:00",
        },

        # Patient 4 (Maternal Risk)
        {
            "id": 607,
            "pregnancy_id": 104,
            "assessment_id": 307,
            "gestational_age": 11.8,
            "uterine_artery_pi": 1.95,
            "uterine_artery_status": "elevated_resistance",
            "umbilical_artery_status": "not_applicable_t1",
            "other_values": '{"mean_pi": 1.95, "unilateral_notch": true}',
            "test_date": "2026-01-10 11:30:00",
            "source": ACADEMIC_TAG,
            "recorded_at": "2026-01-10 11:45:00",
        },
        {
            "id": 608,
            "pregnancy_id": 104,
            "assessment_id": 308,
            "gestational_age": 20.0,
            "uterine_artery_pi": 1.55,
            "uterine_artery_status": "borderline_high",
            "umbilical_artery_status": "positive_diastolic_flow",
            "other_values": '{"umbilical_pi": 1.30, "ri": 0.74}',
            "test_date": "2026-03-10 14:15:00",
            "source": ACADEMIC_TAG,
            "recorded_at": "2026-03-10 14:30:00",
        },

        # Patient 5
        {
            "id": 609,
            "pregnancy_id": 105,
            "assessment_id": 309,
            "gestational_age": 12.1,
            "uterine_artery_pi": 1.15,
            "uterine_artery_status": "normal",
            "umbilical_artery_status": "not_applicable_t1",
            "other_values": '{"mean_pi": 1.15, "notch": false}',
            "test_date": "2025-09-18 10:15:00",
            "source": ACADEMIC_TAG,
            "recorded_at": "2025-09-18 10:30:00",
        },
        {
            "id": 610,
            "pregnancy_id": 105,
            "assessment_id": 310,
            "gestational_age": 22.0,
            "uterine_artery_pi": 0.92,
            "uterine_artery_status": "normal",
            "umbilical_artery_status": "normal_flow",
            "other_values": '{"umbilical_pi": 1.05, "ri": 0.66}',
            "test_date": "2025-11-26 14:00:00",
            "source": ACADEMIC_TAG,
            "recorded_at": "2025-11-26 14:15:00",
        },

        # Patient 6
        {
            "id": 611,
            "pregnancy_id": 106,
            "assessment_id": 311,
            "gestational_age": 12.3,
            "uterine_artery_pi": 1.08,
            "uterine_artery_status": "normal",
            "umbilical_artery_status": "not_applicable_t1",
            "other_values": '{"mean_pi": 1.08, "notch": false}',
            "test_date": "2026-07-10 09:45:00",
            "source": ACADEMIC_TAG,
            "recorded_at": "2026-07-10 10:00:00",
        },
        {
            "id": 612,
            "pregnancy_id": 106,
            "assessment_id": 312,
            "gestational_age": 20.2,
            "uterine_artery_pi": 0.85,
            "uterine_artery_status": "normal",
            "umbilical_artery_status": "normal_flow",
            "other_values": '{"umbilical_pi": 0.98, "ri": 0.63}',
            "test_date": "2026-09-04 11:15:00",
            "source": ACADEMIC_TAG,
            "recorded_at": "2026-09-04 11:30:00",
        },
    ]

    # -------------------------------------------------------------
    # 8. PREDICTIONS (predictions.csv)
    # columns: id, patient_id, pregnancy_id, assessment_id, prediction_type, target, predicted_value, confidence, model_name, model_version, prediction_horizon, timestamp, risk_score, risk_level, xgb_score, cnn_lstm_score, ae_score, transformer_score, created_at
    # -------------------------------------------------------------
    predictions = [
        {
            "id": 101,
            "patient_id": "P-SYN-001",
            "pregnancy_id": 101,
            "assessment_id": 301,
            "prediction_type": "fetal_growth_restriction",
            "target": "EFW_PERCENTILE_T2",
            "predicted_value": 52.0,
            "confidence": 0.95,
            "model_name": "Demo-FGR-Predictor",
            "model_version": "v1.0-academic",
            "prediction_horizon": "mid_trimester_20w",
            "timestamp": "2025-12-10 12:00:00",
            "risk_score": 0.08,
            "risk_level": "LOW",
            "xgb_score": 0.07,
            "cnn_lstm_score": 0.09,
            "ae_score": 0.05,
            "transformer_score": 0.08,
            "created_at": "2025-12-10 12:00:00",
        },
        {
            "id": 102,
            "patient_id": "P-SYN-002",
            "pregnancy_id": 102,
            "assessment_id": 303,
            "prediction_type": "fetal_growth_restriction",
            "target": "EFW_PERCENTILE_T2",
            "predicted_value": 48.0,
            "confidence": 0.88,
            "model_name": "Demo-FGR-Predictor",
            "model_version": "v1.0-academic",
            "prediction_horizon": "mid_trimester_20w",
            "timestamp": "2025-11-24 11:00:00",
            "risk_score": 0.15,
            "risk_level": "LOW",
            "xgb_score": 0.14,
            "cnn_lstm_score": 0.16,
            "ae_score": 0.12,
            "transformer_score": 0.15,
            "created_at": "2025-11-24 11:00:00",
        },
        {
            "id": 103,
            "patient_id": "P-SYN-003",
            "pregnancy_id": 103,
            "assessment_id": 305,
            "prediction_type": "fetal_growth_restriction",
            "target": "EFW_PERCENTILE_T2",
            "predicted_value": 30.0,
            "confidence": 0.91,
            "model_name": "Demo-FGR-Predictor",
            "model_version": "v1.0-academic",
            "prediction_horizon": "mid_trimester_20w",
            "timestamp": "2025-11-01 16:30:00",
            "risk_score": 0.68,
            "risk_level": "WATCH",
            "xgb_score": 0.65,
            "cnn_lstm_score": 0.70,
            "ae_score": 0.62,
            "transformer_score": 0.69,
            "created_at": "2025-11-01 16:30:00",
        },
        {
            "id": 104,
            "patient_id": "P-SYN-004",
            "pregnancy_id": 104,
            "assessment_id": 307,
            "prediction_type": "fetal_growth_restriction",
            "target": "EFW_PERCENTILE_T2",
            "predicted_value": 35.0,
            "confidence": 0.94,
            "model_name": "Demo-FGR-Predictor",
            "model_version": "v1.0-academic",
            "prediction_horizon": "mid_trimester_20w",
            "timestamp": "2026-01-10 12:30:00",
            "risk_score": 0.76,
            "risk_level": "HIGH",
            "xgb_score": 0.78,
            "cnn_lstm_score": 0.75,
            "ae_score": 0.72,
            "transformer_score": 0.77,
            "created_at": "2026-01-10 12:30:00",
        },
        {
            "id": 105,
            "patient_id": "P-SYN-005",
            "pregnancy_id": 105,
            "assessment_id": 309,
            "prediction_type": "fetal_growth_restriction",
            "target": "EFW_PERCENTILE_T2",
            "predicted_value": 50.0,
            "confidence": 0.92,
            "model_name": "Demo-FGR-Predictor",
            "model_version": "v1.0-academic",
            "prediction_horizon": "mid_trimester_20w",
            "timestamp": "2025-09-18 11:30:00",
            "risk_score": 0.10,
            "risk_level": "LOW",
            "xgb_score": 0.09,
            "cnn_lstm_score": 0.11,
            "ae_score": 0.08,
            "transformer_score": 0.10,
            "created_at": "2025-09-18 11:30:00",
        },
        {
            "id": 106,
            "patient_id": "P-SYN-006",
            "pregnancy_id": 106,
            "assessment_id": 311,
            "prediction_type": "fetal_growth_restriction",
            "target": "EFW_PERCENTILE_T2",
            "predicted_value": 55.0,
            "confidence": 0.96,
            "model_name": "Demo-FGR-Predictor",
            "model_version": "v1.0-academic",
            "prediction_horizon": "mid_trimester_20w",
            "timestamp": "2026-07-10 11:00:00",
            "risk_score": 0.06,
            "risk_level": "LOW",
            "xgb_score": 0.05,
            "cnn_lstm_score": 0.07,
            "ae_score": 0.04,
            "transformer_score": 0.06,
            "created_at": "2026-07-10 11:00:00",
        },
    ]

    # -------------------------------------------------------------
    # 9. GROWTH ANALYSIS (growth_analysis.csv)
    # columns: id, pregnancy_id, predicted_efw_percentile, actual_efw_percentile, growth_variance, evaluation_status, contributing_patterns, model_version, generated_at
    # -------------------------------------------------------------
    growth_analysis = [
        {
            "id": 201,
            "pregnancy_id": 101,
            "predicted_efw_percentile": 52.0,
            "actual_efw_percentile": 50.0,
            "growth_variance": -2.0,
            "evaluation_status": "NORMAL_CONCORDANT",
            "contributing_patterns": "Normal trajectory with minimal deviation from first-trimester prediction.",
            "model_version": "v1.0-academic",
            "generated_at": "2026-02-06 15:00:00",
        },
        {
            "id": 202,
            "pregnancy_id": 102,
            "predicted_efw_percentile": 48.0,
            "actual_efw_percentile": 22.0,
            "growth_variance": -26.0,
            "evaluation_status": "GROWTH_RESTRICTION_SUSPECTED",
            "contributing_patterns": "Significant negative deviation (-26 percentile points); fetal abdominal circumference lag.",
            "model_version": "v1.0-academic",
            "generated_at": "2026-02-02 12:00:00",
        },
        {
            "id": 203,
            "pregnancy_id": 103,
            "predicted_efw_percentile": 30.0,
            "actual_efw_percentile": 14.0,
            "growth_variance": -16.0,
            "evaluation_status": "EARLY_FGR_VASCULAR",
            "contributing_patterns": "Progression towards severe growth lag accompanied by abnormal Doppler resistance.",
            "model_version": "v1.0-academic",
            "generated_at": "2026-01-05 11:30:00",
        },
        {
            "id": 204,
            "pregnancy_id": 104,
            "predicted_efw_percentile": 35.0,
            "actual_efw_percentile": 28.0,
            "growth_variance": -7.0,
            "evaluation_status": "MATERNAL_RISK_CONCORDANT",
            "contributing_patterns": "Mild negative deviation consistent with high maternal baseline vascular and metabolic risk.",
            "model_version": "v1.0-academic",
            "generated_at": "2026-03-10 15:00:00",
        },
        {
            "id": 205,
            "pregnancy_id": 105,
            "predicted_efw_percentile": 50.0,
            "actual_efw_percentile": 48.0,
            "growth_variance": -2.0,
            "evaluation_status": "NORMAL_ANTEPARTUM",
            "contributing_patterns": "Normal fetal somatic growth throughout antepartum period before acute preterm labor.",
            "model_version": "v1.0-academic",
            "generated_at": "2025-11-26 14:30:00",
        },
        {
            "id": 206,
            "pregnancy_id": 106,
            "predicted_efw_percentile": 55.0,
            "actual_efw_percentile": 54.0,
            "growth_variance": -1.0,
            "evaluation_status": "NORMAL_ACTIVE",
            "contributing_patterns": "Optimal physiological growth trajectory in current ongoing gestation.",
            "model_version": "v1.0-academic",
            "generated_at": "2026-09-04 12:00:00",
        },
    ]

    # -------------------------------------------------------------
    # 10. CLINICAL EVENTS (clinical_events.csv)
    # columns: id, patient_id, pregnancy_id, event_type, event_date, details, created_at
    # -------------------------------------------------------------
    clinical_events = [
        {
            "id": 701,
            "patient_id": "P-SYN-001",
            "pregnancy_id": 101,
            "event_type": "first_trimester_screen",
            "event_date": "2025-12-10 10:30:00",
            "details": "Routine 1st trimester combined screening completed; low risk calculated.",
            "created_at": "2025-12-10 11:30:00",
        },
        {
            "id": 702,
            "patient_id": "P-SYN-001",
            "pregnancy_id": 101,
            "event_type": "labor_delivery",
            "event_date": "2026-07-03 08:15:00",
            "details": "Spontaneous vaginal delivery at 39 weeks 2 days without maternal-fetal complications.",
            "created_at": "2026-07-03 10:00:00",
        },
        {
            "id": 703,
            "patient_id": "P-SYN-002",
            "pregnancy_id": 102,
            "event_type": "growth_deviation_flag",
            "event_date": "2026-02-02 12:30:00",
            "details": "Automated alert: Fetal abdominal growth trajectory decoupled from 1st-trimester forecast (-26% variance).",
            "created_at": "2026-02-02 12:30:00",
        },
        {
            "id": 704,
            "patient_id": "P-SYN-002",
            "pregnancy_id": 102,
            "event_type": "labor_delivery",
            "event_date": "2026-06-05 14:20:00",
            "details": "Induced labor for fetal growth restriction at 37 weeks 5 days.",
            "created_at": "2026-06-05 16:00:00",
        },
        {
            "id": 705,
            "patient_id": "P-SYN-003",
            "pregnancy_id": 103,
            "event_type": "vascular_risk_detection",
            "event_date": "2025-11-01 16:00:00",
            "details": "Bilateral uterine artery notch detected alongside PlGF reduction.",
            "created_at": "2025-11-01 16:30:00",
        },
        {
            "id": 706,
            "patient_id": "P-SYN-003",
            "pregnancy_id": 103,
            "event_type": "preterm_cesarean",
            "event_date": "2026-04-28 09:45:00",
            "details": "Cesarean delivery performed at 35w6d due to abnormal umbilical artery Doppler and non-reassuring CTG.",
            "created_at": "2026-04-28 11:00:00",
        },
        {
            "id": 707,
            "patient_id": "P-SYN-004",
            "pregnancy_id": 104,
            "event_type": "mfm_multidisciplinary_review",
            "event_date": "2026-01-15 14:00:00",
            "details": "Maternal-fetal medicine review for chronic hypertension and diabetes optimization.",
            "created_at": "2026-01-15 15:00:00",
        },
        {
            "id": 708,
            "patient_id": "P-SYN-004",
            "pregnancy_id": 104,
            "event_type": "scheduled_cesarean",
            "event_date": "2026-07-15 08:30:00",
            "details": "Elective primary cesarean section at 36 weeks 4 days.",
            "created_at": "2026-07-15 10:30:00",
        },
        {
            "id": 709,
            "patient_id": "P-SYN-005",
            "pregnancy_id": 105,
            "event_type": "acute_pprom",
            "event_date": "2026-02-18 04:30:00",
            "details": "Preterm premature rupture of membranes at 32 weeks 0 days; betamethasone course administered.",
            "created_at": "2026-02-18 06:00:00",
        },
        {
            "id": 710,
            "patient_id": "P-SYN-005",
            "pregnancy_id": 105,
            "event_type": "preterm_precipitous_delivery",
            "event_date": "2026-02-19 11:20:00",
            "details": "Preterm vaginal delivery of viable infant at 32 weeks 1 day.",
            "created_at": "2026-02-19 13:00:00",
        },
    ]

    # -------------------------------------------------------------
    # 11. DOCTOR REVIEWS (doctor_reviews.csv)
    # columns: id, patient_id, pregnancy_id, clinician_id, review_date, findings, assessment, recommendations, notes, created_at
    # -------------------------------------------------------------
    doctor_reviews = [
        {
            "id": 801,
            "patient_id": "P-SYN-001",
            "pregnancy_id": 101,
            "clinician_id": "DOC-OBGYN-01",
            "review_date": "2025-12-10 11:15:00",
            "findings": "Normal 12-week combined ultrasound and biochemistry parameters.",
            "assessment": "Low-risk ongoing singleton pregnancy.",
            "recommendations": "Continue standard routine antenatal care; routine 20-week anatomy scan.",
            "notes": "Patient reassured regarding low aneuploidy and FGR risk.",
            "created_at": "2025-12-10 11:30:00",
        },
        {
            "id": 802,
            "patient_id": "P-SYN-001",
            "pregnancy_id": 101,
            "clinician_id": "DOC-OBGYN-01",
            "review_date": "2026-02-06 14:45:00",
            "findings": "Mid-trimester scan perfectly concordant with 1st-trimester prediction.",
            "assessment": "Appropriate for gestational age (50th percentile).",
            "recommendations": "Routine third-trimester visit at 28 weeks.",
            "notes": "No interventions needed.",
            "created_at": "2026-02-06 15:00:00",
        },
        {
            "id": 803,
            "patient_id": "P-SYN-002",
            "pregnancy_id": 102,
            "clinician_id": "DOC-OBGYN-02",
            "review_date": "2026-02-02 12:00:00",
            "findings": "EFW percentile decreased from expected 48th to actual 22nd percentile.",
            "assessment": "Emerging fetal growth restriction (late-onset pattern).",
            "recommendations": "Serial bi-weekly ultrasound biometry and umbilical Doppler starting at 26 weeks.",
            "notes": "Advised on fetal movement counting.",
            "created_at": "2026-02-02 12:30:00",
        },
        {
            "id": 804,
            "patient_id": "P-SYN-003",
            "pregnancy_id": 103,
            "clinician_id": "DOC-MFM-01",
            "review_date": "2025-11-01 16:15:00",
            "findings": "Elevated mean uterine artery PI (2.25) with persistent diastolic notch.",
            "assessment": "High risk of early placental insufficiency and preeclampsia.",
            "recommendations": "Initiate prophylactic low-dose aspirin immediately (150mg nightly).",
            "notes": "FGR prediction model output confirmed high risk (0.68).",
            "created_at": "2025-11-01 16:45:00",
        },
        {
            "id": 805,
            "patient_id": "P-SYN-003",
            "pregnancy_id": 103,
            "clinician_id": "DOC-MFM-01",
            "review_date": "2026-01-05 11:15:00",
            "findings": "EFW 14th percentile with elevated umbilical artery resistance.",
            "assessment": "Early fetal growth restriction confirmed.",
            "recommendations": "Weekly Doppler flow velocity waveforms; delivery planning around 36 weeks.",
            "notes": "Close fetal surveillance indicated.",
            "created_at": "2026-01-05 11:45:00",
        },
        {
            "id": 806,
            "patient_id": "P-SYN-004",
            "pregnancy_id": 104,
            "clinician_id": "DOC-MFM-02",
            "review_date": "2026-01-10 12:45:00",
            "findings": "Pre-existing hypertension and diabetes compound placental risk profile.",
            "assessment": "High-risk pregnancy due to maternal comorbidities.",
            "recommendations": "Maintain strict BP control (<135/85); start low-dose aspirin; endo consult.",
            "notes": "Prescription of labetalol updated.",
            "created_at": "2026-01-10 13:00:00",
        },
        {
            "id": 807,
            "patient_id": "P-SYN-005",
            "pregnancy_id": 105,
            "clinician_id": "DOC-NEO-01",
            "review_date": "2026-02-19 14:00:00",
            "findings": "Preterm delivery at 32w1d; infant experiencing mild grunting and retractions.",
            "assessment": "Preterm infant (32w) with moderate Respiratory Distress Syndrome (RDS).",
            "recommendations": "Admit to NICU Level III; initiate CPAP and surfactant protocol.",
            "notes": "NICU monitoring team mobilized.",
            "created_at": "2026-02-19 14:30:00",
        },
        {
            "id": 808,
            "patient_id": "P-SYN-006",
            "pregnancy_id": 106,
            "clinician_id": "DOC-OBGYN-01",
            "review_date": "2026-09-04 11:45:00",
            "findings": "Normal 20-week ultrasound; patient reports feeling regular fetal kicks.",
            "assessment": "Active normal pregnancy proceeding as expected.",
            "recommendations": "Routine glucose tolerance test at 24-28 weeks.",
            "notes": "Patient counselled, all questions answered.",
            "created_at": "2026-09-04 12:00:00",
        },
    ]

    # -------------------------------------------------------------
    # 12. PRESCRIPTIONS (prescriptions.csv)
    # columns: id, patient_id, pregnancy_id, clinician_id, medication_name, dosage, start_date, end_date, notes, created_at
    # -------------------------------------------------------------
    prescriptions = [
        {
            "id": 901,
            "patient_id": "P-SYN-001",
            "pregnancy_id": 101,
            "clinician_id": "DOC-OBGYN-01",
            "medication_name": "Prenatal Multivitamin with Folic Acid",
            "dosage": "1 tablet daily",
            "start_date": "2025-10-15 00:00:00",
            "end_date": "2026-07-15 00:00:00",
            "notes": "Routine antenatal supplementation",
            "created_at": "2025-10-15 10:30:00",
        },
        {
            "id": 902,
            "patient_id": "P-SYN-003",
            "pregnancy_id": 103,
            "clinician_id": "DOC-MFM-01",
            "medication_name": "Aspirin (Low-Dose)",
            "dosage": "150 mg once daily at bedtime",
            "start_date": "2025-11-01 00:00:00",
            "end_date": "2026-04-20 00:00:00",
            "notes": "Preeclampsia and placental insufficiency prophylaxis following abnormal 1st trimester Doppler",
            "created_at": "2025-11-01 16:30:00",
        },
        {
            "id": 903,
            "patient_id": "P-SYN-004",
            "pregnancy_id": 104,
            "clinician_id": "DOC-MFM-02",
            "medication_name": "Labetalol Hydrochloride",
            "dosage": "100 mg orally twice daily",
            "start_date": "2025-11-15 00:00:00",
            "end_date": "2026-07-20 00:00:00",
            "notes": "Antihypertensive therapy for pre-existing chronic hypertension",
            "created_at": "2025-11-15 11:30:00",
        },
        {
            "id": 904,
            "patient_id": "P-SYN-004",
            "pregnancy_id": 104,
            "clinician_id": "DOC-MFM-02",
            "medication_name": "Aspirin (Low-Dose)",
            "dosage": "150 mg once daily at bedtime",
            "start_date": "2026-01-10 00:00:00",
            "end_date": "2026-07-05 00:00:00",
            "notes": "Preeclampsia prevention in high-risk maternal comorbidities",
            "created_at": "2026-01-10 13:00:00",
        },
    ]

    # -------------------------------------------------------------
    # 13. NEWBORNS (newborns.csv)
    # columns: id, pregnancy_id, newborn_code, birth_date, gestational_age_at_birth, birth_weight, birth_length, birth_status, created_at
    # -------------------------------------------------------------
    newborns = [
        {
            "id": 1001,
            "pregnancy_id": 101,
            "newborn_code": "SYN-NB-1001",
            "birth_date": "2026-07-03 08:15:00",
            "gestational_age_at_birth": 39.2,
            "birth_weight": 3350.0,
            "birth_length": 50.0,
            "birth_status": "healthy_live_birth",
            "created_at": "2026-07-03 09:00:00",
        },
        {
            "id": 1002,
            "pregnancy_id": 102,
            "newborn_code": "SYN-NB-1002",
            "birth_date": "2026-06-05 14:20:00",
            "gestational_age_at_birth": 37.5,
            "birth_weight": 2450.0,
            "birth_length": 46.5,
            "birth_status": "small_for_gestational_age",
            "created_at": "2026-06-05 15:00:00",
        },
        {
            "id": 1003,
            "pregnancy_id": 103,
            "newborn_code": "SYN-NB-1003",
            "birth_date": "2026-04-28 09:45:00",
            "gestational_age_at_birth": 35.8,
            "birth_weight": 2080.0,
            "birth_length": 44.0,
            "birth_status": "late_preterm_fgr",
            "created_at": "2026-04-28 10:30:00",
        },
        {
            "id": 1004,
            "pregnancy_id": 104,
            "newborn_code": "SYN-NB-1004",
            "birth_date": "2026-07-15 08:30:00",
            "gestational_age_at_birth": 36.5,
            "birth_weight": 2550.0,
            "birth_length": 47.0,
            "birth_status": "near_term_infant",
            "created_at": "2026-07-15 09:15:00",
        },
        {
            "id": 1005,
            "pregnancy_id": 105,
            "newborn_code": "SYN-NB-1005",
            "birth_date": "2026-02-19 11:20:00",
            "gestational_age_at_birth": 32.1,
            "birth_weight": 1620.0,
            "birth_length": 41.0,
            "birth_status": "very_preterm_infant",
            "created_at": "2026-02-19 12:00:00",
        },
    ]

    # -------------------------------------------------------------
    # 14. NICU ADMISSIONS (nicu_admissions.csv)
    # columns: id, newborn_id, admission_date, discharge_date, admission_reason, status, created_at, updated_at
    # -------------------------------------------------------------
    nicu_admissions = [
        {
            "id": 2001,
            "newborn_id": 1002,  # P-SYN-002
            "admission_date": "2026-06-05 15:30:00",
            "discharge_date": "2026-06-08 11:00:00",
            "admission_reason": "Low birth weight (2450g), mild hypothermia and feeding observation.",
            "status": "discharged",
            "created_at": "2026-06-05 16:00:00",
            "updated_at": "2026-06-08 11:30:00",
        },
        {
            "id": 2002,
            "newborn_id": 1003,  # P-SYN-003
            "admission_date": "2026-04-28 10:45:00",
            "discharge_date": "2026-05-04 14:00:00",
            "admission_reason": "Late preterm 35.8w, birth weight 2080g, transient tachypnea of the newborn.",
            "status": "discharged",
            "created_at": "2026-04-28 11:15:00",
            "updated_at": "2026-05-04 14:30:00",
        },
        {
            "id": 2003,
            "newborn_id": 1004,  # P-SYN-004
            "admission_date": "2026-07-15 09:45:00",
            "discharge_date": "2026-07-18 10:00:00",
            "admission_reason": "Maternal gestational diabetes protocol, neonatal hypoglycemia surveillance.",
            "status": "discharged",
            "created_at": "2026-07-15 10:15:00",
            "updated_at": "2026-07-18 10:30:00",
        },
        {
            "id": 2004,
            "newborn_id": 1005,  # P-SYN-005
            "admission_date": "2026-02-19 12:15:00",
            "discharge_date": "2026-03-25 15:00:00",
            "admission_reason": "Very preterm infant 32.1w, 1620g, Respiratory Distress Syndrome requiring CPAP and surfactant.",
            "status": "discharged",
            "created_at": "2026-02-19 13:00:00",
            "updated_at": "2026-03-25 15:30:00",
        },
    ]

    # -------------------------------------------------------------
    # 15. NICU VITALS (nicu_vitals.csv)
    # columns: id, nicu_admission_id, timestamp, heart_rate, spo2, respiratory_rate, temperature, source, created_at
    # -------------------------------------------------------------
    nicu_vitals = []
    vital_id = 3001

    # Admission 2001 (P-SYN-002: 5 readings)
    t0 = datetime(2026, 6, 5, 16, 0, 0)
    for i in range(5):
        nicu_vitals.append({
            "id": vital_id,
            "nicu_admission_id": 2001,
            "timestamp": (t0 + timedelta(hours=i*2)).strftime("%Y-%m-%d %H:%M:%S"),
            "heart_rate": round(138.0 + (i * 1.2), 1),
            "spo2": round(96.5 + (i * 0.4), 1),
            "respiratory_rate": round(44.0 + (i * 0.5), 1),
            "temperature": round(36.4 + (i * 0.15), 1),
            "source": "NICU_BEDSIDE_MONITOR",
            "created_at": (t0 + timedelta(hours=i*2)).strftime("%Y-%m-%d %H:%M:%S"),
        })
        vital_id += 1

    # Admission 2002 (P-SYN-003: 5 readings with mild tachycardia)
    t0 = datetime(2026, 4, 28, 11, 0, 0)
    for i in range(5):
        nicu_vitals.append({
            "id": vital_id,
            "nicu_admission_id": 2002,
            "timestamp": (t0 + timedelta(hours=i*2)).strftime("%Y-%m-%d %H:%M:%S"),
            "heart_rate": round(152.0 + (i * 2.0), 1),
            "spo2": round(94.0 + (i * 0.8), 1),
            "respiratory_rate": round(52.0 - (i * 1.5), 1),
            "temperature": round(36.8 + (i * 0.05), 1),
            "source": "NICU_BEDSIDE_MONITOR",
            "created_at": (t0 + timedelta(hours=i*2)).strftime("%Y-%m-%d %H:%M:%S"),
        })
        vital_id += 1

    # Admission 2003 (P-SYN-004: 5 readings, stable)
    t0 = datetime(2026, 7, 15, 10, 0, 0)
    for i in range(5):
        nicu_vitals.append({
            "id": vital_id,
            "nicu_admission_id": 2003,
            "timestamp": (t0 + timedelta(hours=i*3)).strftime("%Y-%m-%d %H:%M:%S"),
            "heart_rate": round(142.0 + (i * 0.5), 1),
            "spo2": round(97.0 + (i * 0.2), 1),
            "respiratory_rate": round(42.0 + (i * 0.5), 1),
            "temperature": round(36.7 + (i * 0.05), 1),
            "source": "NICU_BEDSIDE_MONITOR",
            "created_at": (t0 + timedelta(hours=i*3)).strftime("%Y-%m-%d %H:%M:%S"),
        })
        vital_id += 1

    # Admission 2004 (P-SYN-005: 11 readings showing acute RDS desaturation episode)
    t0 = datetime(2026, 2, 19, 13, 0, 0)
    for i in range(11):
        # Desaturation event around hour 4-6
        if i in [3, 4]:
            hr = 168.0 + (i * 3.0)
            spo2 = 84.5 - (i * 1.5)
            rr = 64.0
        elif i in [5, 6]:
            hr = 162.0
            spo2 = 88.0 + (i * 1.0)
            rr = 58.0
        else:
            hr = 144.0 + (i * 1.0)
            spo2 = 95.0 + (i * 0.3)
            rr = 46.0

        nicu_vitals.append({
            "id": vital_id,
            "nicu_admission_id": 2004,
            "timestamp": (t0 + timedelta(hours=i)).strftime("%Y-%m-%d %H:%M:%S"),
            "heart_rate": round(hr, 1),
            "spo2": min(100.0, round(spo2, 1)),
            "respiratory_rate": round(rr, 1),
            "temperature": round(36.9 + (i * 0.02), 1),
            "source": "NICU_ICU_TELEMETRY",
            "created_at": (t0 + timedelta(hours=i)).strftime("%Y-%m-%d %H:%M:%S"),
        })
        vital_id += 1

    # -------------------------------------------------------------
    # 16. MODEL OUTPUTS (model_outputs.csv)
    # columns: id, patient_id, pregnancy_id, newborn_id, nicu_admission_id, model_name, model_version, input_reference, output_type, output_value, confidence, explanation_reference, created_at
    # -------------------------------------------------------------
    model_outputs = [
        {
            "id": 4001,
            "patient_id": "P-SYN-001",
            "pregnancy_id": 101,
            "newborn_id": None,
            "nicu_admission_id": None,
            "model_name": "FGRNet-Tabular",
            "model_version": "v1.0-academic",
            "input_reference": "assessment_301_features",
            "output_type": "fgr_probability",
            "output_value": 0.08,
            "confidence": 0.95,
            "explanation_reference": "shap_p101_t1.json",
            "created_at": "2025-12-10 12:00:00",
        },
        {
            "id": 4002,
            "patient_id": "P-SYN-002",
            "pregnancy_id": 102,
            "newborn_id": None,
            "nicu_admission_id": None,
            "model_name": "FGRNet-Tabular",
            "model_version": "v1.0-academic",
            "input_reference": "assessment_303_features",
            "output_type": "fgr_probability",
            "output_value": 0.15,
            "confidence": 0.88,
            "explanation_reference": "shap_p102_t1.json",
            "created_at": "2025-11-24 11:00:00",
        },
        {
            "id": 4003,
            "patient_id": "P-SYN-003",
            "pregnancy_id": 103,
            "newborn_id": None,
            "nicu_admission_id": None,
            "model_name": "FGRNet-Vascular",
            "model_version": "v1.0-academic",
            "input_reference": "assessment_305_features",
            "output_type": "vascular_fgr_risk",
            "output_value": 0.68,
            "confidence": 0.91,
            "explanation_reference": "shap_p103_t1.json",
            "created_at": "2025-11-01 16:30:00",
        },
        {
            "id": 4004,
            "patient_id": "P-SYN-004",
            "pregnancy_id": 104,
            "newborn_id": None,
            "nicu_admission_id": None,
            "model_name": "FGRNet-MaternalRisk",
            "model_version": "v1.0-academic",
            "input_reference": "assessment_307_features",
            "output_type": "preeclampsia_fgr_risk",
            "output_value": 0.76,
            "confidence": 0.94,
            "explanation_reference": "shap_p104_t1.json",
            "created_at": "2026-01-10 12:30:00",
        },
        {
            "id": 4005,
            "patient_id": "P-SYN-005",
            "pregnancy_id": 105,
            "newborn_id": 1005,
            "nicu_admission_id": 2004,
            "model_name": "NICU-Autoencoder-Anomaly",
            "model_version": "v1.0-academic",
            "input_reference": "vital_signs_window_3015_3020",
            "output_type": "vital_reconstruction_error",
            "output_value": 0.94,
            "confidence": 0.96,
            "explanation_reference": "ae_reconstruction_error_p105.json",
            "created_at": "2026-02-19 17:30:00",
        },
        {
            "id": 4006,
            "patient_id": "P-SYN-005",
            "pregnancy_id": 105,
            "newborn_id": 1005,
            "nicu_admission_id": 2004,
            "model_name": "NICU-Fusion-Deterioration",
            "model_version": "v1.0-academic",
            "input_reference": "multimodal_telemetry_window",
            "output_type": "deterioration_probability",
            "output_value": 0.86,
            "confidence": 0.93,
            "explanation_reference": "fusion_shap_p105.json",
            "created_at": "2026-02-19 17:30:00",
        },
    ]

    # -------------------------------------------------------------
    # 17. ALERTS (alerts.csv)
    # columns: id, patient_id, newborn_id, nicu_admission_id, alert_type, severity, risk_score, triggering_factors, model_version, status, created_at, acknowledged_at, acknowledged_by
    # -------------------------------------------------------------
    alerts = [
        {
            "id": 5001,
            "patient_id": "P-SYN-003",
            "newborn_id": None,
            "nicu_admission_id": None,
            "alert_type": "fgr_vascular_high_risk",
            "severity": "medium",
            "risk_score": 0.68,
            "triggering_factors": "Bilateral uterine artery notch, low PlGF (24.5 pg/mL), elevated MAP (96 mmHg).",
            "model_version": "v1.0-academic",
            "status": "acknowledged",
            "created_at": "2025-11-01 16:30:00",
            "acknowledged_at": "2025-11-01 16:45:00",
            "acknowledged_by": "DOC-MFM-01",
        },
        {
            "id": 5002,
            "patient_id": "P-SYN-004",
            "newborn_id": None,
            "nicu_admission_id": None,
            "alert_type": "maternal_comorbidity_high_risk",
            "severity": "high",
            "risk_score": 0.76,
            "triggering_factors": "Chronic hypertension (MAP 108 mmHg), pregestational diabetes, high UtA PI (1.95).",
            "model_version": "v1.0-academic",
            "status": "acknowledged",
            "created_at": "2026-01-10 12:30:00",
            "acknowledged_at": "2026-01-10 13:00:00",
            "acknowledged_by": "DOC-MFM-02",
        },
        {
            "id": 5003,
            "patient_id": "P-SYN-002",
            "newborn_id": None,
            "nicu_admission_id": None,
            "alert_type": "growth_deviation_flag",
            "severity": "medium",
            "risk_score": 0.62,
            "triggering_factors": "Fetal growth trajectory dropped 26 percentile points between T1 prediction and T2 actual.",
            "model_version": "v1.0-academic",
            "status": "acknowledged",
            "created_at": "2026-02-02 12:00:00",
            "acknowledged_at": "2026-02-02 12:30:00",
            "acknowledged_by": "DOC-OBGYN-02",
        },
        {
            "id": 5004,
            "patient_id": "P-SYN-005",
            "newborn_id": 1005,
            "nicu_admission_id": 2004,
            "alert_type": "acute_neonatal_hypoxemia",
            "severity": "high",
            "risk_score": 0.88,
            "triggering_factors": "Sustained oxygen desaturation below 85% (SpO2=83.0%) with reactive tachycardia (HR=174 bpm).",
            "model_version": "v1.0-academic",
            "status": "acknowledged",
            "created_at": "2026-02-19 17:30:00",
            "acknowledged_at": "2026-02-19 17:35:00",
            "acknowledged_by": "DOC-NEO-01",
        },
    ]

    # Write all CSV files
    file_map = {
        "patients.csv": patients,
        "pregnancies.csv": pregnancies,
        "maternal_profiles.csv": maternal_profiles,
        "fetal_assessments.csv": fetal_assessments,
        "ultrasound_records.csv": ultrasound_records,
        "lab_results.csv": lab_results,
        "doppler_results.csv": doppler_results,
        "predictions.csv": predictions,
        "growth_analysis.csv": growth_analysis,
        "clinical_events.csv": clinical_events,
        "doctor_reviews.csv": doctor_reviews,
        "prescriptions.csv": prescriptions,
        "newborns.csv": newborns,
        "nicu_admissions.csv": nicu_admissions,
        "nicu_vitals.csv": nicu_vitals,
        "model_outputs.csv": model_outputs,
        "alerts.csv": alerts,
    }

    summary = {}
    for fname, data in file_map.items():
        filepath = os.path.join(SYNTHETIC_DIR, fname)
        if not data:
            continue
        fieldnames = list(data[0].keys())
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        summary[fname] = len(data)
        print(f"  [CREATED] {fname:<25}: {len(data)} records ({len(fieldnames)} columns)")

    print(f"\nAll {len(file_map)} synthetic CSV files generated successfully!")
    return summary


if __name__ == "__main__":
    generate_all()

