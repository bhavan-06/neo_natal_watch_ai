# NeoNatal Watch AI — Deployment & Architecture Audit

## 1. Executive Summary
This audit inspects the complete codebase of **NeoNatal Watch AI** to determine the exact requirements, configurations, dependencies, security surface, and deployment architecture for publishing to GitHub and hosting the application.

---

## 2. Technology Stack & Runtime Environment

| Component | Technology | Version / Configuration | Notes |
|---|---|---|---|
| **Operating System** | Windows | 10 / 11 | Host dev environment |
| **Python Runtime** | Python | 3.12.1 | Standard 64-bit CPython |
| **Node.js / npm** | None / In-browser CDN | N/A | Frontend uses React 18 & Babel standalone; no Node.js build step required |
| **Package Manager** | pip | `requirements.txt` | Standard Python dependency management |
| **Backend Framework** | FastAPI | 0.115.0+ | ASGI web API framework |
| **ASGI Server** | Uvicorn | Standard | Command: `uvicorn backend.app.main:app --host 0.0.0.0 --port 8000` |
| **Frontend Framework** | React 18 | CDN (React, ReactDOM, Babel Standalone) | Located in `frontend/index.html` & `frontend/app.jsx` |
| **Styling** | Tailwind CSS | CDN with Tailwind JIT script | Custom healthcare palette & dark/light theme |
| **Charting** | Chart.js | 4.x CDN | Canvas-rendered vital trends (HR, SpO2, RR, Temp) |
| **Database** | MySQL | 8.x via PyMySQL & SQLAlchemy | Relational persistence for 16 models |
| **Migrations** | Alembic | Configured (`alembic.ini`) | Schema tracking under `migrations/` |
| **Real-Time Streaming** | SSE + WebSockets | FastAPI endpoints | `/api/v1/stream/` (SSE) & `/ws/alerts` (WS) |

---

## 3. Machine Learning Models & Artifacts

All models are trained, validated, and persisted under `models/`. Their storage footprint is compact:

| Model | File | Format | File Size | Role |
|---|---|---|---|---|
| **XGBoost** | `models/xgboost_model.json` | JSON | 81.4 KB | Tabular clinical risk scoring (35% fusion) |
| **Feature List** | `models/xgb_features.json` | JSON | 2.3 KB | Feature column order for XGBoost |
| **CNN-LSTM** | `models/cnn_lstm.keras` | Keras v3 / HDF5 | 585.3 KB | Deep temporal sequence classification (30% fusion) |
| **Transformer** | `models/transformer.keras` | Keras v3 / HDF5 | 1.28 MB | Multi-head self-attention sequence classifier (15% fusion) |
| **Autoencoder** | `models/autoencoder.keras` | Keras v3 / HDF5 | 112.8 KB | Normative vital pattern reconstruction (20% fusion) |
| **AE Threshold** | `models/ae_threshold.json` | JSON | 43 B | Anomaly reconstruction error cutoff |
| **Scaler** | `models/scaler.pkl` | Pickle | 1.2 KB | Standard scaler for vitals sequence normalization |

**Total Model Footprint:** ~2.06 MB.  
**Git & Hosting Implication:** All model artifacts are well below GitHub's 100 MB file limit and require no Git LFS or external bucket storage. They can be safely tracked and deployed directly with the codebase.

---

## 4. Frontend & Backend Serving Architecture

1. **Integrated Static Mounting:**
   FastAPI mounts the frontend static directory directly:
   ```python
   app.mount("/dashboard", StaticFiles(directory="frontend", html=True), name="dashboard")
   ```
   Visiting `/dashboard` serves `frontend/index.html` which loads `frontend/app.jsx` in the browser.
2. **API Base URL:**
   Currently `app.jsx` uses `const API = 'http://localhost:8000/api/v1';`.  
   For hosting, this should dynamically detect `window.location.origin + '/api/v1'` so that it works seamlessly whether hosted on `localhost` or a public cloud provider.
3. **CORS:**
   `backend/app/main.py` has `CORSMiddleware`. We will allow setting `CORS_ORIGINS` via environment variables for strict production security while maintaining developer ergonomics.

---

## 5. Database Configuration & Credentials

- Database connection string in `backend/app/db/database.py`:
  ```python
  SQLALCHEMY_DATABASE_URL = f'mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
  ```
- Local `.env` contains:
  ```env
  DB_HOST=localhost
  DB_PORT=3306
  DB_NAME=neonatal_watch_ai
  DB_USER=root
  DB_PASSWORD=your_password_here
  ```
- **Security Check:** The `.env` file contains credentials and MUST NOT be committed to Git. A sanitized `.env.example` must be created.
- **Report Audit:** `phase_h_report.md` previously contained a plaintext mention of the local password, which will be redacted.

---

## 6. Git Status

- Git executable: `git version 2.55.0.windows.5`.
- Status: Git repository has not been initialized yet in `c:\project\neo_natal_watch_ai`.
- Action required:
  - Initialize repository (`git init -b main`).
  - Configure `.gitignore` to prevent secret leaks and keep ML model artifacts.
  - Review staged files.
  - Create deployment commit.
  - Configure GitHub remote and push.

---

## 7. Hosting & Deployment Strategy

### Deployment Architecture
```
[ User Browser / Clinician Dashboard ]
                 │
                 ▼
[ Cloud Application Host (FastAPI + Static Frontend) ]
        │                       │
        ▼                       ▼
[ ML Inference Engine ]   [ Managed MySQL Database ]
(Embedded inside Python)  (Local or Cloud Provider)
```

1. **Option A: Containerized / Cloud Service (Docker / Render / Railway / Fly.io):**
   - Single container or Python service running Uvicorn.
   - Uvicorn serves both `/api/v1` REST + WebSocket `/ws/alerts` + `/dashboard` static UI.
   - Connects to MySQL via `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`.
2. **Option B: Local / On-Premises Production:**
   - Run `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000`.
   - Access dashboard at `http://<SERVER_IP>:8000/dashboard/`.

---

## 8. Audit Findings & Next Steps

1. **Create `.env.example`:** Provide clean placeholder template for database and server variables.
2. **Update `.gitignore`:** Remove `models/*.keras` and `models/*.json` from `.gitignore` so the required models are packaged and deployed. Keep `.env` strictly ignored.
3. **Make Frontend API Base URL Environment-Aware:** Update `app.jsx` line 5 to use dynamic origin.
4. **Make Backend Configurable:** Support `PORT` and `CORS_ORIGINS` environment variables in `backend/app/main.py`.
5. **Redact Credential in Report:** Clean `phase_h_report.md`.
6. **Initialize Git, Stage Clean Files, and Commit:** Validate with `git status` that zero secrets are staged.
7. **Push to GitHub & Provide Deployment Documentation.**
