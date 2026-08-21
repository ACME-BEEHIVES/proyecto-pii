import json
import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.scan_config import ScanConfig
from app.schemas.config import ScanConfigResponse, ScanConfigUpdate
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

router = APIRouter(prefix="/config")

class TestPathRequest(BaseModel):
    path: str

def get_or_create_default_config(db: Session) -> ScanConfig:
    config = db.query(ScanConfig).filter(ScanConfig.is_active == True).first()
    if not config:
        # Default scan config mapping
        # Carpeta de demo montada en docker-compose.yml (./CARPETA_PRUEBA_MASIVA:/app/CARPETA_PRUEBA_MASIVA),
        # independiente de en que maquina o bajo que usuario este clonado el repo.
        config = ScanConfig(
            scan_paths=json.dumps(["/app/CARPETA_PRUEBA_MASIVA"]),
            extensions=json.dumps([".pdf", ".docx", ".xlsx", ".xls", ".doc", ".txt", ".jpg", ".png", ".csv"]),
            entities=json.dumps(["CHILE_RUT", "EMAIL_ADDRESS", "PERSON", "DATA_SALUD", "DATA_ETNIA", "DATA_POLITICA", "DATA_RELIGION", "DATA_SEXUALIDAD", "DATA_SINDICAL", "DATA_SOCIOECONOMICO", "DATA_IDEOLOGIA", "DATA_BIOLOGICO", "DATA_BIOMETRICO", "PHONE_NUMBER", "DATE_TIME", "DOMICILIO", "NACIONALIDAD", "DATA_PENAL", "PASAPORTE", "LICENCIA_CONDUCIR", "CUENTA_BANCARIA", "NUMERO_SERIE_DOC"]),
            max_workers=1,
            is_active=True
        )
        db.add(config)
        db.commit()
        db.refresh(config)
    return config

def parse_db_url(url: str) -> dict:
    try:
        if not url.startswith("mysql+mysqlconnector://"):
            return {"db_host": "127.0.0.1", "db_port": "3306", "db_user": "root", "db_password": "", "db_name": "pii_discovery"}
        
        cleaned = url[len("mysql+mysqlconnector://"):]
        if "@" in cleaned:
            credentials, location = cleaned.split("@", 1)
        else:
            credentials = "root:"
            location = cleaned
            
        if ":" in credentials:
            db_user, db_password = credentials.split(":", 1)
        else:
            db_user = credentials
            db_password = ""
            
        if "/" in location:
            host_port, db_name = location.split("/", 1)
        else:
            host_port = location
            db_name = ""
            
        if ":" in host_port:
            db_host, db_port = host_port.split(":", 1)
        else:
            db_host = host_port
            db_port = "3306"
            
        return {
            "db_host": db_host,
            "db_port": db_port,
            "db_user": db_user,
            "db_password": db_password,
            "db_name": db_name
        }
    except Exception:
        return {"db_host": "127.0.0.1", "db_port": "3306", "db_user": "root", "db_password": "", "db_name": "pii_discovery"}

def reconstruct_db_url(db_host, db_port, db_user, db_password, db_name) -> str:
    port_str = f":{db_port}" if db_port else ""
    return f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}{port_str}/{db_name}"

def update_env_file(updates: dict):
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
    if not os.path.exists(env_path):
        env_path = ".env"
    
    lines = []
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
    new_lines = []
    processed_keys = set()
    for line in lines:
        stripped = line.strip()
        matched = False
        for key in updates:
            if stripped.startswith(f"{key}="):
                new_lines.append(f"{key}={updates[key]}\n")
                processed_keys.add(key)
                matched = True
                break
        if not matched:
            new_lines.append(line)
            
    for key, val in updates.items():
        if key not in processed_keys:
            new_lines.append(f"{key}={val}\n")
        
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

@router.get("", response_model=ScanConfigResponse)
def get_config(db: Session = Depends(get_db)):
    """Obtiene la configuración activa del motor de escaneo."""
    config = get_or_create_default_config(db)
    
    from app.config import get_settings
    settings = get_settings()
    db_url = settings.DATABASE_URL
    db_details = parse_db_url(db_url)
    
    return ScanConfigResponse(
        id=config.id,
        scan_paths=json.loads(config.scan_paths),
        extensions=json.loads(config.extensions),
        entities=json.loads(config.entities),
        max_workers=config.max_workers,
        is_active=config.is_active,
        schedule_type=config.schedule_type,
        schedule_time=config.schedule_time,
        schedule_day=config.schedule_day,
        db_host=db_details["db_host"],
        db_port=db_details["db_port"],
        db_user=db_details["db_user"],
        db_password=db_details["db_password"],
        db_name=db_details["db_name"],
        upshield_api_url=settings.UPSHIELD_API_URL,
        upshield_api_key=settings.UPSHIELD_API_KEY,
        upshield_tenant_id=settings.UPSHIELD_TENANT_ID,
        upshield_sync_interval=settings.UPSHIELD_SYNC_INTERVAL,
        alert_emails_enabled=settings.ALERT_EMAILS_ENABLED,
        alert_check_interval=settings.ALERT_CHECK_INTERVAL,
        smtp_host=settings.SMTP_HOST,
        smtp_port=settings.SMTP_PORT,
        smtp_username=settings.SMTP_USERNAME,
        smtp_password=settings.SMTP_PASSWORD,
        smtp_from=settings.SMTP_FROM,
        smtp_to=settings.SMTP_TO,
        updated_at=config.updated_at
    )

@router.put("", response_model=ScanConfigResponse)
def update_config(payload: ScanConfigUpdate, db: Session = Depends(get_db)):
    """Actualiza la configuración activa del motor de escaneo."""
    config = get_or_create_default_config(db)
    
    if payload.max_workers < 1 or payload.max_workers > 16:
        raise HTTPException(status_code=400, detail="max_workers debe estar entre 1 y 16.")

    # Validar rutas del sistema prohibidas
    prohibited = ["c:\\windows", "c:\\winnt", "system32", "program files", "/etc", "/var", "/bin", "/sbin", "/usr"]
    for path in payload.scan_paths:
        lower_p = path.lower()
        for pr in prohibited:
            if pr in lower_p:
                raise HTTPException(status_code=400, detail=f"La ruta contiene directorios de sistema prohibidos: {path}")

    # 1. Guardar campos en BD
    config.scan_paths = json.dumps(payload.scan_paths)
    config.extensions = json.dumps(payload.extensions)
    config.entities = json.dumps(payload.entities)
    config.max_workers = payload.max_workers
    config.is_active = payload.is_active
    config.schedule_type = payload.schedule_type
    config.schedule_time = payload.schedule_time
    config.schedule_day = payload.schedule_day
    config.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(config)
    
    # 2. Reconstruir DATABASE_URL (Deshabilitado: el motor ahora usa SQLite local fijo)
    from app.config import get_settings
    current_db_url = get_settings().DATABASE_URL
    env_updates = {}
    
    # Guardar credenciales de UpShield en .env
    env_updates["UPSHIELD_API_URL"] = payload.upshield_api_url
    env_updates["UPSHIELD_API_KEY"] = payload.upshield_api_key
    env_updates["UPSHIELD_TENANT_ID"] = payload.upshield_tenant_id
    env_updates["UPSHIELD_SYNC_INTERVAL"] = str(payload.upshield_sync_interval)
    
    # Guardar SMTP en .env
    env_updates["ALERT_EMAILS_ENABLED"] = str(payload.alert_emails_enabled)
    env_updates["ALERT_CHECK_INTERVAL"] = str(payload.alert_check_interval)
    env_updates["SMTP_HOST"] = payload.smtp_host
    env_updates["SMTP_PORT"] = str(payload.smtp_port)
    env_updates["SMTP_USERNAME"] = payload.smtp_username
    env_updates["SMTP_PASSWORD"] = payload.smtp_password
    env_updates["SMTP_FROM"] = payload.smtp_from
    env_updates["SMTP_TO"] = payload.smtp_to
    
    if env_updates:
        update_env_file(env_updates)
        for k, v in env_updates.items():
            os.environ[k] = v
        get_settings.cache_clear()
            
    db_details = parse_db_url(current_db_url)
    settings = get_settings()
    
    return ScanConfigResponse(
        id=config.id,
        scan_paths=json.loads(config.scan_paths),
        extensions=json.loads(config.extensions),
        entities=json.loads(config.entities),
        max_workers=config.max_workers,
        is_active=config.is_active,
        schedule_type=config.schedule_type,
        schedule_time=config.schedule_time,
        schedule_day=config.schedule_day,
        db_host=db_details["db_host"],
        db_port=db_details["db_port"],
        db_user=db_details["db_user"],
        db_password=db_details["db_password"],
        db_name=db_details["db_name"],
        upshield_api_url=settings.UPSHIELD_API_URL,
        upshield_api_key=settings.UPSHIELD_API_KEY,
        upshield_tenant_id=settings.UPSHIELD_TENANT_ID,
        upshield_sync_interval=settings.UPSHIELD_SYNC_INTERVAL,
        alert_emails_enabled=settings.ALERT_EMAILS_ENABLED,
        alert_check_interval=settings.ALERT_CHECK_INTERVAL,
        smtp_host=settings.SMTP_HOST,
        smtp_port=settings.SMTP_PORT,
        smtp_username=settings.SMTP_USERNAME,
        smtp_password=settings.SMTP_PASSWORD,
        smtp_from=settings.SMTP_FROM,
        smtp_to=settings.SMTP_TO,
        updated_at=config.updated_at
    )

@router.post("/test-path")
def test_path(payload: TestPathRequest):
    """Verifica si una ruta de red o directorio local existe y es accesible."""
    from app.services.path_service import translate_path
    
    p = payload.path.strip()
    if not p:
        raise HTTPException(status_code=400, detail="La ruta no puede estar vacía.")

    lower_p = p.lower()
    prohibited = ["c:\\windows", "c:\\winnt", "system32", "program files", "/etc", "/var", "/bin", "/sbin", "/usr"]
    for pr in prohibited:
        if pr in lower_p:
            return {"status": "error", "message": f"Acceso denegado a rutas de sistema: {p}"}

    # Traducir ruta para verificación en el sistema de archivos del contenedor
    check_p = translate_path(p)

    if not os.path.exists(check_p):
        return {"status": "error", "message": f"La ruta no existe o no es accesible: {p}"}

    return {"status": "ok", "message": f"Ruta válida y accesible: {p}"}


class BrowseDirResponse(BaseModel):
    current_path: str
    parent_path: Optional[str] = None
    directories: List[str]


@router.get("/browse", response_model=BrowseDirResponse)
def browse_directory(path: Optional[str] = None):
    """Obtiene el listado de subdirectorios de una ruta para el explorador de archivos."""
    if not path or not path.strip():
        # Punto de partida util para elegir carpetas de un cliente: el mount
        # generico de C:\Users (ver docker-compose.yml / path_service.py). Si no
        # esta disponible (ej. corriendo fuera de Docker) cae a /app o cwd.
        if os.path.exists("/mnt/c/Users"):
            path = "/mnt/c/Users"
        elif os.path.exists("/app"):
            path = "/app"
        else:
            path = os.getcwd()
    
    path = os.path.abspath(path)
    
    # Validar acceso a rutas de sistema
    lower_p = path.lower()
    prohibited = ["c:\\windows", "c:\\winnt", "system32", "program files", "/etc", "/var", "/bin", "/sbin", "/usr"]
    for pr in prohibited:
        if pr in lower_p:
            raise HTTPException(status_code=400, detail="Acceso denegado a rutas de sistema.")

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="La ruta especificada no existe.")
        
    if not os.path.isdir(path):
        raise HTTPException(status_code=400, detail="La ruta especificada no es un directorio.")

    try:
        entries = os.listdir(path)
        directories = []
        for entry in entries:
            full_path = os.path.join(path, entry)
            # Solo devolvemos directorios que no sean ocultos
            if os.path.isdir(full_path) and not entry.startswith('.'):
                directories.append(entry)
        
        # Sort directories alphabetically
        directories.sort()
        
        # Calculate parent path (if we are not at the filesystem root)
        parent_path = os.path.dirname(path)
        if parent_path == path: # We are at the root
            parent_path = None
            
        return BrowseDirResponse(
            current_path=path,
            parent_path=parent_path,
            directories=directories
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar el directorio: {str(e)}")

