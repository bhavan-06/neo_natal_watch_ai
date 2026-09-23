"""
Test script to simulate sending 60 minutes of vital signs to the FastAPI backend.

Usage:
    # 1. Start the server in a separate terminal:
    #    python backend/app/main.py
    # 2. Run this script:
    #    python scripts/test_api.py
"""

import requests
import json
import pandas as pd
from datetime import datetime, timedelta

def main():
    print("=" * 60)
    print("Testing NeoNatal Watch AI API")
    print("=" * 60)
    
    # 1. Check if server is up
    try:
        res = requests.get("http://localhost:8000/")
        print("Server Health:", res.json())
    except requests.exceptions.ConnectionError:
        print("[ERROR] Could not connect to localhost:8000.")
        print("Please start the server first using: python backend/app/main.py")
        return

    # 2. Generate 60 minutes of mock data (mimicking a deteriorating patient)
    print("\nGenerating 60 minutes of mock vital signs...")
    base_time = datetime.now() - timedelta(minutes=60)
    
    records = []
    for i in range(60):
        # Create a degrading trend: Heart rate rises, SpO2 drops
        hr = 140.0 + (i * 0.5)      # Normal is ~140, goes up to 170
        spo2 = 96.0 - (i * 0.15)    # Normal is ~96, drops to 87
        
        record = {
            "timestamp": (base_time + timedelta(minutes=i)).isoformat(),
            "patient_id": "API-TEST-001",
            "heart_rate": round(hr, 1),
            "spo2": round(spo2, 1),
            "respiratory_rate": 45.0,
            "temperature": 37.0,
            "systolic_bp": 60.0,
            "diastolic_bp": 40.0
        }
        records.append(record)
        
    payload = {"records": records}
    
    # 3. Send POST request
    print("Sending POST request to /api/v1/predict...")
    response = requests.post("http://localhost:8000/api/v1/predict/", json=payload)
    
    if response.status_code == 200:
        print("\n✅ SUCCESS! Received Prediction:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"\n❌ ERROR {response.status_code}:")
        print(response.text)

if __name__ == "__main__":
    main()

