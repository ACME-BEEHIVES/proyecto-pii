from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.config import get_settings
from app.schemas.health import HealthResponse, ServiceHealthStatus
from app.services import tika_service, presidio_service

router = APIRouter(prefix="/health")
settings = get_settings()

@router.get("", response_model=HealthResponse)
def get_health_status(db: Session = Depends(get_db)):
    """Verifica el estado general de salud del agente y todos sus servicios dependientes."""
    services = {}

    # 1. Database health check
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
        services["database"] = ServiceHealthStatus(status="healthy")
    except Exception as e:
        services["database"] = ServiceHealthStatus(status="unhealthy", message=str(e))

    # 2. OCR Engine (PaddleOCR — reemplaza Apache Tika)
    ocr_ok = tika_service.check_health()
    services["ocr_engine"] = ServiceHealthStatus(
        status="healthy" if ocr_ok else "unhealthy",
        message=None if ocr_ok else "PaddleOCR no está disponible. Verifica la instalación."
    )

    # 3. Presidio health check
    presidio_ok = presidio_service.check_health()
    services["presidio"] = ServiceHealthStatus(
        status="healthy" if presidio_ok else "unhealthy",
        message=None if presidio_ok else "No hay respuesta de Microsoft Presidio en el puerto 5001"
    )

    # 4. Realtime Watcher health check
    watcher_status = "unhealthy"
    watcher_msg = "Monitoreo en tiempo real inactivo"
    try:
        from app.services.realtime_watcher import watcher
        if watcher and watcher.active:
            if watcher.observer and watcher.observer.is_alive():
                watcher_status = "healthy"
                watcher_msg = f"Monitoreando {len(watcher.current_paths)} carpetas"
            else:
                watcher_status = "healthy"
                watcher_msg = "Activo (Esperando configuración de carpetas)"
    except Exception as e:
        watcher_msg = f"Error al verificar watcher: {str(e)}"

    services["watcher"] = ServiceHealthStatus(
        status=watcher_status,
        message=watcher_msg
    )

    # Determinar el estado general
    all_ok = db_ok and ocr_ok and presidio_ok and (watcher_status == "healthy")
    status = "ok" if all_ok else ("degraded" if db_ok else "error")

    return HealthResponse(
        status=status,
        service="upshield-edge-agent",
        version="1.0.0",
        environment=settings.ENVIRONMENT,
        services=services
    )


@router.get("/ocr")
def get_ocr_health():
    """Verifica si el motor PaddleOCR está operativo."""
    ok = tika_service.check_health()
    return {"status": "healthy" if ok else "unhealthy", "engine": "PaddleOCR"}


@router.get("/tika")
def get_tika_health():
    """Alias de compatibilidad → ahora apunta al motor PaddleOCR."""
    ok = tika_service.check_health()
    return {"status": "healthy" if ok else "unhealthy", "engine": "PaddleOCR (reemplazó a Tika)"}


@router.get("/presidio")
def get_presidio_health():
    """Verifica si Microsoft Presidio está operativo."""
    ok = presidio_service.check_health()
    return {"status": "healthy" if ok else "unhealthy"}


@router.get("/database")
def get_database_health(db: Session = Depends(get_db)):
    """Verifica si la base de datos MySQL local está operativa."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
