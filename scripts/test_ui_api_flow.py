
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)
patients_res = client.get('/api/v1/patients/')
print('GET /patients/ status:', patients_res.status_code, 'count:', len(patients_res.json()))
for p in patients_res.json():
    print(f"  - {p['id']}: {p.get('name')} ({p.get('patient_code')})")

ids = ['P-SYN-001', 'P-SYN-002', 'P-SYN-003', 'P-SYN-004', 'P-SYN-005', 'P-SYN-006', 'TEST-PREDICT-01']
endpoints = ['timeline', 'pregnancy', 'fetal-assessments', 'growth-analysis', 'newborn', 'nicu', 'predictions']

for pid in ids:
    print(f"\n=== Testing Patient {pid} ===")
    p_res = client.get(f'/api/v1/patients/{pid}')
    print(f"  /patients/{pid} -> {p_res.status_code}: {p_res.json().get('name')}")
    for ep in endpoints:
        r = client.get(f'/api/v1/patients/{pid}/{ep}')
        data = r.json()
        print(f"  /{ep} -> {r.status_code}, items={len(data)}")
        if len(data) > 0 and ep in ['timeline', 'growth-analysis', 'newborn', 'nicu']:
            print(f"    sample {ep}: {json.dumps(data[0], default=str)[:120]}...")
