
import os
import pandas as pd
import json
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import DateTime, Integer, Float, Boolean, String, Text

from backend.app.db import models
from backend.app.db.models import ImportJob, ImportErrorLog, DatasetSource


# Map table name to corresponding SQLAlchemy model class
TABLE_MODEL_MAP = {
    "patients": models.Patient,
    "pregnancies": models.Pregnancy,
    "maternal_profiles": models.MaternalProfile,
    "fetal_assessments": models.FetalAssessment,
    "ultrasound_records": models.UltrasoundRecord,
    "lab_results": models.LabResult,
    "doppler_results": models.DopplerResult,
    "predictions": models.Prediction,
    "growth_analysis": models.GrowthAnalysis,
    "clinical_events": models.ClinicalEvent,
    "doctor_reviews": models.DoctorReview,
    "prescriptions": models.Prescription,
    "newborns": models.Newborn,
    "nicu_admissions": models.NicuAdmission,
    "nicu_vitals": models.NicuVital,
    "model_outputs": models.ModelOutput,
    "alerts": models.Alert,
    "vital_signs": models.VitalSign,
    "chat_history": models.ChatHistory,
}

# Strict parent-to-child import order respecting all foreign-key constraints
IMPORT_DEPENDENCY_ORDER = [
    "patients",
    "pregnancies",
    "maternal_profiles",
    "fetal_assessments",
    "ultrasound_records",
    "lab_results",
    "doppler_results",
    "predictions",
    "growth_analysis",
    "clinical_events",
    "doctor_reviews",
    "prescriptions",
    "newborns",
    "nicu_admissions",
    "nicu_vitals",
    "model_outputs",
    "alerts",
]


def _clean_value(val, col_type):
    """Cast dataframe cell to appropriate Python / SQLAlchemy type, handling nulls."""
    if pd.isna(val) or val is None or (isinstance(val, str) and val.strip().lower() in ("none", "null", "nan", "")):
        return None

    if isinstance(col_type, DateTime):
        if isinstance(val, datetime):
            return val
        return pd.to_datetime(val).to_pydatetime()
    elif isinstance(col_type, Integer):
        return int(float(val))
    elif isinstance(col_type, Float):
        return float(val)
    elif isinstance(col_type, Boolean):
        if isinstance(val, bool):
            return val
        return bool(int(float(val))) if str(val).isdigit() else str(val).strip().lower() in ("true", "1", "yes")
    elif isinstance(col_type, (String, Text)):
        return str(val).strip()
    return val


def process_import(db: Session, file_path: str, dataset_id: int = None, target_table: str = None) -> ImportJob:
    """
    Imports records from CSV/Excel/JSON into the database with full tracking via
    ImportJob and ImportErrorLog. Supports all domain tables while maintaining
    strict backward compatibility.
    """
    job = ImportJob(dataset_id=dataset_id, file_name=file_path, status='IN_PROGRESS')
    db.add(job)
    db.commit()
    db.refresh(job)

    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.json'):
            df = pd.read_json(file_path)
        else:
            raise ValueError(f'Unsupported file format: {file_path}')

        job.rows_detected = len(df)
        rows_imported = 0
        rows_rejected = 0

        # Infer target table if not explicitly passed
        if not target_table:
            base_name = os.path.basename(file_path).lower()
            for ext in ('.csv', '.xlsx', '.json'):
                base_name = base_name.replace(ext, '')
            # Strip prefixes like 'temp_'
            if base_name.startswith('temp_'):
                base_name = base_name[5:]
            if base_name in TABLE_MODEL_MAP:
                target_table = base_name

        model_cls = TABLE_MODEL_MAP.get(target_table)

        # Fallback to legacy patient mapping if no matching table
        if not model_cls:
            if 'patient_code' in df.columns:
                model_cls = models.Patient
            else:
                raise ValueError(f"Unable to determine target model for file '{file_path}' (target_table={target_table})")

        # Inspect model columns
        table = model_cls.__table__
        col_type_map = {c.name: c.type for c in table.columns}
        pk_cols = [c.name for c in table.primary_key.columns]
        pk_name = pk_cols[0] if pk_cols else 'id'

        for index, row in df.iterrows():
            try:
                row_dict = row.to_dict()
                pk_val = row_dict.get(pk_name)

                # Check if record already exists (Idempotent import)
                if pk_val is not None and not pd.isna(pk_val):
                    pk_clean = _clean_value(pk_val, col_type_map[pk_name])
                    existing = db.query(model_cls).filter(getattr(model_cls, pk_name) == pk_clean).first()
                    if existing:
                        rows_rejected += 1
                        error = ImportErrorLog(
                            job_id=job.id,
                            row_data=json.dumps(row_dict, default=str),
                            error_message=f"Duplicate primary key: {pk_name}={pk_clean}"
                        )
                        db.add(error)
                        continue

                # Also check patient_code uniqueness if model is Patient
                if model_cls is models.Patient and 'patient_code' in row_dict:
                    p_code = row_dict.get('patient_code')
                    if p_code and not pd.isna(p_code):
                        p_code_clean = str(p_code).strip()
                        existing_p = db.query(models.Patient).filter(models.Patient.patient_code == p_code_clean).first()
                        if existing_p:
                            rows_rejected += 1
                            error = ImportErrorLog(
                                job_id=job.id,
                                row_data=json.dumps(row_dict, default=str),
                                error_message=f"Duplicate patient_code: {p_code_clean}"
                            )
                            db.add(error)
                            continue

                # Construct clean kwargs
                clean_kwargs = {}
                for col_name, col_type in col_type_map.items():
                    if col_name in row_dict:
                        clean_kwargs[col_name] = _clean_value(row_dict[col_name], col_type)

                instance = model_cls(**clean_kwargs)
                db.add(instance)
                rows_imported += 1

            except Exception as row_err:
                rows_rejected += 1
                error = ImportErrorLog(
                    job_id=job.id,
                    row_data=json.dumps(row.to_dict(), default=str),
                    error_message=str(row_err)
                )
                db.add(error)

        db.commit()
        job.rows_imported = rows_imported
        job.rows_rejected = rows_rejected
        job.status = 'COMPLETED'
        job.completed_at = datetime.utcnow()
        db.commit()
        return job

    except Exception as e:
        db.rollback()
        job.status = 'FAILED'
        job.completed_at = datetime.utcnow()
        err = ImportErrorLog(job_id=job.id, error_message=str(e))
        db.add(err)
        db.commit()
        return job


def import_all_synthetic_data(db: Session, base_dir: str = 'data/synthetic') -> dict:
    """
    Imports the entire 17-file Phase C synthetic dataset in exact dependency order.
    Creates an audited DatasetSource record and tracks each file import with an ImportJob.
    """
    # 1. Ensure DatasetSource record exists
    ds_name = 'NeoNatal-Watch-AI-Synthetic-Academic-simulation-v1.0'
    dataset = db.query(DatasetSource).filter(DatasetSource.dataset_name == ds_name).first()
    if not dataset:
        dataset = DatasetSource(
            dataset_name=ds_name,
            source_url='local://data/synthetic/',
            license='Academic-simulationnstration',
            data_type='Longitudinal-Synthetic-Clinical',
            description='Deterministic synthetic longitudinal dataset covering maternal, fetal, newborn, and NICU trajectories for academic simulationnstration.',
            notes='NOT REAL PATIENT DATA — FOR ACADEMIC / simulationNSTRATION USE ONLY'
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)

    results = {
        "dataset_id": dataset.id,
        "dataset_name": dataset.dataset_name,
        "files_processed": [],
        "total_imported": 0,
        "total_rejected": 0,
        "status": "SUCCESS"
    }

    for table_name in IMPORT_DEPENDENCY_ORDER:
        csv_path = os.path.join(base_dir, f"{table_name}.csv")
        if not os.path.exists(csv_path):
            continue

        job = process_import(db, csv_path, dataset_id=dataset.id, target_table=table_name)
        results["files_processed"].append({
            "table": table_name,
            "file": f"{table_name}.csv",
            "job_id": job.id,
            "status": job.status,
            "rows_detected": job.rows_detected,
            "rows_imported": job.rows_imported,
            "rows_rejected": job.rows_rejected,
        })
        results["total_imported"] += job.rows_imported or 0
        results["total_rejected"] += job.rows_rejected or 0

        if job.status == 'FAILED':
            results["status"] = "PARTIAL_FAILURE"

    return results
