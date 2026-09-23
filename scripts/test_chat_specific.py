import requests

questions = [
    'Why did the risk score increase?',
    'What happened to SpO2?',
    'Which signals contributed most?',
    'What is the current anomaly score?'
]

for q in questions:
    try:
        r = requests.post('http://localhost:8000/api/v1/chat/', json={'message': q, 'patient_id': 'BABY-JOHN-DOE'})
        print(f'Q: {q}')
        print(f'A: {r.json().get("reply")}\n')
    except Exception as e:
        print(f'Error: {e}')

