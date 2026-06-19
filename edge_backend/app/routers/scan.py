import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.scan_job import ScanJob
from app.models.scan_config import ScanConfig
from app.schemas.scan import ScanJobResponse, StopScanRequest
from app.services import scan_engine
from typing import List, Optional

router = APIRouter(prefix="/scan")

def get_or_create_default_config(db: Session) -> ScanConfig:
    config = db.query(ScanConfig).filter(ScanConfig.is_active == True).first()
    if not config:
        # Configuración por defecto
        config = ScanConfig(
            scan_paths=json.dumps([r"C:\Users\PabloOrtizCollados\Desktop\proyecto-pii\CARPETA_PRUEBA_MASIVA"]),
            extensions=json.dumps([".pdf", ".docx", ".xlsx", ".xls", ".doc", ".txt", ".jpg", ".png", ".csv"]),
            entities=json.dumps(["CHILE_RUT", "EMAIL_ADDRESS", "PERSON", "DATA_SALUD", "DATA_ETNIA", "DATA_POLITICA", "DATA_RELIGION", "DATA_SEXUALIDAD", "DATA_SINDICAL", "DATA_SOCIOECONOMICO", "DATA_IDEOLOGIA", "DATA_BIOLOGICO", "DATA_BIOMETRICO", "PHONE_NUMBER", "DATE_TIME", "DOMICILIO", "NACIONALIDAD", "DATA_PENAL", "PASAPORTE", "LICENCIA_CONDUCIR", "CUENTA_BANCARIA", "NUMERO_SERIE_DOC"]),
            max_workers=1,
            is_active=True
        )
        db.add(config)
        db.commit()
        db.refresh(config)
    return config

@router.post("/start", response_model=ScanJobResponse)
def start_scan(db: Session = Depends(get_db)):
    # Verificar si ya hay un escaneo activo
    active_job = db.query(ScanJob).filter(ScanJob.status.in_(["pending", "running"])).first()
    if active_job:
        raise HTTPException(status_code=400, detail="Ya existe un escaneo en ejecución.")
    
    config = get_or_create_default_config(db)
    job = scan_engine.start_scan(db, config)
    return job

@router.post("/stop", response_model=bool)
def stop_scan_body(payload: StopScanRequest, db: Session = Depends(get_db)):
    success = scan_engine.cancel_scan(payload.job_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="No se encontró un escaneo activo o pendiente con ese ID.")
    return True

@router.post("/stop/{job_id}", response_model=bool)
def stop_scan(job_id: int, db: Session = Depends(get_db)):
    success = scan_engine.cancel_scan(job_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="No se encontró un escaneo activo o pendiente con ese ID.")
    return True

@router.get("/status", response_model=Optional[ScanJobResponse])
def get_current_status(db: Session = Depends(get_db)):
    # Obtener el último escaneo lanzado
    job = db.query(ScanJob).order_by(ScanJob.started_at.desc()).first()
    return job

@router.get("/history", response_model=List[ScanJobResponse])
def get_scan_history(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    jobs = db.query(ScanJob).order_by(ScanJob.started_at.desc()).offset(skip).limit(limit).all()
    return jobs

@router.get("/history/{job_id}", response_model=ScanJobResponse)
def get_scan_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(ScanJob).filter(ScanJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Escaneo no encontrado.")
    return job
