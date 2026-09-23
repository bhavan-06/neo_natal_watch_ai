# NeoNatal Watch AI - Project Tree

Below is the clean visual representation of the **actual** folder structure in the repository. We retain the standard Python module names (e.g., `ml`, `backend`) to ensure all imports and the API remain functional.

```text
neo_natal_watch_ai/
│
├── data/                    → Dataset and demo data
│   ├── processed/           → Cleaned, scaled, and split matrices (npy/csv)
│   ├── raw/                 → Original raw data (empty placeholder)
│   └── synthetic/           → Generated synthetic neonatal vitals for prototype
│
├── ml/                      → AI/ML pipeline
│   ├── evaluation/          → Calculates performance metrics
│   ├── features/            → Feature engineering and rolling trends
│   ├── models/              → Neural network architectures and XGBoost wrappers
│   ├── preprocessing/       → Cleans, formats, and windows data
│   └── training/            → Scripts to train each ML model
│
├── models/                  → Saved model weights (.keras, .json, .pkl)
│
├── backend/                 → FastAPI backend
│   └── app/
│       ├── api/             → REST endpoints and WebSocket routes
│       ├── db/              → Database models and CRUD operations
│       ├── schemas/         → Pydantic validation schemas
│       └── services/        → Core logic (e.g., Inference service)
│
├── frontend/                → React dashboard UI
│   ├── app.jsx              → Main React application logic
│   └── index.html           → HTML entry point with CDN links
│
├── tests/                   → Automated Pytest test suite
│
├── reports/                 → Metrics and reports
│   ├── figures/             → Saved evaluation plots (ROC, PR curves)
│   └── PROJECT_HEALTH_REPORT.md → System health and audit report
│
├── docs/                    → Technical documentation
│   └── DATASET.md           → Details about the synthetic dataset
│
├── scripts/                 → Helper and test execution scripts
│
├── notebooks/               → Jupyter notebooks for initial step-by-step experimentation
│
├── config.yaml              → Project-wide configuration parameters
├── pytest.ini               → Pytest configuration
├── requirements.txt         → Python dependency list
├── CLEANUP_REPORT.md        → Record of removed temporary/obsolete files
├── PRESENTATION_FLOW.md     → Step-by-step presentation narrative
├── PROJECT_STRUCTURE.md     → Detailed textual explanation of folders
└── README.md                → Project introduction
```

