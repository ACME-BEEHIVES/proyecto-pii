import time
import threading
from datetime import datetime
from app.database import SessionLocal
from app.models.scan_config import ScanConfig
from app.models.scan_job import ScanJob
from app.services import scan_engine

def check_and_run_scheduled_scans():
    db = SessionLocal()
    try:
        config = db.query(ScanConfig).filter(ScanConfig.is_active == True).first()
        if not config or config.schedule_type == "none":
            return
            
        now = datetime.now()
        current_time_str = now.strftime("%H:%M")
        
        # Check if the time matches
        if current_time_str != config.schedule_time:
            return
            
        # Check if day of week matches (for weekly)
        if config.schedule_type == "weekly":
            # now.weekday(): 0=Mon, 6=Sun
            if now.weekday() != config.schedule_day:
                return
                
        # Check if already run today
        today_date = now.date()
        if config.last_scheduled_run:
            if config.last_scheduled_run.date() == today_date:
                return
                
        # Check if there is already an active job running or pending
        active_job = db.query(ScanJob).filter(ScanJob.status.in_(["pending", "running"])).first()
        if active_job:
            print(f"[Scheduler] Escaneo programado detectado a las {current_time_str}, pero ya hay un trabajo activo. Omitiendo.")
            config.last_scheduled_run = now
            db.commit()
            return
            
        print(f"[Scheduler] Lanzando escaneo programado ({config.schedule_type}) a las {current_time_str}...")
        config.last_scheduled_run = now
        db.commit()
        
        # Start scan
        scan_engine.start_scan(db, config)
        
    except Exception as e:
        print(f"[Scheduler] Error en ciclo de programación: {str(e)}")
    finally:
        db.close()

def run_scheduler_loop():
    print("--- Iniciando bucle de programación del escaneo ---")
    while True:
        try:
            check_and_run_scheduled_scans()
        except Exception as e:
            print(f"[Scheduler] Error crítico: {str(e)}")
        time.sleep(30)
