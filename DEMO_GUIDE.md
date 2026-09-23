# NeoNatal Watch AI Demo Guide

**Note to Mentor/Evaluator:** This is an academic research prototype. It is NOT a real clinical decision-support system and relies entirely on synthetic data.

## 1. Prerequisites
- Python 3.12+
- Required pip packages installed (`pip install -r requirements.txt`)
- A modern web browser (Chrome/Edge/Firefox)

## 2. Environment Setup
Open a terminal in the project root: `C:\project\gratwin_project\neo_natal_watch_ai`
Ensure your virtual environment (if any) is activated.

## 3. Start Database
*No separate command required.* The project utilizes SQLite (`neonatal.db`) for immediate prototyping, which automatically initializes when the backend starts.

## 4. Start Backend
Run the FastAPI backend server:
```powershell
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```
*Wait for the console to display "Inference Service is READY" and "Application startup complete."*

## 5. Start Frontend & Open Dashboard
The frontend is built directly into the FastAPI server. Open your web browser and navigate to:
**[http://localhost:8000/dashboard](http://localhost:8000/dashboard)**

*The dashboard will load immediately.*

## 8. Select Demo Patient
The dashboard is hardcoded to simulate data for patient `BABY-JOHN-DOE` during the prototype phase.

## 9. View Vital Trends
1. Click the blue **"Simulate Live Vitals"** button in the top right corner.
2. The dashboard will instantly generate 60 minutes of deteriorating patient data and display it on the Heart Rate and SpO2 line charts.

## 10. View Risk Score
Once the button is clicked, the vitals are sent to the backend for inference. The left panel will update with the final Fusion Risk Score and Risk Level (e.g., `WATCH` or `HIGH`).

## 11. View Model Outputs
Directly beneath the central risk score, a **Model Breakdown** section displays the individual confidence scores from the CNN-LSTM, Transformer, Autoencoder, and XGBoost models.

## 12. View SHAP Explanation
* **Currently Not Implemented.** SHAP explainability is a known missing feature in this prototype phase.

## 13. Trigger Demo Alert & 16. Display Alert
If the generated vital signs result in a `HIGH` risk level from the ML models, the backend automatically broadcasts an alert over WebSockets.
* A red **Live Alerts** banner will immediately appear at the top of the dashboard without refreshing the page.

## 14. Test Chatbot
In the bottom right corner, locate the AI Assistant panel. Test it by typing:
1. `What is the risk score?`
2. `What happened to SpO2?`
3. `Heart rate?`
4. `Model breakdown`

The chatbot queries the SQLite database directly and returns medically-contextual answers based on the last simulation.

## 15. Stop Services
In the terminal where `uvicorn` is running, press `CTRL + C` to shut down the backend server. Close the browser tab.

---

### QUICK DEMO COMMANDS
Copy and paste these commands into PowerShell to run the demo:

```powershell
# 1. Start the API and ML models
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000

# 2. Open your web browser and navigate to:
# http://localhost:8000/dashboard
Start-Process "http://localhost:8000/dashboard"
```

