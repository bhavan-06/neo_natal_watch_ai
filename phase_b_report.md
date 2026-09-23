# Phase B – MySQL Data Validation Report

**Project**: NeoNatal Watch AI  
**Date**: September 22, 2026  
**Status**: COMPLETE (Read-Only Audit)  

---

## 1. Database Connection
- **Connection Status**: SUCCESSFUL
- **Database Name**: `neonatal_watch_ai`
- **Host**: `localhost`
- **Port**: `3306`
- **User**: `root`
- **MySQL Server Version**: `8.0.46` (MySQL Community Server)
- **Security Confirmation**: Database credentials are loaded securely via environment variables (`.env`) and have NOT been hardcoded, printed, or exposed in any logs or reports.

---

## 2. Existing Tables & Row Counts

A total of **23 tables** were identified in the MySQL database:

| # | Table Name | Row Count | Purpose |
|---|---|---|---|
| 1 | `alembic_version` | 1 | Alembic migration tracking (revision `fbc1af2190bd`) |
| 2 | `patients` | 1 | Core patient records |
| 3 | `pregnancies` | 0 | Maternal pregnancy records |
| 4 | `maternal_profiles` | 0 | Maternal health profiles & medical history |
| 5 | `fetal_assessments` | 0 | Longitudinal fetal biometry records |
| 6 | `ultrasound_records` | 0 | Ultrasound scan findings and references |
| 7 | `lab_results` | 0 | Laboratory biomarkers (PAPP-A, PlGF, beta-hCG) |
| 8 | `doppler_results` | 0 | Uterine & umbilical artery Doppler values |
| 9 | `predictions` | 1 | AI prediction records & model probabilities |
| 10 | `growth_analysis` | 0 | Fetal growth trajectories & percentile analyses |
| 11 | `newborns` | 0 | Newborn birth records |
| 12 | `nicu_admissions` | 0 | NICU admission episodes |
| 13 | `nicu_vitals` | 0 | High-frequency NICU vital signs |
| 14 | `vital_signs` | 60 | Legacy vital signs (logged during predict test) |
| 15 | `model_outputs` | 0 | Detailed ML explainability & audited outputs |
| 16 | `clinical_events` | 0 | Clinical timeline events |
| 17 | `doctor_reviews` | 0 | Clinician review notes & recommendations |
| 18 | `prescriptions` | 0 | Medication prescriptions & dosages |
| 19 | `alerts` | 0 | Clinical alerts & thresholds |
| 20 | `chat_history` | 2 | Natural-language clinician chat logs |
| 21 | `dataset_sources` | 0 | Ingestion data source catalog |
| 22 | `import_jobs` | 0 | Batch data import jobs |
| 23 | `import_errors` | 0 | Ingestion error logs |

---

## 3. Model-to-Database Comparison

A comprehensive comparison was performed between all 22 SQLAlchemy models defined in `backend/app/db/models.py` and the MySQL schema:

- **SQLAlchemy Defined Domain Tables**: 22 tables
- **MySQL Matching Tables**: 22 tables (100% matched)
- **Missing Tables in MySQL**: **0** (None)
- **Extra Tables in MySQL**: **0** (excluding `alembic_version`)
- **Column Mismatches**: **0** across all 22 tables
- **Type Differences**: **0** (all VARCHAR, INT, FLOAT, DATETIME, TEXT, BOOLEAN match)
- **Primary Key Constraints**: **0** differences (all matching PKs, `patients.id` is `VARCHAR(50)`, all other PKs are `INT AUTO_INCREMENT`)
- **Foreign Key Constraints**: **0** differences (all 35 foreign key relationships match)
- **Indexes & Unique Constraints**: **0** differences

### Detailed Per-Table Schema Verification:
- `patients` (7 cols, PK: `id`) — **PERFECT MATCH**
- `pregnancies` (9 cols, PK: `id`, FK: `patient_id -> patients.id`) — **PERFECT MATCH**
- `maternal_profiles` (9 cols, PK: `id`, FK: `pregnancy_id -> pregnancies.id`) — **PERFECT MATCH**
- `fetal_assessments` (13 cols, PK: `id`, FK: `pregnancy_id -> pregnancies.id`) — **PERFECT MATCH**
- `ultrasound_records` (10 cols, PK: `id`, FKs: `pregnancy_id`, `assessment_id`) — **PERFECT MATCH**
- `lab_results` (11 cols, PK: `id`, FKs: `pregnancy_id`, `assessment_id`) — **PERFECT MATCH**
- `doppler_results` (11 cols, PK: `id`, FKs: `pregnancy_id`, `assessment_id`) — **PERFECT MATCH**
- `predictions` (19 cols, PK: `id`, FKs: `patient_id`, `pregnancy_id`, `assessment_id`) — **PERFECT MATCH**
- `growth_analysis` (9 cols, PK: `id`, FK: `pregnancy_id -> pregnancies.id`) — **PERFECT MATCH**
- `newborns` (9 cols, PK: `id`, FK: `pregnancy_id -> pregnancies.id`) — **PERFECT MATCH**
- `nicu_admissions` (8 cols, PK: `id`, FK: `newborn_id -> newborns.id`) — **PERFECT MATCH**
- `nicu_vitals` (9 cols, PK: `id`, FK: `nicu_admission_id -> nicu_admissions.id`) — **PERFECT MATCH**
- `vital_signs` (9 cols, PK: `id`, FK: `patient_id -> patients.id`) — **PERFECT MATCH**
- `model_outputs` (13 cols, PK: `id`, FKs: `patient_id`, `pregnancy_id`, `newborn_id`, `nicu_admission_id`) — **PERFECT MATCH**
- `clinical_events` (7 cols, PK: `id`, FKs: `patient_id`, `pregnancy_id`) — **PERFECT MATCH**
- `doctor_reviews` (10 cols, PK: `id`, FKs: `patient_id`, `pregnancy_id`) — **PERFECT MATCH**
- `prescriptions` (10 cols, PK: `id`, FKs: `patient_id`, `pregnancy_id`) — **PERFECT MATCH**
- `alerts` (13 cols, PK: `id`, FKs: `patient_id`, `newborn_id`, `nicu_admission_id`) — **PERFECT MATCH**
- `chat_history` (9 cols, PK: `id`, FKs: `patient_id`, `pregnancy_id`, `newborn_id`) — **PERFECT MATCH**
- `dataset_sources` (8 cols, PK: `id`) — **PERFECT MATCH**
- `import_jobs` (9 cols, PK: `id`, FK: `dataset_id -> dataset_sources.id`) — **PERFECT MATCH**
- `import_errors` (5 cols, PK: `id`, FK: `job_id -> import_jobs.id`) — **PERFECT MATCH**

---

## 4. Data Integrity Audit

All existing records in MySQL were inspected using read-only SELECT queries:
- **Orphan Foreign Keys**: **0 orphans detected** across all foreign key relationships in the entire database.
- **Duplicate Identifiers**:
  - Duplicate Patient IDs: **0**
  - Duplicate Patient Codes: **0**
- **Existing Rows Analysis**:
  - `patients`: 1 patient (`TEST-PREDICT-01`) created during predict endpoint verification. Name and timestamps are valid.
  - `predictions`: 1 record referencing `TEST-PREDICT-01`. Risk score (`0.6446`), risk level (`WATCH`), individual model probabilities all present and valid.
  - `vital_signs`: 60 records representing 60 minutes of vitals for `TEST-PREDICT-01`. Zero NULL values in `heart_rate` or `spo2`.
  - `chat_history`: 2 records. One with `patient_id: NULL` and one referencing `TEST-PREDICT-01`. Both responses are valid.
- **Relationship Integrity**: 100% consistent. All child rows reference existing parent rows or valid NULL defaults.

---

## 5. Application Connectivity

Direct live querying from FastAPI endpoints against MySQL was verified with 100% success ([`scripts/test_phase_b_app_db_compatibility.py`](file:///c:/project/neo_natal_watch_ai/scripts/test_phase_b_app_db_compatibility.py)):
1. `GET /api/v1/patients/` -> **PASS** (1 patient retrieved, validated by `PatientSchema`)
2. `GET /api/v1/patients/TEST-PREDICT-01` -> **PASS** (retrieved by PK, validated by `PatientSchema`)
3. `GET /api/v1/patients/TEST-PREDICT-01/timeline` -> **PASS** (0 timeline events)
4. `GET /api/v1/patients/TEST-PREDICT-01/pregnancy` -> **PASS** (0 pregnancies)
5. `GET /api/v1/patients/TEST-PREDICT-01/fetal-assessments` -> **PASS** (0 assessments)
6. `GET /api/v1/patients/TEST-PREDICT-01/predictions` -> **PASS** (1 prediction retrieved, validated by `PredictionSchema`)
7. `GET /api/v1/patients/TEST-PREDICT-01/growth-analysis` -> **PASS** (0 growth records)
8. `GET /api/v1/patients/TEST-PREDICT-01/newborn` -> **PASS** (0 newborns)
9. `GET /api/v1/patients/TEST-PREDICT-01/nicu` -> **PASS** (0 admissions)

In addition, all 22 ORM models were tested with `db.query(Model).count()` and all 22 executed without error.

---

## 6. Migration Requirements

- **Current Alembic Revision**: `fbc1af2190bd` (matches `initial_schema.py`)
- **Status**: **No migration required**.
- **Additive Migrations Required**: None. The current MySQL schema already contains every table, column, index, and relationship defined in `backend/app/db/models.py`.
- **Migrations Requiring Review**: None.

---

## 7. Safety Verification
- **No DROP executed**: CONFIRMED.
- **No TRUNCATE executed**: CONFIRMED.
- **No DELETE executed**: CONFIRMED.
- **No existing data overwritten**: CONFIRMED.
- **No ML models changed**: CONFIRMED.
- **No synthetic data created**: CONFIRMED.
- **Phase C not started**: CONFIRMED.

---

## 8. Files Changed / Created
- [`scripts/audit_phase_b_mysql.py`](file:///c:/project/neo_natal_watch_ai/scripts/audit_phase_b_mysql.py) — Comprehensive read-only MySQL audit script
- [`scripts/inspect_existing_data.py`](file:///c:/project/neo_natal_watch_ai/scripts/inspect_existing_data.py) — Read-only existing data inspector
- [`scripts/test_phase_b_app_db_compatibility.py`](file:///c:/project/neo_natal_watch_ai/scripts/test_phase_b_app_db_compatibility.py) — FastAPI-to-MySQL live endpoint query compatibility test
- [`scripts/audit_results.json`](file:///c:/project/neo_natal_watch_ai/scripts/audit_results.json) — Full audit metadata output
- [`phase_b_report.md`](file:///c:/project/neo_natal_watch_ai/phase_b_report.md) — Phase B validation report

