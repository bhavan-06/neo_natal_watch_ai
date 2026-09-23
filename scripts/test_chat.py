import requests, json
from datetime import datetime, timedelta

print("=== Testing /predict ===")
base = datetime.now() - timedelta(minutes=60)
records = [
    {
        "timestamp": (base + timedelta(minutes=i)).isoformat(),
        "patient_id": "BABY-JOHN-DOE",
        "heart_rate": 140 + i * 0.6,
        "spo2": 96 - i * 0.2,
        "respiratory_rate": 45.0,
        "temperature": 37.0,
        "systolic_bp": 60.0,
        "diastolic_bp": 40.0
    }
    for i in range(60)
]
r = requests.post("http://localhost:8000/api/v1/predict/", json={"records": records})
print(json.dumps(r.json(), indent=2))

print()
print("=== Testing /chat ===")
questions = ["hello", "what is the risk score?", "heart rate?", "spo2?", "model breakdown"]
for q in questions:
    r2 = requests.post("http://localhost:8000/api/v1/chat/",
                       json={"message": q, "patient_id": "BABY-JOHN-DOE"})
    reply = r2.json().get("reply", "no reply")
    print(f"Q: {q}")
    print(f"A: {reply}")
    print()

