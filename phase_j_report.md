# Phase J — ML Integration Plan

## 1. Objective

Create a concrete, prioritized roadmap to integrate the existing ML components into NeoNatal Watch AI while preserving the academic prototype constraints. The plan translates Phase I audit findings into actionable future work without modifying any code, data, or schema at this stage.

## 2. Phase I Findings Summary

- **Implemented & Connected**: XGBoost, CNN‑LSTM, Transformer (as a classifier), Autoencoder, Feature Engineering, MinMax Scaler, Fusion model, Real‑time alert WebSocket, API `/api/v1/predict`, MySQL persistence, React dashboard visualisation of all model scores, NICU vital streaming (simulation only).
- **Partially Implemented**: Preprocessing pipeline (full pipeline used only for training; inference uses a subset of steps).  
- **Placeholders / Missing**: SHAP explainability (no library, no code), attention weight extraction (Transformer weights never exposed), multi‑horizon forecasting (Transformer outputs a single probability), prenatal growth AI (rule‑based, not exposed via endpoint), NICU stream → inference linkage (stream writes vitals but does not trigger model inference), CORS open to all origins (security note).
- **Artifacts present**: `models/xgboost_model.json`, `models/cnn_lstm.keras`, `models/transformer.keras`, `models/autoencoder.keras`, `models/scaler.pkl`, `models/xgb_features.json`, `models/ae_threshold.json`.
- **Performance**: All models are lightweight (total < 2 MiB); inference runs with batch‑size 1, TF threads limited to 4, GPU‑growth enabled – suitable for Ryzen 3 7320U, 8 GiB RAM.
- **Security**: No credentials in source; `.env` used; CORS open (`allow_origins=["*"]`).
- **Medical safety**: No autonomous diagnosis claims; academic‑demo disclaimer present throughout UI and docs.
- **Test baseline**: `pytest -q` → 70 passed, 0 failed.

## 3. Current ML Architecture

```
Raw Vital‑Sign CSV → Inference Service
  ↓ preprocessing (outlier clamp, missing fill, MinMax scaling) – subset of training pipeline
  ↓ feature engineering (rolling stats, rate‑of‑change) → flat XGBoost features
  ↓ sequence window (last 30 rows) → CNN‑LSTM / Transformer / Autoencoder inputs
  ↓ XGBoost, CNN‑LSTM, Transformer, Autoencoder inference
  ↓ weighted fusion (0.35 XGB, 0.30 CNN‑LSTM, 0.20 AE, 0.15 Transformer)
  ↓ risk score & level
  ↓ FastAPI `/api/v1/predict`
  ↓ MySQL tables `vital_signs` & `predictions`
  ↓ React dashboard (risk badge, individual model scores, WebSocket alerts)
```

*Prenatal growth analysis* runs as a service‑layer query (`prenatal_service.py`) against stored predictions – no ML model call.

*NICU stream* (`stream.py`) generates simulated vitals and writes to `nicu_vitals` but does **not** invoke the inference pipeline.

## 4. Target ML Architecture

```
Data (MySQL) → Preprocessing (full pipeline) → Feature Engineering
  ↓
[PLANNED] SHAP Explainability (XGBoost)
  ↓
[PLANNED] Attention Extraction (Transformer)
  ↓
Model Fusion (existing weighted ensemble)
  ↓
Risk/Anomaly Scores → MySQL `predictions` & `model_outputs`
  ↓
[PLANNED] Prenatal Growth ML (future model, currently rule‑based)
  ↓
[PLANNED] NICU Real‑Time Inference (stream → inference trigger)
  ↓
FastAPI Endpoints (extend `/predict`, add `/explain`, `/attention`)
  ↓
React UI (add explanation panels, attention heat‑maps, forecast visualisations)
``` 
All **[PLANNED]** blocks are future work; everything else already exists.

## 5. ML Integration Matrix

| Component | Current Status | Current Location | Integration Gap | Proposed Integration | Priority | Complexity | Phase |
|-----------|----------------|------------------|-----------------|----------------------|----------|------------|-------|
| XGBoost | ✅ Implemented & Connected | `ml/models/fusion.py`, `models/xgboost_model.json` | None (verification only) | Verify output schema, add optional SHAP later | P0 | Low | – |
| CNN‑LSTM | ✅ Implemented & Connected | `ml/models/cnn_lstm.py`, `models/cnn_lstm.keras` | None | Verification & optional benchmarking | P1 | Low | – |
| Transformer | ✅ Implemented (classifier) | `ml/models/transformer.py`, `models/transformer.keras` | Missing multi‑horizon forecasting & attention extraction | Extend to output attention weights; design forecast head (future work) | P3 | Medium | – |
| Autoencoder | ✅ Implemented & Connected | `ml/models/autoencoder.py`, `models/autoencoder.keras` | Threshold hard‑coded; no UI for anomaly details | Expose reconstruction error, configurable threshold UI | P2 | Low | – |
| SHAP | ❌ Missing | `ml/explainability/` (empty) | No library, no code, no endpoint | Add `shap` dependency, create explainer for XGBoost, new `/explain` endpoint | P2 | Medium | – |
| Attention | ❌ Missing | – | No weight extraction | Modify Transformer to return attention scores, add `/attention` endpoint | P3 | Medium | – |
| Prenatal Prediction | ⚠️ Partially connected (rule‑based) | `backend/app/services/prenatal_service.py` | No live ML model, no endpoint | Keep rule‑based for now; future model can replace service logic | P1 | Medium | – |
| NICU Real‑Time Scoring | ⚠️ Placeholder (stream only) | `backend/app/api/endpoints/stream.py` | No inference trigger | Buffer 60 records per patient, invoke existing `/predict` automatically, store results | P1 | Medium | – |
| Risk Fusion | ✅ Implemented | `ml/models/fusion.py` | Fixed static weights | Make weights configurable via env or DB (future) | P0 | Low | – |
| Alert Generation | ✅ Implemented (WebSocket) | `alerts_ws.py` | None | Ensure alerts include source model identifiers | P0 | Low | – |
| AI Chatbot | ⚠️ Demo (heuristic) | `chatbot.py` | No ML | Optional future LLM integration (out of scope) | P4 | High | – |

## 6. Priority Matrix

- **P0 – Required foundation**: XGBoost verification, risk fusion stability, alert broadcast correctness.
- **P1 – Core ML integration**: NICU real‑time inference trigger, prenatal rule‑based pipeline validation, benchmarking of existing models.
- **P2 – Explainability**: SHAP for XGBoost, Autoencoder anomaly UI, configurable anomaly threshold.
- **P3 – Advanced forecasting**: Transformer attention extraction, multi‑horizon forecast head design.
- **P4 – Optional enhancements**: AI chatbot upgrade, configurable fusion weights, full CORS hardening.

## 7. XGBoost Integration Plan

- **Model location**: `models/xgboost_model.json` (JSON) + feature list `models/xgb_features.json`.
- **Input**: ~170 engineered tabular features produced by `ml/features/features.py`.
- **Pre‑processing**: Already performed in `inference_service.predict()` (rolling stats + missing‑flag creation).
- **Loading**: `FusionModel._load_models()` uses `xgb.XGBClassifier().load_model()` – retained.
- **Inference function**: `FusionModel.predict_risk()` → `xgb_model.predict_proba()`.
- **Output schema**: `xgb_score` column in `predictions` table (already persisted).
- **Risk‑score handling**: Contributes 35 % to fused risk; thresholding handled by fusion layer.
- **Database persistence**: `crud.save_prediction()` writes `xgb_score`.
- **FastAPI endpoint**: Existing `POST /api/v1/predict` – no change.
- **Frontend**: Already displayed as `XGBoost` score in patient view.
- **Testing**: Verify that `xgb_score` appears in API response and DB row for all future predictions.

*Conclusion*: Existing implementation retained; only verification and optional SHAP addition later.

## 8. Autoencoder Integration Plan

- **Model artifact**: `models/autoencoder.keras`.
- **Input**: Same 30×6 scaled sequence used for other deep models.
- **Pre‑processing**: Same scaler & sequence window.
- **Threshold**: Current 95 th percentile threshold stored in `models/ae_threshold.json` (0.00424). Future UI should allow admin to adjust via config file – not a hard‑coded value.
- **Anomaly score**: `ae_score` column in `predictions` (already persisted). UI shows the score.
- **API**: No separate endpoint; score emitted via `/predict`.
- **Future UI**: Add tooltip explaining that the score is a *pseudo‑probability* derived from reconstruction error; include a badge for “Anomaly Detected” when above a configurable alert threshold (e.g., 0.6).
- **Testing**: Add unit test that verifies `ae_score` is within [0,1] and that synthetic high‑error windows produce higher scores.

## 9. CNN‑LSTM Integration Plan

- **Artifact**: `models/cnn_lstm.keras`.
- **Data source**: Same 60‑record vital‑sign batch supplied to `/predict`.
- **Sequence handling**: Last 30 records selected, scaled, shaped to (1,30,6).
- **Inference**: `self.cnn_lstm_model.predict()` inside `FusionModel` – retained.
- **Output**: `cnn_lstm_score` column in `predictions` table, shown on UI.
- **Future data**: Could also be used for offline batch analysis of synthetic sequences.
- **Testing**: Ensure deterministic output for a given input (seeded RNG) for regression tests.

## 10. Transformer Integration Plan

- **Current state**: Implemented as binary classifier.
- **Future goal**: Multi‑horizon forecasting.
- **Proposed steps**:
  1. Refactor `ml/models/transformer.py` to add a decoder head that predicts future vital‑sign vectors for N steps (e.g., 5‑minute horizon).
  2. Keep existing classifier branch for backward compatibility.
  3. Expose both outputs via `FusionModel` – classifier contribution stays, forecast stored in a new `model_outputs` row with `output_type="forecast"`.
  4. UI panel to plot predicted vs actual future vitals.
- **Integration gap**: No attention weight extraction – will be tackled together with forecasting.
- **Priority**: P3 (advanced) – not required for core functionality.

## 11. SHAP Integration Plan

1. **Add dependency**: `shap` (pure‑Python, CPU‑only).
2. **Create explainer** in a new module `ml/explainability/shap_explainer.py` that loads the XGBoost model and the feature list.
3. **Endpoint**: `GET /api/v1/predict/{patient_id}/explain` returning JSON:
   ```json
   {"model":"xgboost","features":[{"name":"hr_mean_30","value":0.72,"shap":0.05},…]}
   ```
4. **Response**: Top‑5 contributing features with sign.
5. **Frontend**: Add an “Explain” button on the prediction card that fetches and displays a bar chart.
6. **Testing**: Mock explainer to verify API schema.

*Note*: No SHAP values exist for historic synthetic data; explanation will be computed on‑the‑fly for new predictions only.

## 12. Attention Visualization Plan

- **Modify Transformer**: Change `MultiHeadAttention(..., return_attention_scores=True)` and capture the attention tensor.
- **Create a thin wrapper model** that outputs both the probability and the attention matrix.
- **Endpoint**: `GET /api/v1/predict/{patient_id}/attention` returning per‑timestep weight arrays.
- **Frontend**: Heat‑map visualisation (e.g., using `react‑heat‑map-grid`).
- **Gap**: Current code does not expose weights – this will be added in a future phase (P3).

## 13. Prenatal / Fetal Growth AI Plan

- **Keep existing rule‑based service** (`prenatal_service.py`).
- **Future model placeholder**: Define an interface `PrenatalModel.predict(pregnancy_id)` that returns EFW percentile predictions.
- **Integration**: When a model becomes available, replace the rule‑based delta calculation with model output while preserving the current API contract (`GrowthAnalysis` record).
- **UI**: Show “Model‑estimated growth variance” label alongside existing delta.
- **Safety wording**: Always prefix with *“model‑estimated”* and *“requires clinician review”.*

## 14. NICU AI Integration Plan

1. **Buffering**: Accumulate 60 vital‑sign records per NICU patient in memory (or temporary table).
2. **Trigger**: When buffer is full, invoke existing `/api/v1/predict` automatically (or call `inference_service.predict()` internally).
3. **Persist**: Store resulting `predictions` and `model_outputs` rows linked to `nicu_admission_id`.
4. **Alert**: Use existing WebSocket to broadcast HIGH risk.
5. **Frontend**: Extend NICU dashboard to show per‑model scores and anomaly flag.
6. **Performance**: Run inference at most once per minute per patient; use batch‑size 1.
7. **Testing**: Simulate stream in unit tests, assert that a prediction row appears after 60 simulated vitals.

## 15. Risk Fusion Plan

- **Current**: Fixed static weights (0.35/0.30/0.20/0.15).
- **Future**: Move weights to configuration (`fusion_config.json`) so they can be tuned without code change.
- **Missing‑model handling**: If a model fails to load, re‑normalise remaining weights proportionally.
- **Confidence**: Store individual model scores; fused risk labelled as *"academic/demo composite risk indicator"*.

## 16. MySQL Integration Plan

| Future Output | Existing Table | Existing Column | New Column Needed? | Comment |
|---------------|----------------|----------------|-------------------|---------|
| SHAP explanation metadata | `model_outputs` | `explanation_reference` (currently holds placeholder strings) | No – reuse column, store path to generated SHAP JSON when implemented. |
| Attention weights | `model_outputs` | `output_type` = "attention" (new row) | No – add a new row with `output_type="attention"` and JSON payload in `output_value`. |
| Forecast horizon values | `model_outputs` | `output_type` = "forecast" | No – same table, store serialized forecast array.
| Configurable fusion weights | – | – | **PROPOSED FUTURE MIGRATION** – new table `fusion_config` (model_name, weight). |

All other outputs already map to existing columns (`xgb_score`, `cnn_lstm_score`, `ae_score`, `transformer_score`, `risk_score`, `risk_level`). No schema changes are required for Phase J.

## 17. API Integration Plan

| Path | Method | Current Status | Planned Extension |
|------|--------|----------------|-------------------|
| `/api/v1/predict` | POST | Fully functional – returns fused risk and per‑model scores. | No change now; later may add query param `include=shap,attention`. |
| `/api/v1/predict/{patient_id}/explain` | GET | **Not present** | Return SHAP bar‑chart data for XGBoost (P2). |
| `/api/v1/predict/{patient_id}/attention` | GET | **Not present** | Return attention matrix (P3). |
| `/api/v1/forecast/{patient_id}` | GET | **Not present** | Provide multi‑horizon forecast (future). |
| `/api/v1/prenatal/{pregnancy_id}` | GET | Existing rule‑based service not exposed as endpoint. | Add endpoint that returns growth variance and model‑estimated pattern (P1). |
| `/api/v1/nicu/stream` | SSE | Streaming simulation only. | Add optional query `auto_predict=true` to trigger inference after buffer full (P1). |
| `/api/v1/alerts/ws` | WebSocket | Active – broadcasts HIGH risk. | Enrich payload with source model identifiers (P0). |

All new endpoints will reuse existing FastAPI app and JWT‑less auth (demo). 

## 18. Frontend Integration Plan

| UI Area | Current Component | Planned Data Source | Future Visualisation |
|---------|-------------------|----------------------|----------------------|
| Patient Detail Card | `RiskBadge.jsx` | `/predict` response | Add "Explain" button → SHAP bar chart modal.
| Transformer Detail | none | future `/attention` endpoint | Heat‑map of attention weights over 30‑step window.
| Forecast Panel | none | future `/forecast` | Line chart comparing predicted vitals vs actual.
| NICU Dashboard | `NICUChart.jsx` (vitals) | Stream SSE + existing predictions | Show auto‑generated risk score beside vital chart.
| Fusion Config (admin) | none | new config UI (optional) | Slider controls for model weights.

All components will retain existing Tailwind styling and synthetic‑data disclaimer.

## 19. Dataset / Data Gap Plan

| Model | Required Features / Labels | Available? | Gap |
|-------|---------------------------|------------|-----|
| XGBoost | Rolling stats + missing flags (already derived) | ✔️ | – |
| CNN‑LSTM / Transformer / Autoencoder | 30‑step vital‑sign windows (present) | ✔️ | – |
| SHAP | Same XGBoost features | ✔️ (features) – need SHAP library | **DATA GAP — SHAP library needed** |
| Multi‑horizon Forecast | Future vital‑sign sequences (ground‑truth) | Not collected in synthetic data | **DATA GAP — forecast labels required** |
| Prenatal growth model | Early‑trimester labs + later growth outcomes | Synthetic records contain some labs but no labelled ML target | **DATA GAP — training labels missing** |
| NICU real‑time inference | Continuous stream of 60‑record windows | Simulated stream exists; real‑time buffer needed | **DATA GAP — buffering logic** |

## 20. Performance Plan

- Keep batch size 1 for all inference calls.
- Lazy‑load models at startup; reuse singleton instances.
- Limit attention‑extraction calls to on‑demand UI actions (avoid per‑request overhead).
- NICU stream buffering runs in a lightweight async task; inference only when buffer full.
- No GPU required; TF will run on CPU with thread caps already set.
- Optional heavy‑weight features (multi‑horizon forecasting) are marked **OPTIONAL FUTURE DEPLOYMENT**.

## 21. Security Plan

- Continue using `.env` for DB credentials; ensure no secrets leak into source.
- Keep CORS open for demo but document as a **future hardening step** (P4).
- Input validation already present in Pydantic schemas; future endpoints must reuse same validation.
- Log only non‑PII metadata for audit trails; avoid writing raw vital values to logs.
- When SHAP or attention JSON payloads are generated, store them under `artifacts/` with restricted file permissions.

## 22. Medical Safety Plan

All future model‑derived messages will use the mandated language:
- "model‑estimated risk"
- "potential contributing pattern"
- "decision support"
- "requires clinician review"
- UI will display the synthetic‑data disclaimer prominently on any new panels.

No statements of clinical validation, guarantees, or diagnoses will be added.

## 23. Testing & Validation Plan

- **Unit tests** for each new helper (SHAP explainer, attention wrapper).
- **API tests** using the existing FastAPI `TestClient` to verify new endpoints return 200 and correct JSON schema.
- **Database tests** confirming that new `model_outputs` rows are created with correct `output_type`.
- **Frontend tests** (React Testing Library) for modal rendering of SHAP bar chart and attention heat‑map.
- **End‑to‑end** scripts (`scripts/verify_phase_g_e2e.py`) extended to cover new UI panels.
- Maintain current 70/70 baseline; new tests add on top, never remove existing ones.

## 24. Proposed Future Phase Sequence

| Phase | Objective | Dependencies |
|-------|-----------|--------------|
| **K – Explainability Foundations** | Implement SHAP explainer & UI panel; expose attention weights. | XGBoost artifact, Transformer model, FastAPI. |
| **L – NICU Real‑Time Inference** | Buffer stream, trigger `/predict`, store results, UI integration. | Stream endpoint, inference service. |
| **M – Configurable Fusion & Alerts** | Make fusion weights configurable; enrich alert payloads. | Fusion model, WebSocket. |
| **N – Prenatal ML Model Integration** | Replace rule‑based growth analysis with learned model. | Synthetic prenatal data, future labeled dataset. |
| **O – Multi‑Horizon Forecasting** | Extend Transformer to predict future vitals; UI timeline. | Transformer refactor, forecast dataset. |
| **P – Security Hardening** | Restrict CORS, add auth, audit logging. | No code changes required yet. |
| **Q – Full End‑to‑End Validation** | Run comprehensive e2e suite covering all new features. | Completion of K‑P. |

## 25. Risks and Dependencies

- **Missing training data** for forecasting and prenatal models (requires external dataset). 
- **Performance overhead** when extracting attention matrices (mitigated by on‑demand calls). 
- **Security exposure** of open CORS (addressed in Phase P). 
- **Model drift** – weights are static; future re‑training not in scope.

## 26. Expected Final Architecture

```
Data (MySQL) → Full preprocessing pipeline → Feature engineering → XGBoost + CNN‑LSTM + Transformer + Autoencoder → Fusion (configurable) → Risk / Anomaly scores → SHAP & Attention explainability → API endpoints (predict, explain, attention, forecast) → MySQL persistence (predictions, model_outputs) → React UI (risk badge, explanation panels, forecast charts, NICU real‑time scores) → WebSocket alerts → Clinician review loop
```
All **[PLANNED]** blocks become operational after subsequent phases.

## 27. Files Likely to Change in Future Phases

- `ml/explainability/shap_explainer.py` (new)
- `ml/models/transformer.py` (modify to return attention & forecast head)
- `backend/app/api/endpoints/predict.py` (extend query params)
- New endpoint modules: `explain.py`, `attention.py`, `forecast.py`, `prenatal.py`.
- Frontend components: `ExplainModal.jsx`, `AttentionHeatmap.jsx`, `ForecastChart.jsx`, `FusionConfigPanel.jsx`.
- Optional config file `fusion_config.json`.
- Test suites for the above.

## 28. Files That Should NOT Be Changed

- All existing model artifact files (`*.keras`, `xgboost_model.json`, `scaler.pkl`, `ae_threshold.json`).
- Database migration scripts (no schema changes in Phase J).
- Existing FastAPI route definitions for `/predict`, `/stream`, `/alerts_ws`.
- Current React dashboard pages and styling.
- Synthetic dataset CSV files under `data/synthetic/`.
- `phase_i_report.md`, `phase_h_report.md`, and all test fixtures.

## 29. Phase J Conclusion

Phase J delivers a clear, prioritized integration roadmap that respects the prototype constraints, leverages the fully‑implemented models, and outlines concrete steps for explainability, forecasting, and real‑time NICU inference. No code has been altered; artifacts are limited to this report and a task‑list update.

---

*Prepared by Antigravity – © 2026*

