import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.db.database import SessionLocal
from backend.app.db.models import Patient

def clean_names():
    db = SessionLocal()
    for p in db.query(Patient).all():
        if p.name and ("Demo" in p.name or "demo" in p.name):
            old = p.name
            clean = p.name.replace(" (Demo)", "").replace("(Demo)", "").replace("Demo Patient ", "Patient ").replace(" (demo)", "").strip()
            print(f"Updated {p.id}: '{old}' -> '{clean}'")
            p.name = clean
    db.commit()
    db.close()

if __name__ == "__main__":
    clean_names()

