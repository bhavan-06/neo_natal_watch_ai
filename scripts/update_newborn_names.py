import os
import sys

# Add project root to python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.app.db.database import SQLALCHEMY_DATABASE_URL
from backend.app.db.models import Newborn, Patient, Pregnancy, FetalAssessment

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def upgrade_and_seed():
    db = SessionLocal()
    
    # Add name column if it doesn't exist
    try:
        db.execute(text("ALTER TABLE newborns ADD COLUMN name VARCHAR(255);"))
        db.commit()
        print("Added name column to newborns.")
    except Exception as e:
        db.rollback()
        print("Name column might already exist:", str(e))
        
    # Seed names for newborns
    newborn_names = {
        'NB-001': 'Liam',
        'NB-002': 'Emma',
        'NB-003': 'Olivia',
        'NB-004': 'Noah',
        'NB-005': 'Sophia',
        'NB-006': 'Ava',
        'NB-007': 'Isabella',
        'NB-008': 'Mia'
    }
    
    newborns = db.query(Newborn).all()
    for nb in newborns:
        if nb.newborn_code in newborn_names:
            nb.name = newborn_names[nb.newborn_code]
        else:
            nb.name = f"Baby {nb.newborn_code.replace('NB-', '')}"
        
    # Add some more patients
    new_patients = [
        {"id": "P-SYN-009", "patient_code": "SYN-009", "name": "Sophia Martinez", "contact_info": "contact9@example.com"},
        {"id": "P-SYN-010", "patient_code": "SYN-010", "name": "Isabella Clark", "contact_info": "contact10@example.com"}
    ]
    
    for pd in new_patients:
        p = db.query(Patient).filter(Patient.id == pd["id"]).first()
        if not p:
            new_p = Patient(**pd)
            db.add(new_p)
            
            # Add a pregnancy
            preg = Pregnancy(patient_id=new_p.id, pregnancy_code=f"PREG-{new_p.patient_code}", pregnancy_status='ACTIVE')
            db.add(preg)
            db.flush()
            
            # Add fetal assessment
            fa = FetalAssessment(pregnancy_id=preg.id, gestational_age_weeks=32.0, trimester=3, efw_percentile=15.2)
            db.add(fa)
            
            # Add newborn
            nb = Newborn(pregnancy_id=preg.id, newborn_code=f"NB-00{pd['id'][-1]}", name=newborn_names.get(f"NB-00{pd['id'][-1]}", f"Baby {pd['id'][-1]}"))
            db.add(nb)
            
    db.commit()
    print("Database updated successfully.")
    db.close()

if __name__ == "__main__":
    upgrade_and_seed()

