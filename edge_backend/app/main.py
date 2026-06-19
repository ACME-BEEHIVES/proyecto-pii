from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="UpShield Edge Agent API",
    description="Motor de descubrimiento y proteccion de datos personales (PII) para la Ley 21.719 de Chile.",
    version="1.0.0",
)

# CORS — permitir el frontend local
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Nginx production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Health Check basico comentado ya que el health.router lo reemplaza ---
# @app.get("/api/health", tags=["health"])
# def health_check():
#     return {
#         "status": "ok",
#         "service": "upshield-edge-agent",
#         "version": "1.0.0",
#         "environment": settings.ENVIRONMENT,
#     }



from app.routers import scan, findings, config, dsar, health, redaction, db_config, identity
app.include_router(scan.router, prefix="/api", tags=["scan"])
app.include_router(findings.router, prefix="/api", tags=["findings"])
app.include_router(config.router, prefix="/api", tags=["config"])
app.include_router(dsar.router, prefix="/api", tags=["dsar"])
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(redaction.router, prefix="/api", tags=["redaction"])
app.include_router(db_config.router, prefix="/api", tags=["db-config"])
app.include_router(identity.router, prefix="/api", tags=["identity"])



@app.on_event("startup")
def startup_event():
    # Limpiar trabajos de escaneo huérfanos de ejecuciones previas
    from app.database import SessionLocal
    from app.models.scan_job import ScanJob
    from datetime import datetime
    db = SessionLocal()
    try:
        orphaned_jobs = db.query(ScanJob).filter(ScanJob.status.in_(["pending", "running"])).all()
        for job in orphaned_jobs:
            job.status = "failed"
            job.error_message = "Escaneo interrumpido por reinicio del servicio."
            job.completed_at = datetime.utcnow()
        if orphaned_jobs:
            db.commit()
    except Exception as e:
        print(f"Error limpiando trabajos huérfanos en startup: {e}")
    finally:
        db.close()

    import threading
    from app.services.upshield_sync import run_heartbeat_loop
    thread = threading.Thread(target=run_heartbeat_loop, daemon=True)
    thread.start()

    from app.services.scheduler import run_scheduler_loop
    sched_thread = threading.Thread(target=run_scheduler_loop, daemon=True)
    sched_thread.start()

    from app.services.realtime_watcher import watcher
    watcher.start()

    from app.services.alert_service import start_alert_monitoring
    start_alert_monitoring()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
