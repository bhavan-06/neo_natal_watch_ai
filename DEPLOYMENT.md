# NeoNatal Watch AI — Deployment & Hosting Guide

> ⚠️ **ACADEMIC PROTOTYPE — NOT FOR CLINICAL USE**  
> Model outputs are research/academic decision-support outputs and require qualified clinician review. This software is not a certified medical device and must not be used for actual diagnosis or medical treatment.

---

## 1. System Architecture

NeoNatal Watch AI follows an integrated, micro-monolithic architectural model designed for low-latency clinical telemetry and continuous multi-model inference:

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
│ └── Transformer (0.15)│             │ └── Connection Pooling│
└───────────────────────┘             └───────────────────────┘
```

---

## 2. GitHub Repository Setup

The local git repository has been initialized with the `main` branch, safe `.gitignore`, and all necessary model artifacts.

### Pushing to Your GitHub Account

1. **Create an empty repository on GitHub**:
   - Go to [https://github.com/new](https://github.com/new)
   - Repository name: `neo_natal_watch_ai` (or your preferred name)
   - Choose **Public** or **Private**
   - **Do NOT** initialize with a README, .gitignore, or license (these already exist locally)
   - Click **Create repository**

2. **Connect and push from your local terminal**:
   ```bash
   git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/neo_natal_watch_ai.git
   git push -u origin main
   ```

3. **Verify the push**:
   - Confirm that `backend/`, `frontend/`, `models/`, `ml/`, `tests/`, and `README.md` are present on GitHub.
   - Confirm that `.env` and `neonatal.db` are **NOT** present on GitHub.

---

## 3. Frontend Hosting

- **Integrated Serving (Default & Recommended)**:  
  FastAPI serves the frontend directly from `frontend/` at the `/dashboard/` route. The application requires no external frontend hosting or Node.js build process.
- **Dynamic API Origin Resolution**:  
  `frontend/app.jsx` dynamically discovers the host API using `window.location.origin + '/api/v1'`. It works seamlessly across localhost, LAN IPs, custom domains, and cloud URLs without code modifications.

---

## 4. Backend Hosting

The backend is an ASGI application powered by Uvicorn.

### Recommended Providers:
1. **Render (Web Service)**:
   - Environment: Python 3.12
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
2. **Railway**:
   - Automatically detects the `Dockerfile` or `requirements.txt`.
   - Supports WebSocket connections natively.
3. **VPS / Self-Hosted (Ubuntu 22.04+ / Windows Server)**:
   - Run via Docker: `docker compose up -d`
   - Or run as a systemd service with Uvicorn.

---

## 5. MySQL Database Hosting

The application requires a MySQL 8.x or MariaDB database.

### Hosting Options:
- **Cloud Managed MySQL**:
  - **Aiven for MySQL** (Free tier available)
  - **Railway MySQL** (One-click add-on)
  - **Clever Cloud MySQL** (Free academic tier)
  - **AWS RDS / DigitalOcean Managed Databases**
- **Docker Compose (Local/VPS)**:
  - Run `docker compose up -d` to launch a local containerized MySQL 8 instance with volume persistence.

---

## 6. Environment Variables

Configure the following variables in your hosting provider's dashboard or local `.env`:

| Variable | Description | Example (Development) | Example (Production) |
|---|---|---|---|
| `DB_HOST` | MySQL hostname or IP | `localhost` | `mysql.provider.cloud` |
| `DB_PORT` | MySQL connection port | `3306` | `3306` |
| `DB_NAME` | Database schema name | `neonatal_watch_ai` | `neonatal_watch_ai` |
| `DB_USER` | MySQL user | `root` | `app_user` |
| `DB_PASSWORD` | MySQL password | `local_password` | `StrongRandomPassword123!` |
| `PORT` | ASGI server port | `8000` | Provided by host (`$PORT`) |
| `HOST` | Bind host address | `0.0.0.0` | `0.0.0.0` |
| `CORS_ORIGINS` | Permitted origins | `*` | `https://your-frontend.com` |

---

## 7. Local Development Execution

### 1. Start MySQL
Ensure your local MySQL service is active (via XAMPP, MySQL Workbench, or Docker):
```bash
python setup_db.py
```

### 2. Start Backend Server
```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Access Local Endpoints
- **Clinical Dashboard**: [http://localhost:8000/dashboard/](http://localhost:8000/dashboard/)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Health Check**: [http://localhost:8000/](http://localhost:8000/)

---

## 8. Production Deployment

### Option A: One-Click Docker Deployment
```bash
# Build and start all services (FastAPI app + MySQL 8 database)
docker compose up -d --build

# View container logs
docker compose logs -f
```

### Option B: Deploying on Render (Free / Academic Cloud)
1. Fork or push the repository to GitHub.
2. In [Render Dashboard](https://dashboard.render.com/), click **New +** → **Web Service**.
3. Connect your GitHub repository.
4. Set:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
5. Under **Environment Variables**, provide your MySQL connection details (`DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_PORT`).
6. Click **Create Web Service**.

---

## 9. Model Deployment

All 4 machine learning models and preprocessing scalers are bundled in `models/` (<2.5 MB total):
- `models/xgboost_model.json` (XGBoost)
- `models/cnn_lstm.keras` (CNN-LSTM)
- `models/autoencoder.keras` (Autoencoder)
- `models/transformer.keras` (Transformer)
- `models/scaler.pkl` (StandardScaler)

When the FastAPI server starts, `lifespan(app)` loads all models into memory once. No model retraining or external weights downloading occurs during deployment.

---

## 10. CORS & Network Security

`backend/app/main.py` utilizes FastAPI `CORSMiddleware`.
- In development, it defaults to `CORS_ORIGINS=*`.
- In production, set `CORS_ORIGINS=https://your-domain.com` to prevent unauthorized cross-origin requests.

---

## 11. WebSocket & SSE Telemetry

- **WebSocket Route**: `/ws/alerts` allows real-time broadcast of multi-modal deterioration alerts to attending clinicians.
- **SSE Route**: `/api/v1/stream/` streams synthetic continuous telemetry buffers to client chart components.
- Ensure reverse proxies (e.g. Nginx, Cloudflare) have WebSocket proxy headers enabled (`Upgrade`, `Connection: Upgrade`).

---

## 12. Troubleshooting

| Issue | Cause | Resolution |
|---|---|---|
| `OperationalError: (2003, "Can't connect to MySQL server")` | MySQL service offline or incorrect `DB_HOST`/`DB_PORT` | Check MySQL service status and verify `.env` credentials |
| Models fail to load on startup | Missing files in `models/` | Ensure `models/*.keras` and `models/*.json` are cloned |
| UI shows `Network Error` | API base URL unreachable | Ensure backend is running and `CORS_ORIGINS` includes origin |
| WebSocket connection fails (`1006`) | Proxy blocking WebSockets | Configure proxy to pass `Upgrade` headers |

---

## 13. Security Verification Checklist

- [x] Zero passwords committed to version control.
- [x] `.env` excluded via `.gitignore`.
- [x] `.env.example` provided with sanitized placeholders.
- [x] MySQL credentials injected via environment variables only.
- [x] No sensitive patient health information (PHI) — 100% synthetic research data.
- [x] Automated test suite verified (200/200 tests passing).

---

## 14. Academic / Demo Disclaimer

> **Synthetic / Academic Demo Data — NOT FOR CLINICAL USE**  
> All records, predictions, and vitals trajectories in this application are synthetic simulations generated for software engineering demonstration and academic research. Model outputs must be evaluated by licensed medical professionals and are not approved for clinical decision-making.

