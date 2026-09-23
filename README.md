# NeoNatal Watch AI

> ⚠️ **ACADEMIC PROTOTYPE — NOT FOR CLINICAL USE**
>
> This software is an academic and research demonstration prototype developed for longitudinal maternal-fetal-neonatal risk monitoring.
> It must **NOT** be used for real clinical diagnosis, medical triage, or patient treatment.
> All risk scores, alerts, model explanations, and decision-support summaries are synthetic demonstration outputs and require licensed clinician evaluation.

---

## 🏥 Project Overview

**NeoNatal Watch AI** is an end-to-end longitudinal clinical decision support platform that connects maternal-fetal prenatal surveillance with continuous Neonatal Intensive Care Unit (NICU) physiological telemetry and multi-modal artificial intelligence.

The platform links the complete care continuum:
```
Patient (Mother)
  ↓
Maternal Profile (Demographics, MAP, Chronic Conditions)
  ↓
Pregnancy Record (Conception, EDD, Status)
  ↓
Trimester 1 Assessment (CRL, NT, Biomarkers: PAPP-A, PlGF)
  ↓
Trimester 1 Prenatal Prediction (EFW Percentile Target)
  ↓
Trimester 2 Assessment (Actual EFW, Ultrasound, Uterine/Umbilical Doppler)
  ↓
Growth Variance Analysis (Delta %ile, Adaptive Deviation Flag, Contributing Pattern)
  ↓
Clinician Review & Prescriptions (Doctor Notes, Surveillance)
  ↓
Birth & Newborn Record (Gestational Age, Birth Weight, APGAR)
  ↓
NICU Admission (Reason, Status)
  ↓
Real-Time Telemetry (Heart Rate, SpO2, Respiratory Rate, Core Temperature)
  ↓
60-Minute Real-Time Buffer (Sliding Window Ingestion)
  ↓
Multi-Model Machine Learning Inference (XGBoost, CNN-LSTM, Autoencoder, Transformer)
  ↓
Risk Fusion (Weighted Ensemble: 0.35 / 0.30 / 0.20 / 0.15)
  ↓
Three-Tier Explainability & Limitation Auditing:
  ├── TreeSHAP (XGBoost Structured Feature Importance)
  ├── Reconstruction Error Breakdown (Autoencoder Anomaly Explanation)
  ├── Multi-Head Self-Attention Weights (Transformer Temporal Importance)
  └── Multi-Horizon Forecasting Audit (Truthful Limitation Reporting)
  ↓
Alerting System (WebSocket Deduplication & Notification)
  ↓
Interactive Clinical Dashboard (Priority Patients Table, Vital Telemetry, Timeline)
```

---

## 🏗️ Architecture

```
                  ┌─────────────────────────────────────────┐
                  │       Clinician / Admin Browser         │
                  │   High-Contrast React Clinical Dashboard│
                  └────────────────────┬────────────────────┘
                                       │ HTTP / WS / SSE
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │       FastAPI ASGI Server (Port 8000)   │
                  │  ├── REST API (/api/v1)                 │
                  │  ├── Static UI Mount (/dashboard)       │
                  │  ├── Real-time Alerts (/ws/alerts)      │
                  │  └── Vitals Telemetry SSE (/stream)     │
                  └────────────┬────────────────────────────┘
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
┌───────────────────────┐             ┌───────────────────────┐
│  Multi-Model ML Engine│             │ MySQL 8.x Persistence │
│ ├── XGBoost (0.35)    │             │ ├── 16 Relational     │
│ ├── CNN-LSTM (0.30)   │             │ │   Clinical Tables   │
│ ├── Autoencoder (0.20)│             │ ├── SQLAlchemy ORM    │
│ └── Transformer (0.15)│             │ └── Alembic Versioning│
└───────────────────────┘             └───────────────────────┘
```

---

## 💻 Technology Stack

| Layer | Technologies |
|---|---|
| **Backend Framework** | FastAPI 0.115+, Uvicorn (ASGI) |
| **Language Runtime** | Python 3.12 |
| **Relational Database** | MySQL 8.0+ / MariaDB via SQLAlchemy 2.0 & PyMySQL |
| **Machine Learning** | TensorFlow / Keras 3.x, XGBoost, Scikit-learn, NumPy, Pandas |
| **Explainability** | SHAP (TreeExplainer), Autoencoder MSE Decomposition, Self-Attention Weight Extraction |
| **Frontend UI** | React 18, Babel Standalone, Tailwind CSS, Chart.js, FontAwesome 6 |
| **Streaming & Push** | Server-Sent Events (SSE), WebSockets (`/ws/alerts`) |
| **Testing** | pytest, pytest-asyncio, HTTPX / Starlette TestClient (200 automated tests) |

---

## ⚙️ Local Setup

### Prerequisites
- Python 3.11 or 3.12
- MySQL Server 8.0+
- Git

### 1. Clone Repository
```bash
git clone <GITHUB_REPOSITORY_URL>
cd neo_natal_watch_ai
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Copy the provided `.env.example` template to `.env`:
```bash
cp .env.example .env
```

Configure your parameters in `.env`:
```ini
# Database Configuration (MySQL 8.x)
DB_HOST=localhost
DB_PORT=3306
DB_NAME=neonatal_watch_ai
DB_USER=root
DB_PASSWORD=your_secure_password_here

# Test Database (Pytest runner)
TEST_DB_NAME=test_neonatal_watch_ai

# Server Host and Port
HOST=0.0.0.0
PORT=8000

# CORS Allowed Origins (* for local development)
CORS_ORIGINS=*
```

---

## 🗄️ Database Setup

Ensure MySQL service is active, then initialize the database schema:
```bash
python setup_db.py
```
*Note: When FastAPI starts up, SQLAlchemy (`Base.metadata.create_all`) will automatically ensure all 16 clinical tables exist.*

---

## 🚀 Running Backend

Start the FastAPI application with Uvicorn:
```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive API documentation will be available at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/](http://localhost:8000/)

---

## 🖥️ Running Frontend

The frontend is an integrated single-page application mounted directly inside the FastAPI backend.
Once the backend is running, access the dashboard at:
👉 **[http://localhost:8000/dashboard/](http://localhost:8000/dashboard/)**

No separate Node.js build step is required. The UI automatically runs via React 18, Babel Standalone, and Tailwind CSS.

---

## 🧪 Running Tests

The test suite consists of **200 automated tests** covering end-to-end integration, ML inference, API endpoints, explainability, streaming, and database schema:

```bash
python -m pytest tests/ -v
```

Expected result:
```
============================== 200 passed in ~58s ==============================
```

---

## 🤖 ML Models & Artifacts

All models are pre-trained and version-controlled under `models/`:

| Artifact | Architecture | Input Shape / Sequence | Role |
|---|---|---|---|
| `xgboost_model.json` | Gradient Boosted Trees | 48 Tabular Features | Structured patient & vitals risk |
| `cnn_lstm.keras` | 1D-CNN + LSTM | (Batch, 30, 4) | Temporal sequence deterioration |
| `autoencoder.keras` | Conv1D Encoder-Decoder | (Batch, 30, 4) | Anomaly detection via MSE loss |
| `transformer.keras` | Multi-Head Attention | (Batch, 30, 4) | Temporal feature self-attention |
| `scaler.pkl` | StandardScaler | 4 continuous vitals | HR, SpO2, RR, Temperature scaling |

---

## 🌐 Deployment

### Recommended Cloud Architecture
The application is ready for deployment on platforms supporting Python 3.12 containers and managed MySQL (e.g., Render, Railway, AWS ECS, Fly.io):

1. **Backend & Frontend Web Service**:
   - Runtime: Python 3.12
   - Start Command: `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
   - Static Mount: `/dashboard` serves the React frontend seamlessly.
2. **Managed MySQL Database**:
   - Provision a MySQL 8.x database instance.
   - Configure `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD` in the cloud environment settings.
3. **CORS Security**:
   - Set `CORS_ORIGINS=https://your-domain.com` in production environment variables.

---

## 🔗 Live Demo & Links

- **Local Dashboard**: [http://localhost:8000/dashboard/](http://localhost:8000/dashboard/)
- **Live Deployment**: Configurable per deployment environment (see `DEPLOYMENT.md`)
- **API Health Probe**: [http://localhost:8000/](http://localhost:8000/)

---

## 📁 GitHub Repository

- **Repository**: Configured on remote `origin`
- **Main Branch**: `main`

---

## 🔒 Academic / Safety Disclaimer

> **IMPORTANT CLINICAL NOTICE**
> 
> "Synthetic / Academic Demo Data — NOT FOR CLINICAL USE"
>
> All patients, pregnancies, vitals measurements, and clinical records contained in this platform are synthetically generated for academic demonstration and software validation purposes. Model outputs, anomaly indicators, SHAP explanations, and attention distributions are research decision-support outputs and require licensed clinician review. This software does not provide medical diagnoses or replace clinical judgment.
