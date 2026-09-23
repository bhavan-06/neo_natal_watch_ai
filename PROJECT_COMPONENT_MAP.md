# NeoNatal Watch AI - Component Map

This document maps each major technology and feature requested in the architecture to its exact location in the repository. 

*Note: Where technologies were substituted for prototyping (e.g., SQLite instead of PostgreSQL) or are currently missing (e.g., SHAP), it is explicitly noted.*

### 1. Machine Learning Models
*   **XGBoost**
    *   Definition: `ml/models/fusion.py`
    *   Training: `ml/training/train_xgboost.py`
    *   Saved Artifact: `models/xgboost_model.json`
*   **CNN-LSTM**
    *   Definition: `ml/models/cnn_lstm.py`
    *   Training: `ml/training/train_cnn_lstm.py`
    *   Saved Artifact: `models/cnn_lstm.keras`
*   **Transformer**
    *   Definition: `ml/models/transformer.py`
    *   Training: `ml/training/train_transformer.py`
    *   Saved Artifact: `models/transformer.keras`
*   **Autoencoder**
    *   Definition: `ml/models/autoencoder.py`
    *   Training: `ml/training/train_autoencoder.py`
    *   Saved Artifact: `models/autoencoder.keras`

### 2. Explainable AI
*   **SHAP**
    *   *Status: Not Implemented*
    *   (Currently missing from the `ml/` pipeline and codebase).

### 3. Backend & API
*   **FastAPI**
    *   App Initialization: `backend/app/main.py`
    *   Routing: `backend/app/api/router.py`
    *   Endpoints: `backend/app/api/endpoints/` (e.g., `predict.py`, `chatbot.py`)
    *   Inference Logic: `backend/app/services/inference_service.py`

### 4. Database
*   **PostgreSQL**
    *   *Status: Substituted with SQLite for the academic prototype.*
    *   Connection: `backend/app/db/database.py` (points to `neonatal.db`)
    *   Schemas/Models: `backend/app/db/models.py`
    *   CRUD Operations: `backend/app/db/crud.py`

### 5. Frontend & UI
*   **React**
    *   Logic & UI Components: `frontend/app.jsx` (Using Babel standalone)
*   **Tailwind CSS**
    *   Styles: `frontend/index.html` (Imported via CDN)
*   **Recharts**
    *   *Status: Substituted with Chart.js.*
    *   Implementation: Charts are rendered inside `frontend/app.jsx` using the Chart.js CDN.

### 6. Real-Time Pipeline
*   **WebSocket / SSE**
    *   WebSocket Alert Manager: `backend/app/api/endpoints/ws_manager.py`
    *   WebSocket Route: `backend/app/api/endpoints/alerts_ws.py`
    *   SSE Data Stream: `backend/app/api/endpoints/stream.py`

### 7. Data & Validation
*   **Synthetic Data**
    *   Generation Script: *(Generated during Phase 4 notebook/script)*
    *   Storage: `data/synthetic/`
    *   Documentation: `docs/DATASET.md`
*   **Testing**
    *   Unit/Integration Tests: `tests/`
    *   Config: `pytest.ini`, `tests/conftest.py`

