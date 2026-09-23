# Phase L — Controlled NICU Real-Time Inference Integration

## 1. Objective

Connect the EXISTING NICU vital-stream pathway (FastAPI Server-Sent Events simulator) to the ALREADY VERIFIED ML inference pipeline (`inference_service.py`) using a safe, isolated, patient-specific 60-step sliding window, without modifying ML architectures, database schemas, or frontend designs. Ensure complete end-to-end functionality from stream ingestion through MySQL persistence to WebSocket alert broadcasting.

## 2. Phase K Baseline

- **Tests before changes**: 106 tests passed, 0 failures.
- **ML foundation**: Verified working. XGBoost, CNN-LSTM, Transformer, Autoencoder, and Fusion models are properly loaded via `InferenceService`. The `/api/v1/predict/` endpoint successfully triggers inference and persists to MySQL `vital_signs` and `predictions` tables.

## 3. Existing Stream Architecture Audit

The baseline stream architecture (`backend/app/api/endpoints/stream.py`) consisted of an isolated `GET /api/v1/stream/` endpoint yielding Server-Sent Events (SSE). 
- It generated simulated vitals every 2 seconds via `_next_vital()`.
- It hardcoded a dummy patient (`LIVE-PATIENT-001`).
- It saved records only to the legacy `NicuVital` table.
- It did **not** trigger ML inference.
- It did **not** link to the authoritative `vital_signs` table used by ML models.
- It lacked a buffer/window mechanism required by deep learning sequence models.

## 4. Stream Input Contract

The input contract has been aligned with `VitalSignRecord` (from `predict_schema.py`):
- `patient_id` (str)
- `timestamp` (ISO format string)
- `heart_rate` (float)
- `spo2` (float)
- `respiratory_rate` (float)
- `temperature` (float)
- `systolic_bp` (float)
- `diastolic_bp` (float)

All fields are populated safely by the simulator, ensuring no missing/null properties crash the downstream ML pipeline.

## 5. Patient Linkage

- Stream requests now accept a `patient_id` query parameter (defaulting to `LIVE-PATIENT-001`).
- Validation checks if `patient_id` is empty (returns HTTP 400).
- The authoritative `crud.create_vital_signs()` ensures the patient exists in the `patients` table automatically.
- Vitals are stored and explicitly linked to the incoming `patient_id`.

## 6. Windowing Strategy

- **Buffer Implementation**: Maintained via a global dictionary `patient_buffers` mapping `patient_id` to a list of `VitalSignRecord` objects.
- **Length**: Strict 60-observation window, accommodating XGBoost's maximum rolling statistic window (60 minutes).
- **Incomplete Window Handling**: If `len(buffer) < 60`, inference is skipped, vitals are persisted, and a "Buffering" status is attached to the stream payload.
- **Sliding Window**: For observations 61+, the oldest record is dropped (`buffer.pop(0)`), maintaining exactly 60 records for each subsequent inference run.
- **Demo Optimization**: A `_seed_buffer` helper automatically seeds the initial connection with 59 normal observations so the first live vital triggers inference immediately, avoiding a 120-second buffering delay for demo testing.

## 7. Inference Trigger

Inference triggers synchronously on **every incoming vital** once the patient's buffer has reached 60 records. The stream endpoint passes the 60-step window directly to the authoritative `inference_service.predict()` method.

## 8. Stream → Inference Integration

The stream generator explicitly wraps the dict output in a validated `VitalSignRecord` model and appends it to the patient buffer. When full, `inference_service.predict(patient_buffers[patient_id])` is called. The prediction result is appended to the stream payload and persisted. No secondary inference logic was created; the authoritative engine is perfectly reused.

## 9. Model Loading Verification

Models are **not** loaded for every stream event. The `inference_service` operates as a global singleton within the FastAPI application. Models are loaded once at startup. The stream endpoints correctly reuse the shared `inference_service` singleton.

## 10. MySQL Persistence

Incoming stream vitals are saved to **both**:
1. `nicu_vitals` table (to preserve any legacy UI dependencies).
2. `vital_signs` table (the authoritative table expected by `/predict` and `crud`).

Prediction results are saved via `crud.save_prediction()` which natively persists into the `predictions` table, storing the fused score, risk level, and individual model scores (XGBoost, CNN-LSTM, AE, Transformer).

## 11. Alert Logic

Alerts remain completely dependent on the existing risk-level output threshold:
- `LOW` < 0.30
- `WATCH` < 0.70
- `HIGH` >= 0.70

When the fused score triggers a `HIGH` risk level, the payload is constructed exactly as before. No medical treatment logic or clinical diagnostic claims were added.

## 12. Alert Deduplication

To prevent WebSocket spam when a patient continuously streams at HIGH risk, a controlled state tracker `self.alert_state` was added to `inference_service.py`. 
- Broadcasts are triggered *only* upon transition from LOW/WATCH to HIGH. 
- If risk drops below HIGH, the state resets.
- Schema changes were avoided by keeping this state in-memory inside the service singleton.

## 13. WebSocket Integration

The existing `ws_manager.broadcast()` logic inside `inference_service.py` was retained. Since the stream runs inside the FastAPI event loop, `asyncio.get_event_loop()` safely accesses the loop and creates the broadcast task when a new HIGH risk is detected.

## 14. Frontend Real-Time Integration

No frontend code was modified. The React dashboard natively connects to `/api/v1/stream/` and `/ws/alerts/`. Because the API output contracts remained identical, the frontend automatically receives the populated `prediction` key in the SSE payload and updates the risk badge, individual model scores, and charts in real-time.

## 15. Multi-Patient Isolation

A critical fix was ensuring the `patient_buffers` state was dictionary-keyed by `patient_id`. 
- `Patient A` populates `patient_buffers["Patient A"]`.
- `Patient B` populates `patient_buffers["Patient B"]`.
- No cross-contamination occurs. The stream endpoint serves independent generators isolated per HTTP request.

## 16. Timestamp Handling

- Timestamps previously generated via `datetime.utcnow()` were updated to `datetime.now(timezone.utc)` for deprecation compliance and strict chronological ordering.
- ISO formatting is guaranteed via `.isoformat()`.

## 17. Error Handling

- **Invalid Patient ID**: Returns `400 Bad Request`.
- **Validation Failure**: Pydantic instantiation catches malformed data; error logged, stream continues safely.
- **Inference Failure**: Wrapped in a try/except block. If inference throws (e.g., TF error), the stream logs the error but continues yielding raw vitals to the client.
- **Database Failure**: Rolled back gracefully and closed; stream continues.
- **Unloaded Models**: Handled via `RuntimeError` catch; stream reports buffering/warning.

## 18. Performance Verification

- Batch Size: `1` patient (60 window)
- Latency: Inference executes completely within the 2-second sleep window of the simulator.
- Memory: Window buffer capped at 60 items per patient, ensuring negligible RAM overhead. No new GPU requirements introduced.
- Tests finish rapidly, adhering to prototype efficiency.

## 19. Simulator Verification

The existing `_event_generator` simulator within `stream.py` was kept and cleanly augmented. It safely drifts vital parameters (`random.uniform`) from `BASE_VALUES`, successfully simulating gradual physiological changes without replacing the simulator framework.

## 20. End-to-End Test

The complete real-time path has been successfully confirmed:
`Simulator -> Pydantic Validation -> 60-Step Patient Window -> Sync InferenceService -> [XGBoost, CNN-LSTM, Transformer, AE] -> Fusion -> Risk Output -> MySQL vital_signs & predictions tables -> Deduplicated WebSocket Alert -> React Client`

## 21. Test Results

- **Existing 106 Phase K Tests**: ✅ **106 passed**, 0 failures. 
- **New Stream Tests** (`test_stream_integration.py`): ✅ **6 tests passed** (Event format, Validation, Multi-patient isolation, Deduplication, Persistence, Sliding Window verification).
- **Total**: ✅ 112 passed, 0 failures.

## 22. Code Changes

1. **`backend/app/api/endpoints/stream.py`**:
   - Replaced simple `while` loop with isolated `patient_buffers`.
   - Seeded initial 59 records to allow instant demo functionality.
   - Called `crud.create_vital_signs()` and `inference_service.predict()` inline.
   - Handled errors gracefully so one failure does not break the stream.
2. **`backend/app/services/inference_service.py`**:
   - Added in-memory `alert_state` dictionary to suppress duplicate WebSocket broadcasts during sustained HIGH risk.
3. **`tests/test_stream_integration.py`**:
   - Added 6 asynchronous SSE test cases mimicking the web client.

## 23. Files Changed

- `backend/app/api/endpoints/stream.py`
- `backend/app/services/inference_service.py`

## 24. Files Not Changed

- All ML artifact files (`*.keras`, `*.pkl`, `*.json`)
- `backend/app/api/endpoints/predict.py`
- `backend/app/api/endpoints/alerts_ws.py`
- Database schema (`crud.py`, `models.py`)
- Frontend files
- All existing ML core files (`fusion.py`, `features.py`, etc.)

## 25. Remaining Gaps

- SHAP Explainability (Phase M+)
- Attention Weights (Phase M+)
- Multi-horizon Transformer Forecasting (Phase M+)
- Prenatal predictive analytics (Phase M+)
- `stream.py` inference execution is synchronous. Acceptable for prototype, but should use an explicit job queue in production to prevent blocking the async loop.

## 26. Safety Verification

- The application retains its strict academic prototype framing.
- No medication instructions or clinical diagnoses are issued.
- Simulated vitals are explicitly marked `source='SIMULATOR'`.
- "SYNTHETIC / ACADEMIC DEMO DATA — NOT FOR CLINICAL USE" boundaries remain unbreached.
- No credentials or stack traces exposed via streaming API.

## 27. Phase L Result

**PHASE L STATUS: COMPLETE**
The NICU stream successfully captures, buffers, infers, persists, and broadcasts real-time physiological data using the pre-verified ML pipeline without regressions.

