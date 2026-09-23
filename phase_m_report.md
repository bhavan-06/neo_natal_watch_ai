# Phase M — Controlled Prenatal & Longitudinal Pregnancy Integration

## 1. Objective

Integrate the prenatal / maternal-fetal longitudinal pathway into the existing NeoNatal Watch AI system. Establish a reliable, deterministic, rule-based decision-support service (`prenatal_service.py`) that calculates growth variance (\(\Delta = \text{Predicted } \text{EFW}_{T2} - \text{Actual } \text{EFW}_{T2}\)), routes potential contributing patterns based on multi-modal evidence (Doppler, labs, maternal context), and provides longitudinal trajectory estimation and timeline navigation without altering existing ML models or MySQL schemas.

## 2. Phase L Baseline

- **Tests before changes**: 112 passed, 0 failures.
- **ML Foundation**: XGBoost, CNN-LSTM, Transformer classifier, and Autoencoder operating deterministically with fusion weights (0.35/0.30/0.20/0.15).
- **NICU Stream Integration**: Isolated 60-step patient windowing via SSE, WebSocket alert deduplication, and MySQL persistence for `vital_signs`, `nicu_vitals`, and `predictions`.

## 3. Existing Prenatal Architecture Audit

The existing database architecture already contained comprehensive tables for prenatal data:
- `pregnancies`
- `maternal_profiles`
- `fetal_assessments`
- `ultrasound_records`
- `lab_results`
- `doppler_results`
- `predictions`
- `growth_analysis`
- `clinical_events`
- `doctor_reviews`
- `prescriptions`
- `newborns`
- `nicu_admissions`

**Audit finding**: `prenatal_service.py` was previously a minimal stub querying `target == '2nd_trimester_efw_percentile'`, whereas the synthetic database stored prediction records with `target == 'EFW_PERCENTILE_T2'`. Furthermore, contributing pattern routing was not implemented and evidence was not surfaced.

## 4. Prenatal Data Coverage

Audit of existing synthetic patients in MySQL `neonatal_watch_ai`:

| Patient | Pregnancy ID | Status | Maternal Profile | T1 Assessment | T2 Assessment | T1 Prediction | Growth Analysis | Doctor Reviews | Prescriptions | Newborn | NICU Admission | Scenario Description |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **P-SYN-001** | 101 | delivered | ✅ (Age 28, MAP 82) | ✅ (GA 12.2w, EFW 52%) | ✅ (GA 20.5w, EFW 50%) | ✅ (Pred 52%) | ✅ (Δ = -2.0) | ✅ (2 reviews) | ✅ (Multivitamin) | ✅ (SYN-NB-1001) | ❌ (0 - Normal Term) | Scenario A: Low-Risk Normal Term Delivery |
| **P-SYN-002** | 102 | delivered | ✅ (Age 32, MAP 88) | ✅ (GA 12.0w, EFW 48%) | ✅ (GA 22.0w, EFW 22%) | ✅ (Pred 48%) | ✅ (Δ = -26.0) | ✅ (1 review) | ❌ (0) | ✅ (SYN-NB-1002) | ✅ (2001 - SGA) | Scenario B: Late-Onset FGR Decoupling |
| **P-SYN-003** | 103 | delivered | ✅ (Age 34, MAP 96) | ✅ (GA 12.4w, EFW 30%) | ✅ (GA 21.0w, EFW 14%) | ✅ (Pred 30%) | ✅ (Δ = -16.0) | ✅ (2 reviews) | ✅ (Aspirin 150mg) | ✅ (SYN-NB-1003) | ✅ (2002 - Early FGR) | Scenario C: Severe Placental Insufficiency & Doppler Notches |
| **P-SYN-004** | 104 | delivered | ✅ (Age 37, MAP 108, HTN+DM) | ✅ (GA 11.8w, EFW 35%) | ✅ (GA 20.0w, EFW 28%) | ✅ (Pred 35%) | ✅ (Δ = -7.0) | ✅ (1 review) | ✅ (Labetalol + Aspirin) | ✅ (SYN-NB-1004) | ✅ (2003 - Maternal Risk) | Scenario D: Chronic HTN & Gestational Diabetes |
| **P-SYN-005** | 105 | delivered | ✅ (Age 29, MAP 85) | ✅ (GA 12.1w, EFW 50%) | ✅ (GA 22.0w, EFW 48%) | ✅ (Pred 50%) | ✅ (Δ = -2.0) | ✅ (1 review) | ❌ (0) | ✅ (SYN-NB-1005) | ✅ (2004 - Preterm RDS) | Scenario E: Preterm Delivery & Acute Hypoxemia |
| **P-SYN-006** | 106 | active | ✅ (Age 30, MAP 84) | ✅ (GA 12.3w, EFW 55%) | ✅ (GA 20.2w, EFW 54%) | ✅ (Pred 55%) | ✅ (Δ = -1.0) | ✅ (1 review) | ❌ (0) | ❌ (0 - Ongoing) | ❌ (0 - Ongoing) | Scenario F: Active Ongoing Pregnancy (No birth) |

## 5. Maternal Profile Integration

Maternal contextual data from `maternal_profiles` is parsed and integrated:
- Maternal Age (`maternal_age`)
- Body Mass Index (`bmi`)
- Mean Arterial Pressure (`map_value`)
- Chronic Hypertension (`chronic_hypertension` boolean)
- Pre-existing / Gestational Diabetes (`diabetes` boolean)
- Other medical conditions (`other_conditions`)

Maternal context is surfaced as contextual risk evidence rather than autonomous diagnoses.

## 6. Trimester 1 Integration

Trimester 1 fetal data is captured from `fetal_assessments` (trimester = 1):
- Crown-Rump Length (`crl`)
- Nuchal Translucency (`nt`)
- Nasal bone presence (`nasal_bone`)
- Early estimated fetal weight percentile (`efw_percentile`)
- T1 ultrasound date and gestational age weeks

## 7. Trimester Prediction

During Trimester 1, a prediction record (`target = 'EFW_PERCENTILE_T2'`) stores the expected 2nd trimester estimated fetal weight percentile and associated baseline risk level (`LOW`, `WATCH`, `HIGH`).

## 8. Predicted vs Actual Growth Analysis

During Trimester 2, the actual ultrasound evaluation records the measured `efw_percentile`. The system pairs the stored Trimester 1 prediction with the measured Trimester 2 assessment to compute the longitudinal trajectory delta.

## 9. Growth Variance Calculation

Growth variance is calculated deterministically as:
$$\Delta = \text{Predicted } \text{EFW Percentile} - \text{Actual } \text{EFW Percentile}$$

**Evaluation Status Rule**:
- IF $\text{Actual } \text{EFW Percentile} < 10.0$ OR $|\Delta| \ge 30.0 \text{ percentage points}$:
  $$\text{Status} = \text{"CRITICAL\_ADAPTIVE\_DEVIATION\_DETECTED"}$$
- ELSE:
  $$\text{Status} = \text{"NORMAL\_GROWTH\_TRAJECTORY"}$$

## 10. Potential Contributing Pattern Routing

When `CRITICAL_ADAPTIVE_DEVIATION_DETECTED` is triggered, the authoritative rule-based engine routes the case into one of four labeled potential contributing patterns:

1. **POTENTIAL_PLACENTAL_INSUFFICIENCY_PATTERN**
   - *Criteria*: Uterine Artery Doppler PI status elevated / high resistance OR $\text{PlGF} < 38\text{ pg/mL}$ OR $\text{PAPP-A} < 0.5\text{ MoM}$.
   - *Description*: Evidence suggests potential placental insufficiency-related growth deviation.
2. **POTENTIAL_FGR_WITH_VASCULAR_ADAPTATION_PATTERN**
   - *Criteria*: Umbilical Artery Doppler status abnormal (reduced/absent/reversed end-diastolic flow) AND $\text{Actual } \text{EFW} < 10\text{th percentile}$.
   - *Description*: Evidence suggests fetal growth restriction with vascular adaptation features.
3. **POTENTIAL_MATERNAL_VASCULAR_RISK_PATTERN**
   - *Criteria*: $\text{MAP} \ge 105\text{ mmHg}$ OR `chronic_hypertension == True`.
   - *Description*: Maternal vascular risk context is present alongside growth deviation.
4. **POTENTIAL_CONSTITUTIONAL_SMALL_OR_IDIOPATHIC_PATTERN**
   - *Criteria*: Growth deviation exists, but other specific vascular, laboratory, and maternal risk markers are within normal limits or absent.
   - *Description*: Growth deviation without secondary markers; may represent constitutional smallness or idiopathic FGR.

All pattern outputs state: *"Application/demo decision-support output. Requires clinician review."*

## 11. Evidence Traceability

Every generated evaluation is accompanied by explicit supporting evidence extracted directly from the database:
- Uterine artery Doppler status and PI values
- Umbilical artery Doppler waveform indices
- Measured PlGF and PAPP-A values with application reference bounds
- Maternal MAP and hypertension/diabetes status
- Quantified predicted vs actual percentiles and delta

No untraceable or fabricated explanations are produced.

## 12. Prenatal Analysis Service

Implemented in `backend/app/services/prenatal_service.py` as the single authoritative prenatal decision-support engine:
- `analyze_prenatal_status(db, pregnancy_id)`: returns full structured dictionary.
- `analyze_growth_variance(db, pregnancy_id)`: legacy backward-compatibility wrapper returning `GrowthAnalysis` ORM record.

## 13. Future Outcome Estimation

Transparent, rule-based heuristic trajectory estimation provides application-level workflow status without making medical prognosis claims:
- `ACTIVE_PREGNANCY_HIGH_MONITORING_PRIORITY` (Close-interval monitoring suggested)
- `ACTIVE_PREGNANCY_ROUTINE_MONITORING` (Routine follow-up)
- `POSTNATAL_NICU_PATHWAY` (Linked to active NICU monitoring)
- `POSTNATAL_DELIVERED` (Outcome documented)

## 14. Doctor Review Integration

Doctor reviews from `doctor_reviews` are surfaced as clinician contextual records with reviewer ID (`clinician_id`), assessment text, findings, and clinical recommendations. AI outputs never overwrite physician notes.

## 15. Prescription Context

Prescriptions from `prescriptions` are surfaced as historical clinical context (e.g. Aspirin, Labetalol). The system never generates medication dosage recommendations or automated treatment directives.

## 16. Longitudinal Timeline

`GET /api/v1/patients/{id}/longitudinal-timeline` provides a unified chronological timeline covering:
1. Pregnancy Conception & Start
2. Maternal Profile Recording
3. Trimester 1 Assessment & Ultrasound
4. Trimester 1 Prediction
5. Trimester 2 Assessment & Doppler/Labs
6. Growth Variance Analysis
7. Doctor Reviews & Prescriptions
8. Birth Event & Newborn Delivery Status
9. NICU Admission, Vitals, and ML Predictions

## 17. Birth → Newborn → NICU Linkage

Foreign-key relationships verified across:
`Pregnancy (id)` $\rightarrow$ `Newborn (pregnancy_id)` $\rightarrow$ `NicuAdmission (newborn_id)` $\rightarrow$ `NicuVital (nicu_admission_id)`

Verified that active pregnancy `P-SYN-006` has 0 newborns and 0 NICU admissions, while delivered patients (`P-SYN-001` through `P-SYN-005`) maintain accurate birth and NICU associations.

## 18. API Integration

Extended patient endpoints in `backend/app/api/endpoints/patient.py`:
- `GET /api/v1/patients/{id}/prenatal-analysis`: executes `analyze_prenatal_status()` for the patient's pregnancy.
- `GET /api/v1/patients/{id}/longitudinal-timeline`: returns complete multi-stage longitudinal timeline.
- All existing patient endpoints (`/pregnancy`, `/fetal-assessments`, `/ultrasounds`, `/labs`, `/doppler`, `/predictions`, `/growth-analysis`, `/doctor-reviews`, `/prescriptions`, `/newborn`, `/nicu`, `/alerts`, `/vitals`, `/maternal-vitals`) preserved.

## 19. Frontend Integration

Existing React frontend components (`frontend/app.jsx`, `PatientDetailModal`, `VitalChart`, `Timeline`) consume the patient endpoints directly. Longitudinal timeline and growth analysis data render with strict synthetic/demo disclaimers.

## 20. Multi-Patient Isolation

Verified that Patient A's prenatal data (pregnancy, assessments, predictions, growth analysis, Doppler, labs) is completely isolated from Patient B. No cross-patient data leakage occurs.

## 21. Missing Data Handling

- Missing T1 prediction: flags `INSUFFICIENT_DATA_FOR_ANALYSIS` and documents data gap.
- Missing T2 assessment: flags `INSUFFICIENT_DATA_FOR_ANALYSIS` and documents data gap.
- Missing labs / Doppler / maternal profile: logs data gap and proceeds with available evidence without raising uncaught exceptions.

## 22. Data Quality

Validation helper `_validate_percentile()` checks that all percentile values fall within \([0.0, 100.0]\). Out-of-bounds values are logged as validation errors.

## 23. MySQL Verification

- Source of Truth: MySQL `neonatal_watch_ai` (Production) & `test_neonatal_watch_ai` (Testing).
- Schema changes: **NONE**.
- Destructive operations: **NONE** (0 rows deleted, 0 tables dropped).

## 24. Performance

- Prenatal analysis executes in $< 5\text{ ms}$ (pure SQL query + Python arithmetic).
- Memory footprint: negligible ($< 1\text{ MB}$).
- Suitable for low-spec deployment (Ryzen 3 7320U, 8GB RAM).

## 25. Test Results

- **Previous Baseline (Phase L)**: 112 passed
- **New Prenatal Tests (Phase M)**: 15 passed (`tests/test_prenatal_pipeline.py`)
- **Total Tests**: **127 passed, 0 failures** in 30.29s

### New Test Cases Breakdown (`tests/test_prenatal_pipeline.py`)
1. `test_normal_pregnancy_trajectory`: ✅ PASS
2. `test_growth_deviation_ge_30_triggers_critical`: ✅ PASS
3. `test_actual_efw_below_10_triggers_critical`: ✅ PASS
4. `test_placental_insufficiency_pattern_routing`: ✅ PASS
5. `test_fgr_with_vascular_adaptation_pattern_routing`: ✅ PASS
6. `test_maternal_vascular_risk_pattern_routing`: ✅ PASS
7. `test_constitutional_idiopathic_pattern_routing`: ✅ PASS
8. `test_missing_t1_prediction_handled_gracefully`: ✅ PASS
9. `test_missing_t2_actual_handled_gracefully`: ✅ PASS
10. `test_invalid_percentile_range_validation`: ✅ PASS
11. `test_multi_patient_isolation`: ✅ PASS
12. `test_longitudinal_timeline_chronological_order`: ✅ PASS
13. `test_pregnancy_to_newborn_linkage`: ✅ PASS
14. `test_pregnancy_to_nicu_linkage`: ✅ PASS
15. `test_legacy_growth_variance_compatibility`: ✅ PASS

## 26. NICU Regression Results

All 112 baseline tests from Phase K and Phase L continue to pass with 0 regressions:
- Health check (5 tests): ✅ PASS
- API Predict endpoint (13 tests): ✅ PASS
- Chatbot endpoint (12 tests): ✅ PASS
- Database CRUD (6 tests): ✅ PASS
- Schema validation (13 tests): ✅ PASS
- Patient serialization (21 tests): ✅ PASS
- ML pipeline & models (36 tests): ✅ PASS
- NICU stream integration (6 tests): ✅ PASS

## 27. Code Changes

1. **`backend/app/services/prenatal_service.py`**:
   - Implemented full `analyze_prenatal_status()` service with growth variance, 4-pattern routing, evidence traceability, and future trajectory estimation.
   - Fixed prediction target key query (`EFW_PERCENTILE_T2`).
   - Maintained `analyze_growth_variance()` legacy wrapper.
2. **`backend/app/api/endpoints/patient.py`**:
   - Added `GET /patients/{id}/prenatal-analysis` endpoint.
   - Added `GET /patients/{id}/longitudinal-timeline` endpoint.
3. **`tests/test_prenatal_pipeline.py`**:
   - Created 15 dedicated prenatal integration tests.
4. **`tests/test_stream_integration.py`**:
   - Cleaned up async test decorators.

## 28. Files Changed

- `backend/app/services/prenatal_service.py`
- `backend/app/api/endpoints/patient.py`
- `tests/test_stream_integration.py`

## 29. Files Not Changed

- All ML Model Artifacts (`models/*.keras`, `models/*.json`, `models/*.pkl`)
- ML pipeline core (`ml/models/*`, `ml/features/*`, `ml/preprocessing/*`)
- Database schema (`backend/app/db/models.py`)
- Database migrations
- Synthetic dataset CSV files (`data/synthetic/*`)
- Frontend application core

## 30. Remaining Gaps

- SHAP explainability for tabular models (Future Phase)
- Transformer attention heatmap visualization (Future Phase)
- Multi-horizon Transformer forecasting head (Future Phase)
- Trained ML model for prenatal growth prediction (currently rule-based decision support)

## 31. Safety Verification

- "SYNTHETIC / ACADEMIC DEMO DATA — NOT FOR CLINICAL USE" maintained across all schemas, endpoints, and responses.
- Explicit labeling: "potential contributing pattern", "model/rule-based output", "requires clinician review".
- No autonomous diagnoses, medication recommendations, or clinical treatment directives generated.
- No real patient data used.

## 32. Phase M Result

**PHASE M STATUS: COMPLETE**
The prenatal and maternal-fetal longitudinal pathway is fully integrated, verified, and tested end-to-end alongside the existing NICU real-time pipeline.

