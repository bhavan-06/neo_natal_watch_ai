# Phase K — Controlled ML Foundation & Existing Model Integration

## 1. Objective

Verify that the existing ML inference foundation in NeoNatal Watch AI is reliable, correctly wired, and produces valid outputs end-to-end — from raw vital sign input through preprocessing, feature engineering, model inference, fusion, risk classification, API response, MySQL persistence, and frontend display — before any advanced ML features are implemented in later phases.

## 2. Phase I/J Findings Used

From **Phase I** (ML Architecture Audit):
- XGBoost, CNN-LSTM, Transformer (classifier), and Autoencoder are all implemented and connected to the Fusion model.
- SHAP explainability is missing (empty `ml/explainability/` directory).
- Transformer attention weights are not extracted.
- NICU stream does not trigger inference.
- Prenatal growth analysis is rule-based, not ML-driven.
- All model artifacts are present and total < 2 MiB.
- Hardware optimizations are in place (batch_size=1, TF threads capped at 4).

From **Phase J** (ML Integration Plan):
- P0 priorities: XGBoost verification, fusion stability, alert broadcasting.
- P1 priorities: NICU real-time inference trigger, prenatal validation.
- P2–P4: SHAP, attention extraction, forecasting — deferred to later phases.
- No schema changes required for current architecture.

## 3. Baseline Before Changes

| Metric | Value |
|--------|-------|
| Existing test suite | 70 tests |
| Test result | 70 passed, 0 failures |
| Test database | MySQL `test_neonatal_watch_ai` |
| Production database | MySQL `neonatal_watch_ai` |
| Model artifacts | 8 files in `models/` directory |
| Known TF issue | `set_intra_op_parallelism_threads` crashes when TF context already initialized |

## 4. Model Artifact Verification

| Artifact | Path | Size | Framework | Expected Input | Output | Loading | Status |
|----------|------|------|-----------|---------------|--------|---------|--------|
| XGBoost Classifier | `models/xgboost_model.json` | 81,365 B | xgboost | 102 tabular features | `predict_proba[:, 1]` → [0, 1] | `xgb.XGBClassifier().load_model()` | ✅ PASS |
| CNN-LSTM | `models/cnn_lstm.keras` | 585,277 B | TensorFlow/Keras | (1, 30, 6) float32 | (1, 1) sigmoid | `tf.keras.models.load_model(compile=False)` | ✅ PASS |
| Transformer | `models/transformer.keras` | 1,278,198 B | TensorFlow/Keras | (1, 30, 6) float32 | (1, 1) sigmoid | `tf.keras.models.load_model(compile=False)` | ✅ PASS |
| Autoencoder | `models/autoencoder.keras` | 112,767 B | TensorFlow/Keras | (1, 30, 6) float32 | (1, 30, 6) reconstruction | `tf.keras.models.load_model(compile=False)` | ✅ PASS |
| MinMax Scaler | `models/scaler.pkl` | 1,239 B | scikit-learn | 6 vital columns | Scaled [0, 1] | `joblib.load()` | ✅ PASS |
| XGBoost Features | `models/xgb_features.json` | 2,324 B | JSON | — | List of 102 feature names | `json.load()` | ✅ PASS |
| AE Threshold | `models/ae_threshold.json` | 43 B | JSON | — | `{"anomaly_threshold": 0.004240}` | `json.load()` | ✅ PASS |
| .gitkeep | `models/.gitkeep` | 0 B | — | — | — | — | N/A |

All 7 ML artifacts loaded successfully. No artifacts are missing or corrupt.

## 5. XGBoost Verification

- **Model**: `xgb.XGBClassifier` binary classifier.
- **Feature ordering**: 102 features defined in `xgb_features.json` — 6 raw vitals + 6 missing flags + 72 rolling stats (mean/std/min/max × 6 vitals × 3 windows) + 18 rate-of-change (diff × 6 vitals × 3 windows).
- **Scaler usage**: XGBoost operates on *unscaled* engineered features. The MinMax scaler is used only for the deep learning sequence input.
- **Inference**: `model.predict_proba(X)[:, 1]` returns class-1 probability in [0, 1].
- **Risk-score conversion**: XGBoost probability contributes 35% to the fused score via weighted average.
- **Error handling**: If any required feature column is missing, a `KeyError` is raised (expected behavior — the inference service always provides all 102 features).
- **Test result**: `test_xgboost_predict_proba` — ✅ PASS. Output shape (1, 2), probability in valid range.

## 6. CNN-LSTM Verification

- **Architecture**: Conv1D(32) → BatchNorm → MaxPool → Conv1D(64) → BatchNorm → MaxPool → LSTM(64) → BatchNorm → Dropout → Dense(32) → Dense(1, sigmoid).
- **Input shape**: (1, 30, 6) — 30-minute window of 6 scaled vital signs.
- **Sequence construction**: Last 30 rows of input, scaled via `scaler.transform()`, expanded to 3D.
- **Output shape**: (1, 1) — single sigmoid probability.
- **Test result**: `test_cnn_lstm_inference` — ✅ PASS. Score in [0, 1].

## 7. Transformer Verification

- **Architecture**: Conv1D projection → Learnable positional embedding → 2× MultiHeadAttention(4 heads, size 32) → GlobalAveragePooling1D → Dense(64) → Dense(32) → Dense(1, sigmoid).
- **Current function**: Binary classifier (deterioration probability). NOT multi-horizon forecaster.
- **Input shape**: (1, 30, 6) — same as CNN-LSTM.
- **Output shape**: (1, 1) — single sigmoid probability.
- **Attention extraction**: Not implemented (`return_attention_scores=False` by default in Keras MultiHeadAttention). Deferred to future phase.
- **Test result**: `test_transformer_inference` — ✅ PASS. Score in [0, 1].

## 8. Autoencoder Verification

- **Architecture**: Conv1D(32) → MaxPool → Conv1D(16) → MaxPool (bottleneck) → Conv1D(16) → UpSample → Conv1D(32) → UpSample → Cropping1D → Conv1D(6, linear).
- **Input/Output shape**: (1, 30, 6) → (1, 30, 6) reconstruction.
- **Anomaly score**: Reconstruction MSE → pseudo-probability via `clip(0.5 × (MSE / threshold), 0, 1)`.
- **Threshold**: 0.004240 (95th percentile of validation normal-sample MSE), loaded from `ae_threshold.json`.
- **Threshold usage**: Verified — `ae_threshold.json` is loaded in `FusionModel._load_models()` and used in `predict_risk()`.
- **Anomaly scores in synthetic data**: The synthetic dataset contains `ae_score` values that were written by actual inference calls via `/predict` — they are NOT placeholder values.
- **Test results**: `test_autoencoder_inference` ✅, `test_autoencoder_anomaly_score` ✅. Reconstruction shape matches input, pseudo-probability in [0, 1].

## 9. Feature Engineering Verification

**Pipeline trace:**

```
Raw vital signs (60 records)
  ↓
inference_service.predict():
  ↓ pd.DataFrame conversion
  ↓ timestamp parsing & sorting
  ↓ Add 6 binary missing-value flags (_was_missing columns)
  ↓
engineer_features(df, window_sizes=[15, 30, 60]):
  ↓ sort by [patient_id, timestamp]
  ↓ add_rolling_statistics() → 72 columns (mean/std/min/max × 6 vitals × 3 windows)
  ↓ add_rate_of_change() → 18 columns (diff × 6 vitals × 3 windows)
  ↓ fillna(0) safety fallback
  ↓ Total: 8 original + 6 flags + 90 engineered = 104 columns
  ↓
flat_input = df_features.iloc[-1:] → 102 XGBoost features
```

**Feature ordering**: Verified that `engineer_features(df, window_sizes=[15, 30, 60])` produces all 102 features required by `xgb_features.json`.

**Critical finding**: The default parameter in `features.py` is `window_sizes=[15, 60]` (missing 30). However, the inference service always passes `window_sizes=[15, 30, 60]` explicitly. This is a latent risk but NOT a current bug.

**NaN handling**: Feature engineering fills NaN with 0 as a safety net. Verified: `test_engineer_features_no_nans` — ✅ PASS.

**Test results**: All 3 feature engineering tests ✅ PASS.

## 10. Model Output Contract

The existing inference pipeline already returns a well-defined output structure:

```python
{
    "patient_id": str,          # From input records
    "timestamp": str,           # ISO format, last record timestamp
    "risk_score": float,        # Fused probability [0, 1], rounded to 4 decimal places
    "risk_level": str,          # "LOW" | "WATCH" | "HIGH"
    "individual_models": {
        "xgboost": float,       # [0, 1]
        "cnn_lstm": float,      # [0, 1]
        "autoencoder": float,   # [0, 1]
        "transformer": float    # [0, 1]
    },
    "message": str              # "Prediction successful"
}
```

This contract is enforced by:
- `PredictionResponse` Pydantic schema in `predict_schema.py`
- FastAPI `response_model=PredictionResponse` on the `/predict` endpoint
- 13 existing tests in `test_api_predict.py`
- 7 new tests in `TestInferenceServiceE2E`

No changes to the output contract were required.

## 11. Fusion Verification

- **Weights**: XGBoost 0.35, CNN-LSTM 0.30, Autoencoder 0.20, Transformer 0.15.
- **Normalization**: Weights are normalized to sum to 1.0 in `__init__()`.
- **Formula**: `risk = Σ(weight_i × model_i_prob)` — simple weighted average.
- **Missing model behavior**: If any model fails to load, `_load_models()` raises an exception and the entire service fails to start. No silent degradation.
- **Numerical range**: Each model outputs [0, 1]; weighted sum of [0, 1] values with normalized weights is guaranteed [0, 1].
- **NaN handling**: No explicit NaN check in fusion. If a model returns NaN, the fused score will be NaN. This is an acceptable behavior for a demo — NaN propagation is safer than silently replacing with a default value.
- **Determinism**: Verified — same input produces same output within ε < 1e-4.
- **Test results**: `test_fusion_weights_sum_to_one` ✅, `test_fusion_predict_risk_output` ✅, `test_fusion_deterministic` ✅, `test_fusion_loads_all_models` ✅.

## 12. Risk-Level Verification

| Score Range | Risk Level |
|-------------|------------|
| [0.0, 0.30) | LOW |
| [0.30, 0.70) | WATCH |
| [0.70, 1.0] | HIGH |

Boundaries verified with 5 dedicated tests covering exact edge cases:
- `test_low_risk` ✅ (0.0, 0.15, 0.29)
- `test_watch_risk` ✅ (0.30, 0.50, 0.69)
- `test_high_risk` ✅ (0.70, 0.85, 1.0)
- `test_boundary_low_watch` ✅ (0.299999 → LOW, 0.3 → WATCH)
- `test_boundary_watch_high` ✅ (0.699999 → WATCH, 0.7 → HIGH)

Labels are treated as application/demo risk categories, not clinical diagnoses.

## 13. FastAPI Integration

**Endpoint**: `POST /api/v1/predict/`

**Request flow**:
```
PredictionRequest (Pydantic validation, min 60 records)
  ↓ inference_service.predict(request.records)
  ↓ crud.create_vital_signs(db, request.records) → MySQL vital_signs table
  ↓ crud.save_prediction(db, result) → MySQL predictions table
  ↓ Return PredictionResponse
```

**Error handling**:
- `RuntimeError` (models not loaded) → HTTP 503
- `Exception` (inference failure) → HTTP 400 with message
- Pydantic validation failure → HTTP 422

**Response structure**: Validated by `response_model=PredictionResponse`.

**Known issue**: `predict_deterioration()` is declared `async def` but calls synchronous CPU-bound inference. This blocks the event loop during inference. For a single-user demo prototype, this is acceptable. For production, should use `def` or `run_in_threadpool`.

**Test results**: All 13 existing `test_api_predict.py` tests ✅ PASS.

## 14. MySQL Persistence

**Tables used by inference**:
- `vital_signs`: Stores raw vital sign records from each `/predict` call.
- `predictions`: Stores fused risk score, risk level, and individual model scores.

**Verified fields persisted**:
- `patient_id`, `timestamp`, `risk_score`, `risk_level`
- `xgb_score`, `cnn_lstm_score`, `ae_score`, `transformer_score`

**Patient auto-creation**: `crud.ensure_patient_exists()` creates a Patient record if not found.

**Integrity**: No accidental overwrites — each call creates new rows with auto-increment IDs.

**Longitudinal history**: All synthetic patient data preserved (6 synthetic + 1 baseline).

**Test results**: `test_prediction_persisted` ✅, `test_vital_signs_persisted` ✅, plus 6 existing CRUD tests ✅.

## 15. Frontend Verification

The existing React dashboard correctly displays:
- Risk score badge with color coding
- Individual model scores (XGBoost, CNN-LSTM, Autoencoder, Transformer)
- Patient association
- Timestamps
- Risk level labels (LOW/WATCH/HIGH)

No frontend changes were made. No SHAP/attention/forecast panels were added (deferred to later phases).

## 16. Error Handling

| Scenario | Behavior | Verified |
|----------|----------|----------|
| Model artifacts missing | `_load_models()` raises Exception, server fails to start | ✅ By design |
| Models not loaded | `RuntimeError("Models are not loaded yet.")` → HTTP 503 | ✅ `test_service_not_loaded_raises` |
| Empty payload | Pydantic validation → HTTP 422 | ✅ `test_predict_rejects_empty_payload` |
| Too few records (< 60) | Pydantic `min_length=60` → HTTP 422 | ✅ `test_predict_rejects_too_few_records` |
| Missing vital field | Pydantic validation → HTTP 422 | ✅ `test_predict_rejects_missing_heart_rate` |
| Non-numeric vital | Pydantic validation → HTTP 422 | ✅ `test_predict_rejects_non_numeric_vital` |
| WebSocket alert fails | Caught, logged as warning, prediction still returns | ✅ By code inspection |
| TF context already initialized | Now caught with try/except, logged, continues | ✅ Fixed in Phase K |

**Credentials not exposed**: No database passwords, environment secrets, or stack traces are returned in API error responses. Pydantic/FastAPI HTTP error details contain only validation messages.

## 17. Performance Verification

| Metric | Value |
|--------|-------|
| Total model artifacts | ~2.06 MiB |
| Model loading | Once at startup (singleton) |
| Inference batch size | 1 |
| TF threads | Intra=4, Inter=2 |
| GPU | Not required (CPU-only, GPU growth enabled if available) |
| Full test suite time | 22.18 seconds (106 tests) |
| Repeated model loading | No — cached in `InferenceService` singleton |
| Unnecessary preprocessing | No — feature engineering runs once per prediction call |

Hardware: AMD Ryzen 3 7320U, 8 GB RAM, integrated AMD Radeon. All inference operations complete within acceptable time for a demo prototype.

## 18. End-to-End Inference Test

**Flow verified**:

```
60 synthetic vital records (constant HR=140, SpO2=96, RR=45, Temp=37, SBP=60, DBP=40)
  ↓ VitalSignRecord Pydantic validation ✅
  ↓ DataFrame conversion ✅
  ↓ Timestamp parsing & sorting ✅
  ↓ Missing-value flags added ✅
  ↓ Feature engineering (102 features) ✅
  ↓ Sequence window (30×6 scaled) ✅
  ↓ XGBoost predict_proba ✅
  ↓ CNN-LSTM predict ✅
  ↓ Transformer predict ✅
  ↓ Autoencoder reconstruct → MSE → pseudo-probability ✅
  ↓ Fusion (weighted average) ✅
  ↓ Risk level classification ✅
  ↓ API response construction ✅
  ↓ MySQL persistence (vital_signs + predictions) ✅
  ↓ Patient ID preserved in output ✅
```

All stages executed successfully. No fake outputs. No placeholder logic.

## 19. Test Results

### Before Changes
- Existing tests: **70 passed**, 0 failures

### After Changes
- Existing tests: **70 passed**, 0 failures (all preserved)
- New ML pipeline tests: **36 passed**, 0 failures

### Test Breakdown

| Test File | Tests | Status |
|-----------|-------|--------|
| `test_api_health.py` | 5 | ✅ PASS |
| `test_api_predict.py` | 13 | ✅ PASS |
| `test_api_chatbot.py` | 12 | ✅ PASS |
| `test_database.py` | 6 | ✅ PASS |
| `test_patient_endpoints.py` | 21 | ✅ PASS |
| `test_schemas.py` | 13 | ✅ PASS |
| **`test_ml_pipeline.py`** (NEW) | **36** | ✅ PASS |
| **Total** | **106** | ✅ **ALL PASS** |

### New Test Classes (36 tests)

| Class | Tests | Coverage |
|-------|-------|----------|
| `TestModelArtifacts` | 10 | Artifact existence, loading, scaler validation |
| `TestFeatureEngineering` | 3 | Column count, NaN-free output, XGBoost feature match |
| `TestXGBoostInference` | 1 | Predict proba shape and range |
| `TestDeepLearningInference` | 4 | CNN-LSTM, Transformer, Autoencoder inference + AE anomaly score |
| `TestFusionModel` | 4 | Model loading, weight normalization, risk output, determinism |
| `TestRiskLevelClassification` | 5 | All boundaries and edge cases |
| `TestInferenceServiceE2E` | 7 | Full pipeline: readiness, output shape, ranges, patient ID |
| `TestMySQLPersistence` | 2 | Prediction and vital sign DB persistence |

## 20. Code Changes

### Bug Fix: TF Context Re-Initialization

**File**: `backend/app/services/inference_service.py` (lines 53–58)

**Problem**: `tf.config.threading.set_intra_op_parallelism_threads(4)` raises `RuntimeError: Intra op parallelism cannot be modified after initialization` when TensorFlow context has already been initialized (e.g., when ML test classes load Keras models before the inference service is initialized via the FastAPI lifespan).

**Root cause**: TensorFlow's eager context is a global singleton. Once any TF operation runs (including `tf.keras.models.load_model`), the threading configuration is locked.

**Fix**: Wrapped the threading configuration calls in a `try/except RuntimeError` block. If already configured, the service logs a message and continues. The threading values are also set via environment variables (`OMP_NUM_THREADS`, `TF_NUM_INTRAOP_THREADS`, `TF_NUM_INTEROP_THREADS`) at the top of the file, which take effect before any TF initialization.

**Old behavior**: Server startup crashes if TF context is already initialized.
**New behavior**: Server startup succeeds; threading values from environment variables are honored.

**Impact**: Zero impact on production behavior (first call always succeeds). Fixes test suite compatibility.

## 21. Files Changed

| File | Change | Reason |
|------|--------|--------|
| `backend/app/services/inference_service.py` | Wrapped `set_intra_op_parallelism_threads` / `set_inter_op_parallelism_threads` in try/except | Fix TF context re-initialization crash |
| `tests/test_ml_pipeline.py` | **NEW** — 36 ML verification tests | Phase K test coverage |

## 22. Files Not Changed

- All model artifacts (`*.keras`, `xgboost_model.json`, `scaler.pkl`, `ae_threshold.json`, `xgb_features.json`)
- Database schema / migration scripts
- `ml/models/fusion.py`
- `ml/features/features.py`
- `ml/preprocessing/preprocess.py`
- `ml/models/cnn_lstm.py`, `ml/models/transformer.py`, `ml/models/autoencoder.py`
- `backend/app/api/endpoints/predict.py`
- `backend/app/api/endpoints/stream.py`
- `backend/app/api/endpoints/alerts_ws.py`
- `backend/app/main.py`
- `backend/app/db/crud.py`, `backend/app/db/models.py`, `backend/app/db/database.py`
- `backend/app/schemas/predict_schema.py`
- Frontend files
- Synthetic dataset CSV files
- Existing test files (`conftest.py`, `test_api_*.py`, `test_database.py`, `test_patient_endpoints.py`, `test_schemas.py`)
- Phase reports (`phase_i_report.md`, `phase_j_report.md`, etc.)

## 23. Remaining Gaps

| Gap | Severity | Phase to Address |
|-----|----------|-----------------|
| SHAP explainability missing | Not blocking | Phase K+ (future) |
| Transformer attention weights not extracted | Not blocking | Phase K+ (future) |
| Transformer is classifier, not forecaster | Not blocking | Phase K+ (future) |
| NICU stream does not trigger inference | Not blocking | Phase K+ (future) |
| Prenatal growth is rule-based, not ML | Not blocking | Phase K+ (future) |
| `features.py` default `window_sizes=[15, 60]` missing 30 | Low risk (mitigated by explicit param) | Document only |
| `predict_deterioration` is async but runs sync inference | Low risk for demo | Future optimization |
| No NaN imputation before `scaler.transform` in inference | Low risk (input validation enforces non-null) | Document only |
| `fusion.predict_risk` return type hint says `np.ndarray` but returns tuple | Cosmetic | Minor |
| `Prediction` table vs `ModelOutput` table disconnect | Not blocking | Future consolidation |

## 24. Safety Verification

- ✅ "SYNTHETIC / ACADEMIC DEMO DATA — NOT FOR CLINICAL USE" labeling preserved
- ✅ Academic/research prototype framing maintained
- ✅ Decision-support language only (no autonomous diagnosis)
- ✅ No treatment recommendations generated
- ✅ No clinical validation claims made
- ✅ No credentials exposed in source code or API responses
- ✅ No model accuracy claims from synthetic data
- ✅ Risk levels labeled as application categories, not clinical diagnoses

## 25. Phase K Result

| Checkpoint | Status |
|------------|--------|
| Existing model artifacts load | ✅ PASS |
| XGBoost verified | ✅ PASS |
| CNN-LSTM verified | ✅ PASS |
| Transformer classifier verified | ✅ PASS |
| Autoencoder verified | ✅ PASS |
| Fusion verified | ✅ PASS |
| Risk level verified | ✅ PASS |
| /api/v1/predict verified | ✅ PASS |
| MySQL persistence verified | ✅ PASS |
| Existing frontend output verified | ✅ PASS |
| Error handling verified | ✅ PASS |
| Performance checked | ✅ PASS |
| End-to-end inference checked | ✅ PASS |
| Existing tests still pass | ✅ 70/70 |
| No model retraining | ✅ Confirmed |
| No database schema changes | ✅ Confirmed |
| No synthetic data deletion/modification | ✅ Confirmed |
| No SQLite | ✅ Confirmed |
| No credentials exposed | ✅ Confirmed |
| Safety labeling preserved | ✅ Confirmed |
| phase_k_report.md created | ✅ |
| task.md updated | ✅ |

**PHASE K STATUS: COMPLETE**

---

*Prepared by Antigravity — © 2026*

