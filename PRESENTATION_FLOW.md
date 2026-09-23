# NeoNatal Watch AI - Presentation Flow

This document outlines the step-by-step presentation flow of the NeoNatal Watch AI project. It explains the journey from the initial problem to the final real-time dashboard in simple English.

---

### 1. Problem
*   **WHAT:** Neonatal Intensive Care Units (NICUs) produce massive amounts of vital sign data. It's hard for human nurses to notice subtle, slow deteriorations in a baby's health before a critical event happens.
*   **WHY:** Early warning systems can alert staff *before* an emergency, potentially saving lives.
*   **INPUT:** The clinical need for predictive monitoring.
*   **PROCESS:** Defining the project goals to predict risk based on vital signs.
*   **OUTPUT:** Project scope.
*   **NEXT STEP:** Gathering data to train the AI.

### 2. Input data
*   **WHAT:** We use a synthetic dataset that mimics real neonatal vital signs (Heart Rate, SpO2, Respiratory Rate, Temperature, Blood Pressure).
*   **WHY:** Real medical data is highly restricted. Synthetic data lets us build and prove the software architecture safely.
*   **INPUT:** Medical literature on normal and abnormal neonatal vital ranges.
*   **PROCESS:** Generating time-series data with normal periods and sudden deterioration events.
*   **OUTPUT:** Raw CSV files of vital signs.
*   **NEXT STEP:** Loading this data into the system.

### 3. Data ingestion
*   **WHAT:** Reading the raw data files into the machine learning pipeline.
*   **WHY:** The models need data in computer memory (DataFrames) to analyze it.
*   **INPUT:** Raw CSV files.
*   **PROCESS:** Loading files, checking for missing values, and sorting by timestamp.
*   **OUTPUT:** A unified, clean dataset in memory.
*   **NEXT STEP:** Preparing the data for machine learning.

### 4. Preprocessing
*   **WHAT:** Scaling the numbers and splitting the data.
*   **WHY:** Neural networks learn better when all numbers are scaled (e.g., between 0 and 1). We also must split data into Training (to learn) and Testing (to verify) sets so the model doesn't "cheat".
*   **INPUT:** Cleaned raw data.
*   **PROCESS:** Normalization (StandardScaler) and sequence windowing (creating 60-minute chunks of time).
*   **OUTPUT:** `X_train`, `X_test` matrices.
*   **NEXT STEP:** Extracting advanced features.

### 5. Feature engineering
*   **WHAT:** Creating new data points from existing ones, like "Heart Rate variability over the last 15 minutes."
*   **WHY:** Raw numbers aren't always enough. Trends and changes over time are stronger indicators of health.
*   **INPUT:** Preprocessed vital signs.
*   **PROCESS:** Calculating rolling means, standard deviations, and missingness flags.
*   **OUTPUT:** A dataset enriched with statistical trends.
*   **NEXT STEP:** Training the first AI model.

### 6. XGBoost
*   **WHAT:** A powerful machine learning algorithm based on decision trees.
*   **WHY:** It is excellent at finding patterns in tabular data and statistical features.
*   **INPUT:** The engineered features.
*   **PROCESS:** Training the model to recognize which features lead to deterioration.
*   **OUTPUT:** A trained XGBoost model.
*   **NEXT STEP:** Training deep learning models for sequence data.

### 7. CNN-LSTM
*   **WHAT:** A deep learning neural network (Convolutional Neural Network + Long Short-Term Memory).
*   **WHY:** CNNs are great at finding local patterns (like a sudden spike), and LSTMs are great at remembering long-term trends over the 60-minute window.
*   **INPUT:** 3D sequences of vitals (Time chunks).
*   **PROCESS:** The model learns the time-based shape of a baby's deteriorating health.
*   **OUTPUT:** A trained CNN-LSTM model.
*   **NEXT STEP:** Training a model to find unusual patterns.

### 8. Autoencoder
*   **WHAT:** A neural network that learns to compress and reconstruct normal data.
*   **WHY:** If it sees abnormal data (a baby getting sick), it will fail to reconstruct it perfectly. The size of this "error" acts as an anomaly score.
*   **INPUT:** Only "normal" patient sequences.
*   **PROCESS:** Training the network to perfectly recreate normal vital signs.
*   **OUTPUT:** A trained Autoencoder and a baseline error threshold.
*   **NEXT STEP:** Training the most modern architecture.

### 9. Transformer
*   **WHAT:** An attention-based neural network (like the tech behind ChatGPT).
*   **WHY:** Transformers are incredible at looking at an entire sequence and paying "attention" only to the most critical moments (like a sudden drop in oxygen).
*   **INPUT:** 3D sequences of vitals.
*   **PROCESS:** Training the model using self-attention mechanisms.
*   **OUTPUT:** A trained Transformer model.
*   **NEXT STEP:** Combining all these models together.

### 10. Risk fusion
*   **WHAT:** Blending the predictions of XGBoost, CNN-LSTM, Autoencoder, and Transformer into one final score.
*   **WHY:** No single model is perfect. An ensemble approach is much more reliable and reduces false alarms.
*   **INPUT:** Four separate risk scores.
*   **PROCESS:** Averaging or weighting the scores.
*   **OUTPUT:** A single, final Risk Score (0% to 100%) and a Risk Level (LOW, WATCH, HIGH).
*   **NEXT STEP:** *Note: Explainability (SHAP) is planned here but currently missing.*

### 11. SHAP explainability
*   **WHAT:** *Currently Not Implemented.* Will show exactly which vital sign caused the risk score to go up.
*   **WHY:** Doctors won't trust an AI if it's a "black box." They need to know *why* the alarm went off.
*   **INPUT:** The model's prediction.
*   **PROCESS:** Calculating the contribution of each feature to the final score.
*   **OUTPUT:** Visual explanations.
*   **NEXT STEP:** Building the web server.

### 12. FastAPI
*   **WHAT:** The backend web server.
*   **WHY:** The frontend dashboard needs a way to talk to the AI models. FastAPI is extremely fast and handles these requests perfectly.
*   **INPUT:** HTTP requests from the frontend.
*   **PROCESS:** Receiving data, sending it to the ML models, and returning the risk score.
*   **OUTPUT:** JSON responses (e.g., `{"risk_score": 0.85}`).
*   **NEXT STEP:** Saving data permanently.

### 13. PostgreSQL (Currently SQLite)
*   **WHAT:** The database where we store patient records and history.
*   **WHY:** If the server restarts, we don't want to lose patient history. (Currently using SQLite for easy prototyping).
*   **INPUT:** Vital signs and prediction results from FastAPI.
*   **PROCESS:** Saving data into structured tables using SQLAlchemy.
*   **OUTPUT:** Persistent data storage.
*   **NEXT STEP:** Simulating a live hospital monitor.

### 14. Real-time simulator
*   **WHAT:** A system that generates new vital signs every few seconds, acting like a hospital monitor.
*   **WHY:** We need a way to test the system in real-time without hooking it up to a real baby.
*   **INPUT:** Time ticks.
*   **PROCESS:** Generating vitals and streaming them via Server-Sent Events (SSE).
*   **OUTPUT:** A live stream of data.
*   **NEXT STEP:** Building the user interface.

### 15. React dashboard
*   **WHAT:** The visual interface (Frontend) built with React and Chart.js.
*   **WHY:** Nurses and doctors need a clean, easy-to-read screen showing charts and the AI's risk assessment.
*   **INPUT:** Data from the FastAPI backend.
*   **PROCESS:** Rendering live charts and colored risk panels (Green, Yellow, Red).
*   **OUTPUT:** A visual webpage.
*   **NEXT STEP:** Handling emergencies.

### 16. Alert simulation
*   **WHAT:** A WebSocket system that pushes instant notifications to the dashboard.
*   **WHY:** If a baby suddenly goes into HIGH risk, the frontend shouldn't have to ask if everything is okay—the backend should instantly push an alarm.
*   **INPUT:** A HIGH risk prediction from the ML models.
*   **PROCESS:** Broadcasting an alert over WebSockets.
*   **OUTPUT:** A red alert banner appearing instantly on the dashboard.
*   **NEXT STEP:** Adding conversational AI.

### 17. AI chatbot
*   **WHAT:** A chat interface built into the dashboard.
*   **WHY:** Allows medical staff to quickly ask questions like "What is the current heart rate?" or "What is the risk score?" without digging through charts.
*   **INPUT:** Text questions from the user.
*   **PROCESS:** Searching the database for the latest patient vitals and generating a readable answer.
*   **OUTPUT:** A text reply.
*   **NEXT STEP:** Conclusion.

### 18. Final output
*   **WHAT:** The complete end-to-end NeoNatal Watch AI system.
*   **WHY:** It proves the architecture works from raw data all the way to a real-time web dashboard.
*   **INPUT:** The integrated components.
*   **PROCESS:** Running the full stack together.
*   **OUTPUT:** A functional academic prototype demonstrating how AI can monitor neonatal health.

