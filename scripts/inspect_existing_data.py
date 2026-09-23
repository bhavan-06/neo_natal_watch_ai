"""
scripts/inspect_existing_data.py
--------------------------------
Read-only detailed data inspection for the tables with existing rows:
  - patients
  - predictions
  - vital_signs
  - chat_history
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from backend.app.db.database import engine


def inspect_data():
    print("=" * 60)
    print("DETAILED DATA INSPECTION OF EXISTING RECORDS")
    print("=" * 60)

    with engine.connect() as conn:
        print("\n--- 1. PATIENTS ---")
        rows = conn.execute(text("SELECT * FROM patients")).fetchall()
        for r in rows:
            print("Row:", dict(r._mapping))

        print("\n--- 2. PREDICTIONS ---")
        rows = conn.execute(text("SELECT id, patient_id, timestamp, risk_score, risk_level, xgb_score, cnn_lstm_score, ae_score, transformer_score FROM predictions")).fetchall()
        for r in rows:
            print("Row:", dict(r._mapping))

        print("\n--- 3. VITAL SIGNS (Sample of 5 rows) ---")
        rows = conn.execute(text("SELECT id, patient_id, timestamp, heart_rate, spo2, respiratory_rate, temperature, systolic_bp, diastolic_bp FROM vital_signs LIMIT 5")).fetchall()
        for r in rows:
            print("Row:", dict(r._mapping))

        print("\n--- 4. CHAT HISTORY ---")
        rows = conn.execute(text("SELECT id, patient_id, user_role, question, response, model_used, created_at FROM chat_history")).fetchall()
        for r in rows:
            print("Row:", dict(r._mapping))

        print("\n--- 5. DUPLICATE ID CHECK ---")
        dup_patient = conn.execute(text("SELECT id, COUNT(*) as c FROM patients GROUP BY id HAVING c > 1")).fetchall()
        print("Duplicate patient IDs:", [dict(r._mapping) for r in dup_patient] or "None")

        dup_codes = conn.execute(text("SELECT patient_code, COUNT(*) as c FROM patients WHERE patient_code IS NOT NULL GROUP BY patient_code HAVING c > 1")).fetchall()
        print("Duplicate patient codes:", [dict(r._mapping) for r in dup_codes] or "None")

        print("\n--- 6. NULL-HEAVY IMPORTANT COLUMN CHECK ---")
        patient_nulls = conn.execute(text("SELECT SUM(CASE WHEN name IS NULL THEN 1 ELSE 0 END) as null_names, SUM(CASE WHEN patient_code IS NULL THEN 1 ELSE 0 END) as null_codes FROM patients")).fetchone()
        print("Patients NULL summary:", dict(patient_nulls._mapping))

        vital_nulls = conn.execute(text("SELECT SUM(CASE WHEN heart_rate IS NULL THEN 1 ELSE 0 END) as null_hr, SUM(CASE WHEN spo2 IS NULL THEN 1 ELSE 0 END) as null_spo2 FROM vital_signs")).fetchone()
        print("Vital signs NULL summary:", dict(vital_nulls._mapping))


if __name__ == "__main__":
    inspect_data()

