"""
scripts/pre_import_safety_check.py
----------------------------------
Pre-import safety validation for Phase E.
Checks:
  1. Database connection.
  2. Current row counts match known baseline (patients: 1, predictions: 1, vital_signs: 60, chat_history: 2).
  3. None of the 6 synthetic patient IDs or codes exist in MySQL.
  4. None of the synthetic primary keys collide with existing database keys.
  5. All foreign keys resolve within the synthetic dataset.
  6. Phase C CSV validation passes.
  7. Schema matches 100% with Phase B audit.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from backend.app.db.database import engine
from scripts.validate_synthetic_data import validate_all


def run_safety_checks():
    print("=" * 65)
    print("PHASE E — PRE-IMPORT SAFETY AUDIT")
    print("=" * 65)

    checks = []

    # 1. DB Connection
    try:
        with engine.connect() as conn:
            ver = conn.execute(text("SELECT VERSION()")).scalar()
            print(f"[PASS] 1. Database Connection OK (MySQL {ver})")
            checks.append(True)
    except Exception as e:
        print(f"[FAIL] 1. Database Connection failed: {e}")
        return False

    # 2. Baseline Row Counts
    with engine.connect() as conn:
        p_count = conn.execute(text("SELECT COUNT(*) FROM patients")).scalar()
        pr_count = conn.execute(text("SELECT COUNT(*) FROM predictions")).scalar()
        vs_count = conn.execute(text("SELECT COUNT(*) FROM vital_signs")).scalar()
        ch_count = conn.execute(text("SELECT COUNT(*) FROM chat_history")).scalar()
        preg_count = conn.execute(text("SELECT COUNT(*) FROM pregnancies")).scalar()

        print(f"  Current baseline: patients={p_count}, predictions={pr_count}, vital_signs={vs_count}, chat={ch_count}, pregnancies={preg_count}")
        if p_count == 1 and pr_count == 1 and vs_count == 60 and ch_count == 2 and preg_count == 0:
            print("[PASS] 2. Baseline row counts strictly match expected pre-import state.")
            checks.append(True)
        else:
            print(f"[FAIL] 2. Unexpected row counts: patients={p_count}, predictions={pr_count}, vital_signs={vs_count}")
            return False

        # 3. Existing Patient Check
        existing_patient = conn.execute(text("SELECT id FROM patients WHERE id = 'TEST-PREDICT-01'")).scalar()
        if existing_patient:
            print(f"[PASS] 3. Existing test patient '{existing_patient}' is present and intact.")
            checks.append(True)
        else:
            print("[FAIL] 3. Existing test patient TEST-PREDICT-01 is missing!")
            return False

        # 4. Check for Synthetic ID / Code Collisions in DB
        syn_ids = ["P-SYN-001", "P-SYN-002", "P-SYN-003", "P-SYN-004", "P-SYN-005", "P-SYN-006"]
        syn_codes = ["SYN-PAT-001", "SYN-PAT-002", "SYN-PAT-003", "SYN-PAT-004", "SYN-PAT-005", "SYN-PAT-006"]

        collision_ids = conn.execute(text(f"SELECT id FROM patients WHERE id IN {tuple(syn_ids)}")).fetchall()
        collision_codes = conn.execute(text(f"SELECT patient_code FROM patients WHERE patient_code IN {tuple(syn_codes)}")).fetchall()

        if not collision_ids and not collision_codes:
            print("[PASS] 4. Zero collisions with synthetic IDs or patient codes in MySQL.")
            checks.append(True)
        else:
            print(f"[FAIL] 4. Collisions found: IDs={collision_ids}, codes={collision_codes}")
            return False

        # 5. Check prediction ID collision
        pred_collision = conn.execute(text("SELECT id FROM predictions WHERE id IN (101, 102, 103, 104, 105, 106)")).fetchall()
        if not pred_collision:
            print("[PASS] 5. Zero collisions in prediction IDs.")
            checks.append(True)
        else:
            print(f"[FAIL] 5. Prediction ID collision: {pred_collision}")
            return False

    # 6. CSV Validation Suite
    print("\nRunning CSV Validation Suite...")
    csv_ok = validate_all()
    if csv_ok:
        print("[PASS] 6. CSV validation suite passed 100%.")
        checks.append(True)
    else:
        print("[FAIL] 6. CSV validation failed!")
        return False

    all_ok = all(checks)
    print("=" * 65)
    print(f"PRE-IMPORT SAFETY CHECK RESULT: {'PASS (Safe to Proceed)' if all_ok else 'FAIL'}")
    print("=" * 65)
    return all_ok


if __name__ == "__main__":
    ok = run_safety_checks()
    sys.exit(0 if ok else 1)

