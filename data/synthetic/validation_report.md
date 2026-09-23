# Synthetic Dataset Pre-Import Validation Report

**Dataset**: Academic Demonstration Dataset v1.0  
**Validation Date**: 2026-09-22 22:51:52  
**Overall Validation Result**: **PASS**  

---

## 1. Validation Checklist

| Category | Status | Notes |
|---|---|---|
| **Column Names Matching** | **PASS** | 100% exact match against SQLAlchemy `Base.metadata.tables` across all 17 CSV files. |
| **Primary Key & Patient Code Uniqueness** | **PASS** | Zero duplicate IDs; zero collisions with existing MySQL records (`TEST-PREDICT-01`). |
| **Foreign Key Referential Integrity** | **PASS** | 100% of foreign keys resolve to valid parents across the relational graph. |
| **Chronological Consistency** | **PASS** | Strict ordering verified: Conception < T1 Scan < T2 Scan < Delivery < NICU Admission < Discharge. |
| **Data Types & Biometric Bounds** | **PASS** | All gestational ages, EFW percentiles, and neonatal vitals within plausible physiological bounds. |

---

## 2. File-by-File Record Counts

| File Name | Record Count | Target Database Table | Primary Key | Key Foreign Keys |
|---|---|---|---|---|
| `patients.csv` | 6 | `patients` | `id` (String) | — |
| `pregnancies.csv` | 6 | `pregnancies` | `id` (Int) | `patient_id` |
| `maternal_profiles.csv` | 6 | `maternal_profiles` | `id` (Int) | `pregnancy_id` |
| `fetal_assessments.csv` | 12 | `fetal_assessments` | `id` (Int) | `pregnancy_id` |
| `ultrasound_records.csv` | 12 | `ultrasound_records` | `id` (Int) | `pregnancy_id`, `assessment_id` |
| `lab_results.csv` | 6 | `lab_results` | `id` (Int) | `pregnancy_id`, `assessment_id` |
| `doppler_results.csv` | 12 | `doppler_results` | `id` (Int) | `pregnancy_id`, `assessment_id` |
| `predictions.csv` | 6 | `predictions` | `id` (Int) | `patient_id`, `pregnancy_id`, `assessment_id` |
| `growth_analysis.csv` | 6 | `growth_analysis` | `id` (Int) | `pregnancy_id` |
| `clinical_events.csv` | 10 | `clinical_events` | `id` (Int) | `patient_id`, `pregnancy_id` |
| `doctor_reviews.csv` | 8 | `doctor_reviews` | `id` (Int) | `patient_id`, `pregnancy_id` |
| `prescriptions.csv` | 4 | `prescriptions` | `id` (Int) | `patient_id`, `pregnancy_id` |
| `newborns.csv` | 5 | `newborns` | `id` (Int) | `pregnancy_id` |
| `nicu_admissions.csv` | 4 | `nicu_admissions` | `id` (Int) | `newborn_id` |
| `nicu_vitals.csv` | 26 | `nicu_vitals` | `id` (Int) | `nicu_admission_id` |
| `model_outputs.csv` | 6 | `model_outputs` | `id` (Int) | `patient_id`, `pregnancy_id`, `newborn_id`, `nicu_admission_id` |
| `alerts.csv` | 4 | `alerts` | `id` (Int) | `patient_id`, `newborn_id`, `nicu_admission_id` |
| **TOTAL** | **139** | — | — | — |

---

## 3. Discovered Anomalies & Resolutions
- **None**. All foreign key relationships, chronological sequences, and data constraints passed validation on initial audit.
- **Safety Guarantee**: No records have been written to the live MySQL database. Files remain staged in `data/synthetic/` awaiting Phase E.
