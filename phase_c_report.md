# Phase C Report — Synthetic Longitudinal Dataset Creation

**Project**: NeoNatal Watch AI  
**Date**: September 22, 2026  
**Status**: COMPLETE (Staged in CSVs; Validation Passed; NOT Imported into MySQL)  

---

## 1. Executive Summary

Phase C successfully produced a lightweight, realistic, and completely synthetic longitudinal dataset designed specifically for end-to-end demonstration and architectural testing of the **NeoNatal Watch AI** platform.

The dataset captures the entire maternal-fetal-neonatal trajectory:
- Maternal booking and risk profiles
- First-trimester biometrics (CRL, NT, nasal bone) and biomarkers (PAPP-A, PlGF)
- First-trimester AI predictions (EFW percentile forecast, deterioration risk)
- Second-trimester ultrasound biometry and Doppler hemodynamics (uterine & umbilical arteries)
- Trajectory growth analyses (predicted vs. actual variance)
- Longitudinal clinical events, clinician reviews, and pharmacological prescriptions
- Labor, delivery, and newborn outcomes
- Postnatal NICU admissions, continuous vital sign monitoring (HR, SpO2, RR, Temp), multimodal alerts, and explainability audit logs

All 17 CSV files have been created in `data/synthetic/`, rigorously validated for structural, relational, and chronological consistency, and staged awaiting Phase E for controlled pipeline ingestion. **No data has been inserted into MySQL during Phase C.**

---

## 2. Number of Synthetic Patients & Scenarios Created

A total of **6 unique synthetic patients** (`P-SYN-001` through `P-SYN-006`) were created across 6 distinct clinical demonstration scenarios:

| Scenario | Patient ID | Clinical Scenario | Demonstration Objective |
|---|---|---|---|
| **Scenario A** | `P-SYN-001` | Normal Longitudinal Pregnancy & Outcome | Low-risk primigravida, concordant 1st/2nd trimester growth (50th percentile), full-term vaginal delivery (3350g), NICU-free outcome. |
| **Scenario B** | `P-SYN-002` | Fetal Growth Restriction (FGR) Decoupling | Normal 1st-trimester prediction (48th percentile), sharp mid-trimester drop (22nd percentile, -26% variance), late-onset FGR, late-preterm birth (2450g), short NICU stay for feeding support. |
| **Scenario C** | `P-SYN-003` | Vascular & Doppler Hemodynamic Decoupling | Abnormal 1st-trimester uterine artery Doppler (PI 2.25, bilateral notches) and low PlGF (24.5 pg/mL), predicted high vascular risk (0.68), persistent umbilical artery resistance, prophylactic aspirin 150mg, preterm cesarean (2080g), NICU admission. |
| **Scenario D** | `P-SYN-004` | Maternal Comorbid Risk Pattern | Chronic essential hypertension (MAP 108 mmHg) and Type 2 diabetes, high combined risk score (0.76), labetalol and aspirin regimens, planned cesarean at 36.5w (2550g), NICU hypoglycemia surveillance. |
| **Scenario E** | `P-SYN-005` | Preterm Delivery with Acute NICU Telemetry & Alerts | Normal early gestation followed by acute PPROM at 32w, very preterm birth (1620g), Level III NICU admission with Respiratory Distress Syndrome, 11 vital sign telemetry readings showing oxygen desaturation (SpO2 83%), Autoencoder anomaly score 0.94, high-severity alert triggered and acknowledged. |
| **Scenario F** | `P-SYN-006` | Active / Ongoing Pregnancy Cohort | Gestation currently active (EDD Feb 2027), 20-week anatomy scan normal, demonstrates graceful handling of ongoing cases with NULL delivery/newborn records. |

---

## 3. CSV Files Created & Record Counts

All 17 CSV files were generated in `data/synthetic/` with exact matching column names and data types corresponding to the MySQL database schema and SQLAlchemy models:

| # | CSV File Name | Target Table | Record Count | Number of Columns | Primary Key | Key Foreign Keys |
|---|---|---|---|---|---|---|
| 1 | `patients.csv` | `patients` | 6 | 7 | `id` (String) | — |
| 2 | `pregnancies.csv` | `pregnancies` | 6 | 9 | `id` (Int) | `patient_id` |
| 3 | `maternal_profiles.csv` | `maternal_profiles` | 6 | 9 | `id` (Int) | `pregnancy_id` |
| 4 | `fetal_assessments.csv` | `fetal_assessments` | 12 | 13 | `id` (Int) | `pregnancy_id` |
| 5 | `ultrasound_records.csv` | `ultrasound_records` | 12 | 10 | `id` (Int) | `pregnancy_id`, `assessment_id` |
| 6 | `lab_results.csv` | `lab_results` | 6 | 11 | `id` (Int) | `pregnancy_id`, `assessment_id` |
| 7 | `doppler_results.csv` | `doppler_results` | 12 | 11 | `id` (Int) | `pregnancy_id`, `assessment_id` |
| 8 | `predictions.csv` | `predictions` | 6 | 19 | `id` (Int) | `patient_id`, `pregnancy_id`, `assessment_id` |
| 9 | `growth_analysis.csv` | `growth_analysis` | 6 | 9 | `id` (Int) | `pregnancy_id` |
| 10 | `clinical_events.csv` | `clinical_events` | 10 | 7 | `id` (Int) | `patient_id`, `pregnancy_id` |
| 11 | `doctor_reviews.csv` | `doctor_reviews` | 8 | 10 | `id` (Int) | `patient_id`, `pregnancy_id` |
| 12 | `prescriptions.csv` | `prescriptions` | 4 | 10 | `id` (Int) | `patient_id`, `pregnancy_id` |
| 13 | `newborns.csv` | `newborns` | 5 | 9 | `id` (Int) | `pregnancy_id` |
| 14 | `nicu_admissions.csv` | `nicu_admissions` | 4 | 8 | `id` (Int) | `newborn_id` |
| 15 | `nicu_vitals.csv` | `nicu_vitals` | 26 | 9 | `id` (Int) | `nicu_admission_id` |
| 16 | `model_outputs.csv` | `model_outputs` | 6 | 13 | `id` (Int) | `patient_id`, `pregnancy_id`, `newborn_id`, `nicu_admission_id` |
| 17 | `alerts.csv` | `alerts` | 4 | 13 | `id` (Int) | `patient_id`, `newborn_id`, `nicu_admission_id` |
| **TOTAL** | **17 Files** | — | **139** | — | — | — |

---

## 4. Pre-Import Validation Results

The programmatic validation script ([`scripts/validate_synthetic_data.py`](file:///c:/project/neo_natal_watch_ai/scripts/validate_synthetic_data.py)) audited all 17 CSV files against 5 rigorous criteria:

1. **Column Names Matching**: **PASS** (100% exact column match against SQLAlchemy models without any missing or fabricated columns).
2. **Primary Key & Patient Code Uniqueness**: **PASS** (Zero duplicate primary keys; zero duplicate patient codes; zero ID collisions with existing MySQL data `TEST-PREDICT-01`).
3. **Foreign Key Referential Integrity**: **PASS** (100% of foreign keys resolve to valid parent records across the entire relational graph).
4. **Chronological Consistency**: **PASS** (All sequences strictly obey physiological timeline: Conception Date < T1 Assessment < T2 Assessment < Delivery < NICU Admission < NICU Vitals < Discharge Date).
5. **Data Types & Biometric Bounds**: **PASS** (Gestational ages, EFW percentiles, and neonatal telemetry values fall within physiologically plausible bounds).

**Overall Validation Status**: **PASS** (100% Clean). Detailed report saved at [`data/synthetic/validation_report.md`](file:///c:/project/neo_natal_watch_ai/data/synthetic/validation_report.md).

---

## 5. Synthetic Data Labeling & Academic Disclaimers

Every synthetic record and documentation file is explicitly identified as:
- **`source` / `source_dataset`**: Set to `"SYNTHETIC_DEMO"` in `fetal_assessments.csv`, `ultrasound_records.csv`, `lab_results.csv`, `doppler_results.csv`.
- **`model_version`**: Marked as `"v1.0-academic"` in predictions, growth analysis, model outputs, and alerts.
- **Documentation**: [`data/synthetic/synthetic_dataset_metadata.md`](file:///c:/project/neo_natal_watch_ai/data/synthetic/synthetic_dataset_metadata.md) prominently displays the warning:
  > **NOT REAL PATIENT DATA — FOR ACADEMIC / DEMONSTRATION USE ONLY — NOT FOR CLINICAL USE**

---

## 6. Safety Verification
- **MySQL database was NOT modified**: CONFIRMED. Row counts remain unchanged:
  - `patients`: 1 row (`TEST-PREDICT-01`)
  - `predictions`: 1 row
  - `vital_signs`: 60 rows
  - `chat_history`: 2 rows
  - All other tables: 0 rows
- **No DROP executed**: CONFIRMED.
- **No TRUNCATE executed**: CONFIRMED.
- **No DELETE executed**: CONFIRMED.
- **No ML models modified or retrained**: CONFIRMED.
- **Phase D (ML Audit) NOT started**: CONFIRMED.
- **Phase E (Data Import) NOT started**: CONFIRMED. All data remains staged in CSV files.

---

## 7. Files Created / Modified
- 17 CSV files under [`data/synthetic/`](file:///c:/project/neo_natal_watch_ai/data/synthetic/):
  - `patients.csv`, `pregnancies.csv`, `maternal_profiles.csv`, `fetal_assessments.csv`, `ultrasound_records.csv`, `lab_results.csv`, `doppler_results.csv`, `predictions.csv`, `growth_analysis.csv`, `clinical_events.csv`, `doctor_reviews.csv`, `prescriptions.csv`, `newborns.csv`, `nicu_admissions.csv`, `nicu_vitals.csv`, `model_outputs.csv`, `alerts.csv`
- [`data/synthetic/synthetic_dataset_metadata.md`](file:///c:/project/neo_natal_watch_ai/data/synthetic/synthetic_dataset_metadata.md) (Metadata, disclaimers, schema relationships)
- [`data/synthetic/synthetic_patients.md`](file:///c:/project/neo_natal_watch_ai/data/synthetic/synthetic_patients.md) (Detailed patient-by-patient clinical casebook)
- [`data/synthetic/validation_report.md`](file:///c:/project/neo_natal_watch_ai/data/synthetic/validation_report.md) (Programmatic validation audit report)
- [`scripts/generate_synthetic_data.py`](file:///c:/project/neo_natal_watch_ai/scripts/generate_synthetic_data.py) (Generator script)
- [`scripts/validate_synthetic_data.py`](file:///c:/project/neo_natal_watch_ai/scripts/validate_synthetic_data.py) (Validation script)
- [`phase_c_report.md`](file:///c:/project/neo_natal_watch_ai/phase_c_report.md) (Phase C summary report)
- `task.md` (Task tracker update)

