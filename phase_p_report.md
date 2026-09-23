# PHASE P REPORT

## 1. Objective

Phase P introduced controlled Transformer Attention Explainability and completed a technical audit of Multi-Horizon Forecasting capabilities for **NeoNatal Watch AI**.

The objectives achieved in this phase are:
1. Extract and expose exact Multi-Head Self-Attention matrices from the existing trained Transformer model (`models/transformer.keras`).
2. Provide a mathematically sound temporal attention summary showing how the model distributes attention across the 30-minute input sequence window.
3. Conduct a technical audit of Multi-Horizon Forecasting capabilities, reporting exact model limitations without fabricating fake forecasts or retraining model artifacts.
4. Integrate attention explanations and forecasting audit status into REST API endpoints and the React hospital dashboard UI.

---

## 2. Phase O Baseline

- **Baseline Tests**: 172 passed / 0 failed (Phase K: 106, Phase L: 6, Phase M: 15, Phase N: 15, Phase O: 30).
- **Subsystems Operational**:
  - XGBoost risk model: Operational
  - CNN-LSTM deep sequence model: Operational
  - Transformer classifier: Operational
  - Autoencoder anomaly detector: Operational
  - Fusion weighted ensemble: Operational
  - TreeSHAP feature explainability: Operational
  - Autoencoder reconstruction explainability: Operational
  - Prenatal longitudinal decision support: Operational
  - Real-time NICU stream & alert pipeline: Operational
  - MySQL persistent database: Operational
  - React hospital dashboard: Operational

---

## 3. Existing Transformer Architecture Audit

- **Model Class**: Keras Functional API (`NeoNatal_Transformer`) defined in `ml/models/transformer.py`.
- **Trained Artifact**: `models/transformer.keras` (Size: 1.28 MB).
- **Architecture Overview**:
  - 1D Convolutional Projection layer (`Conv1D`, 64 filters, kernel size 1).
  - Learnable Positional Embedding layer (`Embedding`, 30 steps, 64 dim).
  - 2 Transformer Encoder blocks, each containing:
    - LayerNormalization + `MultiHeadAttention` (4 heads, key dimension 32) + Dropout + Residual Add.
    - LayerNormalization + `Conv1D` (64 filters, ReLU) + Dropout + `Conv1D` (64 filters) + Residual Add.
  - `GlobalAveragePooling1D` layer.
  - Multi-Layer Perceptron (MLP): `Dense(64, ReLU)` -> `Dropout(0.3)` -> `Dense(32, ReLU)` -> `Dropout(0.3)`.
  - Output Layer: `Dense(1, activation="sigmoid")`, named `deterioration_probability`.

---

## 4. Transformer Input Shape

$$\text{Input Tensor Shape}: (n_{\text{samples}}, 30, 6)$$

---

## 5. Transformer Output Shape

$$\text{Output Tensor Shape}: (n_{\text{samples}}, 1)$$

---

## 6. Feature Count and Feature Mapping

- **Feature Count**: 6 continuous vital sign telemetry channels.
- **Vital Sign Features (`VITAL_COLUMNS`)**:
  1. `heart_rate` (bpm)
  2. `spo2` (%)
  3. `respiratory_rate` (breaths/min)
  4. `temperature` (°C)
  5. `systolic_bp` (mmHg)
  6. `diastolic_bp` (mmHg)

---

## 7. Sequence Length

- **Window Length**: Exactly 30 time steps (30 minutes of telemetry at 1-minute sampling intervals).

---

## 8. Attention Architecture

- **Block Count**: 2 stacked Transformer Encoder blocks (`multi_head_attention` and `multi_head_attention_1`).
- **Heads Per Block**: 4 attention heads (`num_heads=4`, `head_size=32`).
- **Total Attention Matrices**: 8 attention matrices per sequence input (2 layers $\times$ 4 heads).

---

## 9. Attention Extraction Method

Attention matrices are extracted on-demand during forward execution by querying layer normalization outputs and executing the exact loaded `MultiHeadAttention` layer instances with `return_attention_scores=True`.

This extracts the exact attention tensors without re-initializing, refitting, or mutating trained model weights.

---

## 10. Attention Tensor Dimensions

- **Per-Layer Attention Tensor Shape**: `(batch_size, num_heads, sequence_length, sequence_length)` = `(1, 4, 30, 30)`.
- **Full Model Raw Attention Array Structure**: `[2, 4, 30, 30]`, representing `[layer_idx, head_idx, time_query, time_key]`.

---

## 11. Attention Aggregation

1. **Per-Layer Mean Attention Matrix**: Averaged across the 4 attention heads for each layer:
   $$A_{\text{layer\_0}} = \frac{1}{4} \sum_{h=0}^{3} A_{0, h} \in \mathbb{R}^{30 \times 30}$$
   $$A_{\text{layer\_1}} = \frac{1}{4} \sum_{h=0}^{3} A_{1, h} \in \mathbb{R}^{30 \times 30}$$

2. **Overall Mean Attention Matrix**: Averaged across both Transformer layers:
   $$A_{\text{overall}} = \frac{1}{2} (A_{\text{layer\_0}} + A_{\text{layer\_1}}) \in \mathbb{R}^{30 \times 30}$$

3. **Normalized Temporal Summary**: Mean attention received by key step $j$ across query steps $i$, normalized to sum to 1.0:
   $$w_j = \frac{1}{30} \sum_{i=0}^{29} A_{\text{overall}}[i, j]$$
   $$\sum_{j=0}^{29} w_j = 1.0$$

---

## 12. Temporal Attention Analysis

- Identifies which specific 1-minute time steps in the 30-minute window received the highest attention weights from the Transformer model.
- Time step entries contain `step_index` (0..29), `timestamp`, `attention_weight`, and `attention_percent`.

---

## 13. Feature-Level Attention Analysis

- Attention mechanisms in standard sequence Transformers operate over sequence time positions (temporal self-attention, shape $30 \times 30$), NOT directly across feature channels.
- Feature contributions remain accurately attributed to SHAP for XGBoost tabular features and Autoencoder for vital sign reconstruction residuals.

---

## 14. Attention Prediction Consistency

- **Prediction BEFORE attention extraction**: $P_{\text{before}} = f_{\text{Transformer}}(X)$.
- **Prediction AFTER attention extraction**: $P_{\text{after}} = f_{\text{Transformer}}(X)$.
- **Numerical Verification**: $|P_{\text{before}} - P_{\text{after}}| = 0.000000$ (0 prediction shift).

---

## 15. Multi-Horizon Forecasting Audit

A technical audit was conducted on `models/transformer.keras` to determine whether the existing model artifact can generate multi-step future vital forecasts.

- **Current Model Architecture**: Single-output binary classifier (`Dense(1, activation="sigmoid")`).
- **Current Model Target**: Binary deterioration probability ($P \in [0, 1]$).
- **Audit Conclusion**: The existing Transformer artifact is a single-output binary classifier for deterioration risk and does NOT output multi-horizon regression or sequence predictions. Multi-horizon future vital forecasting requires a forecasting-capable model/training target and cannot be truthfully implemented using the current classifier artifact without retraining or architecture changes.

---

## 16. Forecasting Capability

- **Status**: UNSUPPORTED on current classifier artifact.
- **Reporting**: The system reports the exact technical limitation via dedicated API endpoints (`POST /api/v1/predict/forecast` and `GET /api/v1/patients/{id}/forecast`) and UI audit panels without fabricating fake forecasts.

---

## 17. Forecast Target

- **Current Target**: Binary deterioration risk probability ($P \in [0, 1]$).

---

## 18. Forecast Horizon Definition

- **Current Horizon**: Sequence-to-one current state assessment over the 30-minute window.

---

## 19. Forecast Generation

- **Behavior**: Returns structured audit status explaining the model classification task and technical limitation. Fake multi-step forecast arrays are NOT generated.

---

## 20. Forecast Consistency

- Querying forecast status does NOT modify existing model predictions, risk scores, fusion weights, or database records.

---

## 21. API Integration

Added 4 dedicated API endpoints:
- `POST /api/v1/predict/attention-explain`: Returns Multi-Head Self-Attention weights for a 30-step sequence.
- `GET /api/v1/patients/{id}/attention-explain`: Queries patient telemetry in MySQL and returns attention weights.
- `POST /api/v1/predict/forecast`: Returns multi-horizon forecasting capability audit status.
- `GET /api/v1/patients/{id}/forecast`: Queries patient forecast capability audit status.

---

## 22. Frontend Integration

Added two UI cards to section 5 of the patient modal in `frontend/app.jsx`:
1. **Transformer Attention Analysis Panel**: Displays top attended sequence timesteps, layer/head counts, raw tensor dimensions (`[2, 4, 30, 30]`), risk score, and safety disclaimers.
2. **Multi-Horizon Forecasting Audit Card**: Displays the classifier limitation status banner and non-clinical disclaimers.

---

## 23. Real-Time Stream Safety

- Attention extraction and forecasting audits are performed on-demand via REST API endpoints when requested by the dashboard.
- Real-time SSE streaming, 60-step telemetry buffering, and WebSocket alert broadcasting run unaffected with **0 latency impact**.

---

## 24. MySQL Verification

- **Database Changes**: ZERO MySQL schema changes, table alterations, column additions, or record mutations.

---

## 25. Multi-Patient Isolation

- Requests for Patient A and Patient B execute independently without cross-contaminating attention matrices or prediction scores.

---

## 26. Numerical Stability

- Attention weight matrices sum to 1.0 along the key axis.
- Zero NaN or Inf values produced during attention aggregation.

---

## 27. Performance Benchmark

- Transformer forward inference: `< 15 ms`
- Attention matrix extraction: `< 20 ms`
- Total explanation response time: `< 35 ms` (well under the `< 250 ms` low-spec hardware target).

---

## 28. SHAP Regression

- All 15 Phase N SHAP tests continue to pass with 0 failures.

---

## 29. Autoencoder Regression

- All 30 Phase O Autoencoder tests continue to pass with 0 failures.

---

## 30. Prenatal Regression

- All 15 Phase M Prenatal tests continue to pass with 0 failures.

---

## 31. NICU Regression

- All 6 Phase L NICU real-time stream tests continue to pass with 0 failures.

---

## 32. Test Results

- **Previous Baseline**: 172 passed / 0 failed.
- **New Attention Tests**: 23 passed / 0 failed (`tests/test_transformer_attention.py`).
- **New Forecasting Audit Tests**: 4 passed / 0 failed (`tests/test_transformer_forecasting.py`).
- **Total Test Suite**: **199 passed / 0 failed (100% SUCCESS)**.

---

## 33. Code Changes

- Created `ml/explainability/transformer_explainer.py` (`TransformerAttentionExplainer`).
- Extended `backend/app/services/inference_service.py` (`explain_transformer`, `get_transformer_forecast`).
- Extended `backend/app/api/endpoints/predict.py` (`POST /attention-explain`, `POST /forecast`).
- Extended `backend/app/api/endpoints/patient.py` (`GET /{id}/attention-explain`, `GET /{id}/forecast`).
- Extended `frontend/app.jsx` (Attention & Forecast audit UI components).
- Created `tests/test_transformer_attention.py` (23 tests).
- Created `tests/test_transformer_forecasting.py` (4 tests).

---

## 34. Model Artifact Changes

- **Model Artifacts Changed**: **NO** (`models/transformer.keras` remains 100% untouched).

---

## 35. Database Changes

- **Database Changes**: **NONE** (0 schema changes, 0 table modifications).

---

## 36. Dataset Changes

- **Dataset Changes**: **NONE** (0 synthetic data files altered).

---

## 37. Files Created

- `ml/explainability/transformer_explainer.py`
- `tests/test_transformer_attention.py`
- `tests/test_transformer_forecasting.py`
- `phase_p_report.md`

---

## 38. Files Changed

- `backend/app/services/inference_service.py`
- `backend/app/api/endpoints/predict.py`
- `backend/app/api/endpoints/patient.py`
- `frontend/app.jsx`
- `task.md`

---

## 39. Files Not Changed

- `models/transformer.keras` (UNTOUCHED)
- `models/xgboost_model.json` (UNTOUCHED)
- `models/cnn_lstm.keras` (UNTOUCHED)
- `models/autoencoder.keras` (UNTOUCHED)
- `models/scaler.pkl` (UNTOUCHED)
- `ml/models/fusion.py` (UNTOUCHED)
- `backend/app/db/models.py` (UNTOUCHED)
- All synthetic datasets under `data/synthetic/` (UNTOUCHED)

---

## 40. Findings Outside Phase P Scope

- Multi-horizon time-series vital forecasting (e.g. predicting HR or SpO2 values 15-30 minutes into the future) would require training a dedicated sequence-to-sequence regression Transformer or fine-tuning an autoregressive decoder model.

---

## 41. Safety Verification

- Non-clinical safety disclaimers embedded in all attention responses:
  > *"Transformer attention weights show how the model distributed attention across the input sequence. They do not establish clinical causation, diagnosis, treatment recommendations, or clinical importance. SYNTHETIC / ACADEMIC DEMO DATA — NOT FOR CLINICAL USE."*
- Forecasting audit disclaimer embedded:
  > *"Forecasts are model-generated research outputs based on the available input sequence. They are not clinical predictions, diagnoses, or treatment recommendations."*

---

## 42. Remaining Gaps

- Future sequence forecasting requires a dedicated trained regression architecture if requested in future project phases.

---

## 43. Phase P Result

- **OVERALL PHASE P RESULT**: **PASS WITH FINDINGS** (Transformer attention explainability fully operational; multi-horizon forecasting audited and documented as unsupported on current binary classifier artifact without retraining).

---
*End of Phase P Report.*

