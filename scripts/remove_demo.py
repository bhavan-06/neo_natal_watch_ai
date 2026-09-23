import os
import re

files_to_check = [
    "c:/project/neo_natal_watch_ai/backend/app/services/import_service.py",
    "c:/project/neo_natal_watch_ai/backend/app/services/inference_service.py",
    "c:/project/neo_natal_watch_ai/backend/app/services/prenatal_service.py",
    "c:/project/neo_natal_watch_ai/backend/app/api/endpoints/patient.py"
]

for file_path in files_to_check:
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Replace case insensitively
        new_content = re.sub(r'demo', 'simulation', content, flags=re.IGNORECASE)
        
        if new_content != content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Updated {file_path}")

print("Demo strings replaced.")

