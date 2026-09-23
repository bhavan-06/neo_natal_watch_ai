
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.services.import_service import process_import
import shutil
import os

router = APIRouter()

@router.post('/import')
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Save file temporarily
    file_location = f'temp_{file.filename}'
    with open(file_location, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Run in background
    # Note: For production, use Celery. Here we use FastAPI BackgroundTasks
    # But since process_import needs DB, we should be careful with session thread-safety in background.
    # For prototype, we'll run it synchronously or create a new session inside the task.
    job = process_import(db, file_location)
    
    return {'message': 'Import completed', 'job_id': job.id, 'imported': job.rows_imported, 'rejected': job.rows_rejected}

