# NeoNatal Watch AI
## Project Health Report

### 1. Overall Status

NEEDS FIXES 

While the core machine learning models and API are functional, there are several missing features and discrepancies between the intended architecture and the actual implementation. The project is an academic prototype and is NOT ready for clinical production.

### 2. Architecture Status

The project roughly follows the intended architecture.
However, several expected files/folders are missing or incorrectly placed:
* `docs/` folder is empty.
* `MODEL_CARD.md` is missing.
* `docker-compose.yml` is missing.
* `reports/` folder contains only figures, no written reports.
* The frontend is built as a single `index.html` with an `app.jsx` file utilizing Babel standalone instead of a full React build setup, which is fine for a quick prototype but not scalable.

### 3. Backend Status

PARTIALLY WORKING

The FastAPI backend starts successfully.
The following endpoints exist and work:
* `GET /` (Health check)
* `POST /api/v1/predict/` (Generates predictions)
* `GET /api/v1/stream/` (SSE mock data stream)
* `POST /api/v1/chat/` (Prototype Chatbot)
* `WS /ws/alerts` (WebSocket for alerts)

The following endpoints are **MISSING**:
* `GET /patients`
* `GET /patients/{patient_id}`
* `GET /patients/{patient_id}/vitals`
* `GET /patients/{patient_id}/risk`
* `GET /patients/{patient_id}/timeline`
* `POST /forecast`
* `POST /anomaly`
* `GET /alerts`

### 4. Database Status

WORKING (using SQLite instead of PostgreSQL)

The backend uses SQLite (`neonatal.db`) instead of the intended PostgreSQL. 
* Connection, tables, relationships, and CRUD operations exist.
* Tables created: `patients`, `vital_signs`, `predictions`.
* Missing expected tables: `alerts`, `model_outputs`, `clinical_events`, `users`.
* Credentials are not hard-coded (SQLite doesn't require them).

### 5. ML Status

WORKING 

The ML pipeline works end-to-end:
* Models trained and saved: XGBoost, CNN-LSTM, Autoencoder, Transformer.
* The `InferenceService` successfully loads all models and scalers into memory.
* Prediction inference correctly processes sequence data and flat features.

STATUS:
* XGBoost: WORKING
* CNN-LSTM: WORKING
* Autoencoder: WORKING
* Transformer: WORKING

### 6. Dataset Status

WORKING

* `DATASET.md` exists and clearly documents the dataset strategy.
* The dataset used is marked clearly as SYNTHETIC.
* Synthetic data is stored in `data/synthetic/` and not misrepresented as real clinical data.

### 7. Model Evaluation Status

WORKING

* The project successfully logs metrics and generates evaluation plots.
* `reports/figures/` contains ROC-AUC, PR-AUC, Confusion Matrix plots for all models.

### 8. Explainability Status

NOT IMPLEMENTED

* There is no SHAP implementation found in the project.
* `shap` is not imported or used in the `ml/` codebase or notebooks.
* Explanations regarding feature importance contributions (e.g., "SpO2 trend contributed positively") are missing from both the ML pipeline and the Chatbot.

### 9. Frontend Status

PARTIALLY WORKING

* The frontend is a standalone `index.html` and `app.jsx` file using Babel and Chart.js.
* It successfully displays risk scores and model breakdowns.
* It lacks specific expected components: patient list, patient detail, anomaly score, forecast, and SHAP explanation.
* It does not fully integrate the SSE vital sign stream (`/api/v1/stream/`) for chart updates; instead, it uses a one-off mock data generator on button click.

### 10. Real-Time Pipeline Status

PARTIALLY WORKING

* Data simulator (SSE) exists in the backend.
* WebSocket alert system works.
* The frontend does not actively consume the SSE stream for live charting, making the "real-time" aspect mostly simulated on button click.

### 11. Chatbot Status

PARTIALLY WORKING

* The chatbot is a rule-based prototype, not an LLM.
* It correctly retrieves risk scores, SpO2, and Heart Rate from the database.
* It fails to answer advanced queries like "Which signals contributed most?" (due to missing SHAP/explainability).
* It does not invent patient information or recommend treatment.

### 12. Security Status

WORKING

* No hard-coded secrets or credentials found.
* `.env.example` exists.

### 13. Testing Status

WORKING

* The pytest suite is well-configured.
* 49 tests run successfully, covering schemas, CRUD operations, backend health, prediction, and chatbot endpoints.
* A minor issue with test database file locking (`WinError 32`) on teardown was identified and fixed.

### 14. Documentation Status

NEEDS FIXES

* `README.md` and `DATASET.md` exist.
* `MODEL_CARD.md` is missing.
* The documentation mentions missing features (like SHAP explainability and PostgreSQL).
* The documentation explicitly states that this is an academic prototype and not for clinical use.

### 15. Build Status

WORKING

* Backend API starts successfully using `uvicorn backend.app.main:app`.
* Frontend loads successfully in a browser.
* Tests run and pass.

### 16. Issues Found

* **File:** `backend/app/api/endpoints/predict.py`, etc.
  **Problem:** Missing several REST endpoints (`/patients`, `/forecast`, `/anomaly`, `/alerts`).
  **Severity:** Medium
  **Recommended fix:** Implement missing endpoints as outlined in the initial architecture.

* **File:** `ml/` codebase
  **Problem:** SHAP and Explainable AI components are entirely missing.
  **Severity:** High
  **Recommended fix:** Implement SHAP for XGBoost and deep learning models to extract feature importance.

* **File:** `frontend/app.jsx`
  **Problem:** The frontend doesn't use the SSE stream (`/api/v1/stream/`) for live data updates.
  **Severity:** Medium
  **Recommended fix:** Replace the `generateMockData` function with an `EventSource` listener that consumes the SSE endpoint.

* **File:** Project Root
  **Problem:** `MODEL_CARD.md` and `docker-compose.yml` are missing.
  **Severity:** Low
  **Recommended fix:** Create these files to match the expected architecture.

### 17. Features Working

* ML model training and inference (XGBoost, CNN-LSTM, Autoencoder, Transformer)
* SQLite database integration and CRUD operations
* FastAPI backend with prediction and chatbot endpoints
* WebSocket alert broadcasting
* Standalone React dashboard with Chart.js visualizations
* Comprehensive Pytest suite

### 18. Features Missing

* SHAP / Explainable AI
* Complete REST API for Patients, Forecasts, and Alerts
* Live SSE data streaming integration in the Frontend
* PostgreSQL database implementation
* `MODEL_CARD.md` and Docker setup

### 19. Production Readiness

ACADEMIC DEMO READY

This project is in a functional state for academic demonstration purposes, showcasing a hybrid machine learning pipeline and a real-time risk assessment API. 

It is strictly **NOT** REAL CLINICAL PRODUCTION READY. It lacks clinical validation, utilizes synthetic data, and is a prototype meant for research evaluation only.

