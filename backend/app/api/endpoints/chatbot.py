"""
Phase 16 - AI Chatbot Endpoint
A rule-based chatbot that answers questions about patient risk trends and vitals.
This is a PROTOTYPE — it uses pattern matching, not a live LLM.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.db import models

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    patient_id: str = "BABY-JOHN-DOE"


class ChatResponse(BaseModel):
    reply: str


def _get_latest_vitals(db: Session, patient_id: str):
    """Fetch the most recent vital sign from the database."""
    return (
        db.query(models.VitalSign)
        .filter(models.VitalSign.patient_id == patient_id)
        .order_by(models.VitalSign.timestamp.desc())
        .first()
    )


def _get_latest_prediction(db: Session, patient_id: str):
    """Fetch the most recent risk prediction from the database."""
    return (
        db.query(models.Prediction)
        .filter(models.Prediction.patient_id == patient_id)
        .order_by(models.Prediction.timestamp.desc())
        .first()
    )


def _build_reply(msg: str, vitals, prediction) -> str:
    """
    Pattern-match the user's question and return a helpful response.
    Beginner note: This is NOT a real AI language model — it simply checks
    which keywords the user typed and returns the appropriate pre-written answer.
    For a production system you would plug in an LLM (e.g. Gemini, GPT-4).
    """
    msg_lower = msg.lower()

    # --- Risk / score questions --------------------------
    if any(k in msg_lower for k in ["risk", "score", "status", "danger"]):
        if prediction:
            return (
                f"The latest AI risk score for patient '{prediction.patient_id}' is "
                f"{round(prediction.risk_score * 100, 1)}% — level: {prediction.risk_level}. "
                f"(LOW < 30%, WATCH 30-70%, HIGH > 70%.)"
            )
        return "No prediction on record yet. Click 'Simulate Live Vitals' on the dashboard first."

    # --- Heart rate ------------------------------------
    if any(k in msg_lower for k in ["heart", "bpm", "heart rate", "pulse"]):
        if vitals:
            hr = vitals.heart_rate
            status = "elevated" if hr > 160 else ("normal" if hr <= 160 else "borderline")
            return f"Current heart rate: {hr} bpm ({status}). Normal neonatal range: 100–160 bpm."
        return "No heart rate data found for this patient."

    # --- SpO2 ------------------------------------------
    if any(k in msg_lower for k in ["spo2", "oxygen", "saturation", "o2"]):
        if vitals:
            spo2 = vitals.spo2
            status = "critically low" if spo2 < 88 else ("low" if spo2 < 92 else "normal")
            return f"Current SpO2: {spo2}% ({status}). Normal neonatal range: 92–100%."
        return "No SpO2 data found for this patient."

    # --- Temperature -----------------------------------
    if any(k in msg_lower for k in ["temp", "temperature", "fever"]):
        if vitals:
            temp = vitals.temperature
            status = "elevated (possible fever)" if temp > 37.5 else ("hypothermic" if temp < 36.5 else "normal")
            return f"Current temperature: {temp} °C ({status}). Normal neonatal range: 36.5–37.5 °C."
        return "No temperature data found for this patient."

    # --- Respiratory rate ------------------------------
    if any(k in msg_lower for k in ["respiratory", "breathing", "breath", "rr"]):
        if vitals:
            rr = vitals.respiratory_rate
            status = "elevated (tachypnea)" if rr > 60 else ("low (bradypnea)" if rr < 30 else "normal")
            return f"Current respiratory rate: {rr} breaths/min ({status}). Normal: 30–60 bpm."
        return "No respiratory rate data found."

    # --- Blood pressure --------------------------------
    if any(k in msg_lower for k in ["blood pressure", "bp", "systolic", "diastolic"]):
        if vitals:
            return (
                f"Current BP: {vitals.systolic_bp}/{vitals.diastolic_bp} mmHg. "
                "Normal neonatal systolic: 60–90 mmHg."
            )
        return "No blood pressure data found."

    # --- Model explanation ----------------------------
    if any(k in msg_lower for k in ["model", "ai", "xgboost", "cnn", "lstm", "transformer", "autoencoder"]):
        if prediction:
            im = prediction
            return (
                f"Model breakdown: XGBoost={round(im.xgb_score*100,1)}%, "
                f"CNN-LSTM={round(im.cnn_lstm_score*100,1)}%, "
                f"Autoencoder={round(im.ae_score*100,1)}%, "
                f"Transformer={round(im.transformer_score*100,1)}%. "
                "These are blended (fused) into a single risk score."
            )
        return "No prediction data yet."

    # --- Alert / high risk query ----------------------
    if any(k in msg_lower for k in ["alert", "alarm", "critical", "emergency"]):
        if prediction and prediction.risk_level == "HIGH":
            return (
                "ALERT: This patient currently has a HIGH risk score. "
                "The AI recommends immediate clinical review. "
                "Remember: this is an academic prototype — always defer to a qualified clinician."
            )
        return "No active HIGH risk alert for this patient at the moment."

    # --- Help / greeting ------------------------------
    if any(k in msg_lower for k in ["hello", "hi", "hey", "help", "what can you"]):
        return (
            "Hello! I am the NeoNatal Watch AI Assistant. You can ask me about: "
            "'risk score', 'heart rate', 'SpO2', 'temperature', 'respiratory rate', "
            "'blood pressure', 'model breakdown', or 'alerts'. How can I help?"
        )

    # --- Fallback -------------------------------------
    return (
        "I didn't understand that question. Try asking about "
        "'risk score', 'heart rate', 'SpO2', 'temperature', 'model', or 'alerts'."
    )


@router.post("/", response_model=ChatResponse)
def chatbot(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Receive a natural-language question and return a helpful reply
    based on the latest database values for that patient.
    """
    vitals = _get_latest_vitals(db, request.patient_id)
    prediction = _get_latest_prediction(db, request.patient_id)
    reply = _build_reply(request.message, vitals, prediction)
    
    # Save chat history
    try:
        patient_exists = False
        if request.patient_id:
            patient_exists = db.query(models.Patient).filter(models.Patient.id == request.patient_id).first() is not None
        chat = models.ChatHistory(
            patient_id=request.patient_id if patient_exists else None,
            user_role='CLINICIAN',
            question=request.message,
            response=reply,
            model_used='Rule-based-Prototype'
        )
        db.add(chat)
        db.commit()
    except Exception:
        db.rollback()
    
    return ChatResponse(reply=reply)

