# NeoNatal Watch AI - Project Structure

The project follows a standard, modular software engineering structure. We have avoided adding numbered prefixes (like `01_data`, `02_ml`) to the folders because standard Python packages cannot start with numbers, and changing them would break imports and violate Python best practices. 

Instead, the structure is logically separated by domain. Here is the explanation of each folder in simple English:

### `data/`
**Purpose:** Contains all project datasets and generated demo data.
*   **`raw/`**: Original, untouched data (if applicable).
*   **`processed/`**: Data that has been cleaned, scaled, and split for model training.
*   **`synthetic/`**: Simulated neonatal ICU vitals used for this academic prototype.

### `ml/`
**Purpose:** Contains preprocessing, feature engineering, training, evaluation and explainability logic.
*   **`preprocessing/`**: Scripts to clean and format raw data.
*   **`features/`**: Code to extract rolling trends and clinical indicators from vitals.
*   **`models/`**: The neural network architectures (CNN-LSTM, Autoencoder, Transformer) and XGBoost wrappers.
*   **`training/`**: Scripts to train the models on the processed data.
*   **`evaluation/`**: Code to generate metrics and plots.

### `models/`
**Purpose:** Stores the actual saved model weights (e.g., `.keras`, `.pkl`, `.json` files) after training is complete, so the backend can load them without retraining.

### `backend/`
**Purpose:** Provides the FastAPI layer between the AI models, database, and frontend.
*   **`app/api/`**: The web endpoints (routes) that the frontend talks to (e.g., `/predict`, `/chat`).
*   **`app/db/`**: Database models and CRUD (Create, Read, Update, Delete) operations.
*   **`app/schemas/`**: Data validation rules to ensure incoming data is correct.
*   **`app/services/`**: The core business logic, like running inference on the ML models.

### `frontend/`
**Purpose:** Provides the dashboard shown to the user.
*   Contains the React application (`app.jsx`) and HTML entry point. It displays live charts, risk scores, and the AI chatbot.

### `reports/`
**Purpose:** Stores model metrics, evaluation plots, and project health reports.
*   **`figures/`**: Visualizations of model performance (ROC curves, confusion matrices).
*   **`PROJECT_HEALTH_REPORT.md`**: The overall system audit and status.

### `tests/`
**Purpose:** Tests individual components and the complete system.
*   Contains Pytest scripts to verify the backend, database, schemas, and chatbot work correctly.

### `docs/`
**Purpose:** Contains architecture and technical documentation.
*   **`DATASET.md`**: Details about the synthetic data used in this prototype.

### `scripts/`
**Purpose:** Helper scripts to run specific tasks, like generating data, training models, or running automated API tests.

### `notebooks/`
**Purpose:** Jupyter notebooks used for initial data exploration, prototyping, and step-by-step experimentation before moving code to the `ml/` folder.

