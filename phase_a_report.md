# Phase A Report — API Serialization & Schema Architecture

**Project**: NeoNatal Watch AI  
**Date**: September 22, 2026  
**Status**: COMPLETE  

---

## 1. Executive Summary

Phase A focused entirely on establishing a clean, type-safe API serialization layer for all domain objects in the system using **Pydantic v2**. 

All 21 SQLAlchemy models existing in `backend/app/db/models.py` were inspected, corresponding Pydantic v2 schemas were defined under `backend/app/schemas/`, and all applicable REST endpoints under `backend/app/api/endpoints/patient.py` were updated with explicit `response_model` annotations.

No database tables or schemas were modified, no existing frontend code was broken, and no existing API routes were removed or renamed.

---

## 2. Models Discovered in `backend/app/db/models.py`

A thorough inspection of `backend/app/db/models.py` identified **21 SQLAlchemy domain models**:

| # | Model Name | Primary Key | Description / Relationships |
|---|---|---|---|
| 1 | `Patient` | `id: String(50)` | Core patient record (pregnancies, vitals, predictions, clinical events, alerts) |
| 2 | `Pregnancy` | `id: Integer` | Maternal pregnancy episode (fetal assessments, growth analysis, newborns) |
| 3 | `MaternalProfile` | `id: Integer` | Maternal health history, risk factors, chronic hypertension, diabetes |
| 4 | `FetalAssessment` | `id: Integer` | Longitudinal fetal biometrics (EFW, CRL, NT, biometry percentiles) |
| 5 | `UltrasoundRecord` | `id: Integer` | Ultrasound scan imaging reference, findings, metadata |
| 6 | `LabResult` | `id: Integer` | Biomarkers (PAPP-A, PlGF, free beta-hCG, test dates) |
| 7 | `DopplerResult` | `id: Integer` | Uterine/umbilical artery pulsatility index and Doppler status |
| 8 | `Prediction` | `id: Integer` | Longitudinal AI predictions, risk scores, ensemble model scores |
| 9 | `GrowthAnalysis` | `id: Integer` | Predicted vs actual EFW percentiles, growth variance analysis |
| 10 | `Newborn` | `id: Integer` | Birth outcome, birth weight, gestational age at birth |
| 11 | `NicuAdmission` | `id: Integer` | NICU admission episodes, admission reason, discharge date |
| 12 | `NicuVital` | `id: Integer` | High-frequency NICU vitals (HR, SpO2, RR, temperature) |
| 13 | `VitalSign` | `id: Integer` | Legacy vital signs table (HR, SpO2, RR, Temp, SBP, DBP) |
| 14 | `ModelOutput` | `id: Integer` | Audited model outputs, confidence, explanation references |
| 15 | `ClinicalEvent` | `id: Integer` | Longitudinal timeline clinical events and findings |
| 16 | `DoctorReview` | `id: Integer` | Clinician reviews, clinical assessments, recommendations |
| 17 | `Prescription` | `id: Integer` | Prescribed medications, dosages, administration schedule |
| 18 | `Alert` | `id: Integer` | Clinical alerts, severity, triggering factors, acknowledgment |
| 19 | `ChatHistory` | `id: Integer` | Clinician chatbot interaction history |
| 20 | `DatasetSource` | `id: Integer` | Metadata for external/imported datasets |
| 21 | `ImportJob` / `ImportErrorLog` | `id: Integer` | Ingestion job tracking and row-level error audit logs |

---

## 3. Pydantic Schemas Created / Configured

All schemas are located under `backend/app/schemas/` and utilize Pydantic v2 `ConfigDict(from_attributes=True)`:

| Schema Name | File Location | Key Fields & Types |
|---|---|---|
| `PatientSchema` | `backend/app/schemas/patient.py` | `id: str`, `patient_code`, `name`, `date_of_birth`, `contact_info`, timestamps |
| `MaternalProfileSchema` | `backend/app/schemas/maternal_profile.py` | `id: int`, `pregnancy_id`, `maternal_age`, `bmi`, `map_value`, `chronic_hypertension`, `diabetes` |
| `PregnancySchema` | `backend/app/schemas/pregnancy.py` | `id: int`, `patient_id: str`, `pregnancy_code`, `pregnancy_status`, `conception_date`, `estimated_due_date` |
| `FetalAssessmentSchema` | `backend/app/schemas/fetal_assessment.py` | `id: int`, `pregnancy_id: int`, `gestational_age_weeks`, `trimester`, `crl`, `nt`, `efw`, `efw_percentile` |
| `UltrasoundRecordSchema` | `backend/app/schemas/ultrasound_record.py` | `id: int`, `pregnancy_id`, `assessment_id`, `ultrasound_date`, `gestational_age`, `findings` |
| `LabResultSchema` | `backend/app/schemas/lab_result.py` | `id: int`, `pregnancy_id`, `assessment_id`, `papp_a`, `plgf`, `free_beta_hcg`, `status` |
| `DopplerResultSchema` | `backend/app/schemas/doppler_result.py` | `id: int`, `pregnancy_id`, `assessment_id`, `uterine_artery_pi`, `uterine_artery_status` |
| `PredictionSchema` | `backend/app/schemas/prediction.py` | `id: int`, `patient_id`, `prediction_type`, `predicted_value`, `risk_score`, `risk_level`, ensemble scores |
| `GrowthAnalysisSchema` | `backend/app/schemas/growth_analysis.py` | `id: int`, `pregnancy_id`, `predicted_efw_percentile`, `actual_efw_percentile`, `growth_variance` |
| `NewbornSchema` | `backend/app/schemas/newborn.py` | `id: int`, `pregnancy_id`, `newborn_code`, `birth_date`, `birth_weight`, `birth_length` |
| `NicuAdmissionSchema` | `backend/app/schemas/nicu_admission.py` | `id: int`, `newborn_id`, `admission_date`, `discharge_date`, `admission_reason`, `status` |
| `NicuVitalSchema` | `backend/app/schemas/nicu_vital.py` | `id: int`, `nicu_admission_id`, `heart_rate`, `spo2`, `respiratory_rate`, `temperature` |
| `VitalSignSchema` | `backend/app/schemas/vital_sign.py` | `id: int`, `patient_id`, `heart_rate`, `spo2`, `respiratory_rate`, `temperature`, `systolic_bp`, `diastolic_bp` |
| `ModelOutputSchema` | `backend/app/schemas/model_output.py` | `id: int`, `patient_id`, `model_name`, `model_version`, `output_type`, `output_value`, `confidence` |
| `ClinicalEventSchema` | `backend/app/schemas/clinical_event.py` | `id: int`, `patient_id`, `pregnancy_id`, `event_type`, `event_date`, `details` |
| `DoctorReviewSchema` | `backend/app/schemas/doctor_review.py` | `id: int`, `patient_id`, `pregnancy_id`, `clinician_id`, `findings`, `assessment`, `recommendations` |
| `PrescriptionSchema` | `backend/app/schemas/prescription.py` | `id: int`, `patient_id`, `medication_name`, `dosage`, `start_date`, `end_date` |
| `AlertSchema` | `backend/app/schemas/alert.py` | `id: int`, `patient_id`, `alert_type`, `severity`, `risk_score`, `status` |
| `ChatHistorySchema` | `backend/app/schemas/chat_history.py` | `id: int`, `patient_id`, `user_role`, `question`, `response`, `model_used` |
| `TimelineEntrySchema` | `backend/app/schemas/timeline.py` | `date: Optional[datetime]`, `type: str`, `details: Optional[str]` |
| `DatasetSourceSchema` / `ImportJobSchema` | `backend/app/schemas/dataset_source.py` | Ingestion and error log audit schemas |
| `PredictionRequest` / `PredictionResponse` | `backend/app/schemas/predict_schema.py` | Pre-existing schemas preserved for ML inference endpoint |

All schemas are exported via `backend/app/schemas/__init__.py`.

---

## 4. Endpoints Updated with `response_model`

In `backend/app/api/endpoints/patient.py`:

| Endpoint | Method | Response Model | Description |
|---|---|---|---|
| `/api/v1/patients/` | GET | `List[PatientSchema]` | Paginated/limited list of patients |
| `/api/v1/patients/{id}` | GET | `PatientSchema` | Single patient details; returns 404 if missing |
| `/api/v1/patients/{id}/timeline` | GET | `List[TimelineEntrySchema]` | Aggregated clinical events and alerts ordered by date |
| `/api/v1/patients/{id}/pregnancy` | GET | `List[PregnancySchema]` | Pregnancy episodes for patient |
| `/api/v1/patients/{id}/fetal-assessments` | GET | `List[FetalAssessmentSchema]` | Fetal biometric records for patient's pregnancies |
| `/api/v1/patients/{id}/predictions` | GET | `List[PredictionSchema]` | Historical AI predictions for patient |
| `/api/v1/patients/{id}/growth-analysis` | GET | `List[GrowthAnalysisSchema]` | Fetal growth analyses for patient's pregnancies |
| `/api/v1/patients/{id}/newborn` | GET | `List[NewbornSchema]` | Newborn outcomes for patient |
| `/api/v1/patients/{id}/nicu` | GET | `List[NicuAdmissionSchema]` | NICU admissions across patient's newborns |

Existing endpoints verified (no changes required):
- `POST /api/v1/predict/` — already typed with `response_model=PredictionResponse`
- `POST /api/v1/chat/` — already typed with `response_model=ChatResponse`
- `GET /api/v1/stream/` — SSE StreamingResponse
- `POST /api/v1/data/import` — file upload endpoint
- `WS /ws/alerts` — WebSocket alert streaming

---

## 5. Serialization and Lazy-Loading Safety

- **Relationship Isolation**: Relationship fields (e.g. `pregnancies`, `fetal_assessments`) were intentionally excluded from flat response schemas. This guarantees that returning an ORM instance never triggers unexpected N+1 lazy-loading cascades or circular serialization loops.
- **Datetime Handling**: All datetime fields are typed as `Optional[datetime]` to enable ISO-8601 formatting by FastAPI/Pydantic automatically.
- **Nullable Handling**: All nullable columns have explicit defaults (`= None`) to prevent `ValidationError` on sparse or partial records.
- **Foreign Key Safety**: In `backend/app/api/endpoints/chatbot.py`, a foreign key existence check was added so that natural-language queries for unpersisted patient IDs do not trigger MySQL foreign-key constraint violations.

---

## 6. Verification and Test Results

### Automated Pytest Suite
Ran the entire test suite including 49 pre-existing tests + 21 newly created Phase A integration tests:
- **Total Tests Collected**: 70
- **Total Tests Passed**: 70 (100%)
- **Total Tests Failed**: 0

### Live Backend Verification (`scripts/verify_phase_a.py`)
Tested via `httpx.AsyncClient` with `ASGITransport` against the running FastAPI application:
1. `GET /` (Health check) -> **PASS** (HTTP 200, status="online")
2. `GET /api/v1/patients/` (List) -> **PASS** (HTTP 200, count=0)
3. `GET /api/v1/patients/NON_EXISTENT_ID` -> **PASS** (HTTP 404, detail="Patient not found")
4. `GET /api/v1/patients/NON_EXISTENT_ID/timeline` -> **PASS** (HTTP 404)
5. `GET /api/v1/patients/NON_EXISTENT_ID/pregnancy` -> **PASS** (HTTP 200, body=[])
6. `GET /api/v1/patients/NON_EXISTENT_ID/fetal-assessments` -> **PASS** (HTTP 200, body=[])
7. `GET /api/v1/patients/NON_EXISTENT_ID/predictions` -> **PASS** (HTTP 200, body=[])
8. `GET /api/v1/patients/NON_EXISTENT_ID/growth-analysis` -> **PASS** (HTTP 200, body=[])
9. `GET /api/v1/patients/NON_EXISTENT_ID/newborn` -> **PASS** (HTTP 200, body=[])
10. `GET /api/v1/patients/NON_EXISTENT_ID/nicu` -> **PASS** (HTTP 200, body=[])
11. `POST /api/v1/predict/` -> **PASS** (HTTP 200, risk=0.6446, level="WATCH")
12. `POST /api/v1/chat/` -> **PASS** (HTTP 200, reply returned)

**Result**: 12/12 endpoints verified successfully (100%).

---

## 7. Files Changed / Created

### Schemas Created (`backend/app/schemas/`)
- `patient.py`
- `maternal_profile.py`
- `pregnancy.py`
- `fetal_assessment.py`
- `ultrasound_record.py`
- `lab_result.py`
- `doppler_result.py`
- `prediction.py`
- `growth_analysis.py`
- `newborn.py`
- `nicu_admission.py`
- `nicu_vital.py`
- `vital_sign.py`
- `model_output.py`
- `clinical_event.py`
- `doctor_review.py`
- `prescription.py`
- `alert.py`
- `chat_history.py`
- `timeline.py`
- `dataset_source.py`
- `__init__.py`

### Endpoints Updated
- `backend/app/api/endpoints/patient.py` (added response_model annotations for all 9 GET endpoints)
- `backend/app/api/endpoints/chatbot.py` (safely handled patient existence check before saving chat history)

### Tests & Verification Scripts Created
- `tests/test_patient_endpoints.py` (21 test cases for patient endpoints & schemas)
- `scripts/verify_phase_a.py` (live 12-endpoint httpx verification script)

---

## 8. Remaining Issues
None. Phase A serialization and verification is complete.

---

## 9. Next Steps
Awaiting user approval before proceeding to **Phase B — MySQL Data Validation**.

