import logging
import time
import requests
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.config import get_settings
from app.models.finding import ScanFinding
from app.models.scan_job import ScanJob

logger = logging.getLogger("upshield_sync")
settings = get_settings()

def send_request_with_backoff(method: str, path: str, payload: dict, max_retries: int = 3) -> tuple[bool, int, dict | None]:
    """
    Envía una petición HTTP a la API central de UpShield con reintentos y backoff exponencial (offline-first).
    Retorna un tuple: (éxito, status_code, json_de_respuesta)
    """
    url = f"{settings.UPSHIELD_API_URL.rstrip('/')}{path}"
    headers = {
        "X-API-Key": settings.UPSHIELD_API_KEY,
        "X-Tenant-ID": settings.UPSHIELD_TENANT_ID,
        "Content-Type": "application/json"
    }

    # Si no hay URL configurada o es vacía, no procedemos y simulamos éxito en dev si no hay credenciales
    if not settings.UPSHIELD_API_URL:
        logger.warning("UPSHIELD_API_URL no está configurado. Sincronización omitida.")
        return False, 0, None

    attempt = 0
    backoff = 1  # Tiempo inicial de espera en segundos

    while attempt < max_retries:
        try:
            logger.info(f"Intento {attempt + 1}/{max_retries} para {method} {url}")
            if method.upper() == "POST":
                response = requests.post(url, json=payload, headers=headers, timeout=10)
            elif method.upper() == "GET":
                response = requests.get(url, params=payload, headers=headers, timeout=10)
            else:
                logger.error(f"Método HTTP no soportado: {method}")
                return False, 0, None

            # Si el status code es exitoso (2xx), retornamos éxito
            if 200 <= response.status_code < 300:
                try:
                    res_json = response.json()
                except ValueError:
                    res_json = None
                return True, response.status_code, res_json

            # Si es un error de cliente (4xx excepto 429), no reintentamos ya que la petición es inválida
            if 400 <= response.status_code < 500 and response.status_code != 429:
                logger.error(f"Error de cliente ({response.status_code}) al enviar a UpShield: {response.text}")
                return False, response.status_code, None

            # En caso de 5xx o 429 (Too Many Requests), reintentamos con backoff
            logger.warning(f"Respuesta con código de error {response.status_code}. Reintentando...")

        except requests.RequestException as e:
            logger.warning(f"Error de conexión en intento {attempt + 1}: {str(e)}")

        attempt += 1
        if attempt < max_retries:
            time.sleep(backoff)
            backoff *= 2  # Duplicar el tiempo de espera

    logger.error(f"Sincronización fallida tras {max_retries} intentos. Modo offline-first: datos conservados localmente.")
    return False, 0, None

def sync_health(status_data: dict) -> bool:
    """Envía el estado de salud local al SaaS central."""
    success, _, _ = send_request_with_backoff("POST", "/api/edge/sync/health", status_data)
    return success

def sync_scan_status(job: ScanJob) -> bool:
    """Reporta el estado y métricas de un escaneo local al SaaS central."""
    payload = {
        "job_id": job.id,
        "tenant_id": settings.UPSHIELD_TENANT_ID,
        "status": job.status,
        "root_path": job.root_path,
        "files_total": job.files_total,
        "files_scanned": job.files_scanned,
        "files_skipped": job.files_skipped,
        "findings_count": job.findings_count,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "error_message": job.error_message
    }
    success, _, _ = send_request_with_backoff("POST", "/api/edge/sync/scan-job", payload)
    return success

def sync_findings(scan_job_id: int, db: Session) -> bool:
    """
    Agrupa los hallazgos del scan_job_id y los envía al SaaS central.
    NUNCA se envía texto detectado (detected_text), ni plano ni cifrado, para preservar privacidad.
    """
    # Agrupamos por archivo (ruta completa y nombre) y tipo de entidad
    results = (
        db.query(
            ScanFinding.file_path,
            ScanFinding.file_name,
            ScanFinding.entity_type,
            ScanFinding.is_sensitive,
            func.count(ScanFinding.id).label("count"),
            func.max(ScanFinding.confidence_score).label("max_confidence")
        )
        .filter(ScanFinding.scan_job_id == scan_job_id)
        .group_by(
            ScanFinding.file_path,
            ScanFinding.file_name,
            ScanFinding.entity_type,
            ScanFinding.is_sensitive
        )
        .all()
    )

    findings_payload = []
    for r in results:
        findings_payload.append({
            "file_path": r.file_path,
            "file_name": r.file_name,
            "entity_type": r.entity_type,
            "is_sensitive": r.is_sensitive,
            "count": r.count,
            "max_confidence": float(r.max_confidence) if r.max_confidence is not None else 0.0
        })

    payload = {
        "scan_job_id": scan_job_id,
        "tenant_id": settings.UPSHIELD_TENANT_ID,
        "timestamp": datetime.utcnow().isoformat(),
        "findings": findings_payload
    }

    success, _, _ = send_request_with_backoff("POST", "/api/edge/sync/findings", payload)
    return success

def sync_resolution(finding_id: int, db: Session) -> bool:
    """
    Reporta la resolución de un hallazgo al SaaS central.
    Envía metadatos de la mitigación pero NUNCA el texto detectado.
    """
    finding = db.query(ScanFinding).filter(ScanFinding.id == finding_id).first()
    if not finding:
        return False

    payload = {
        "tenant_id": settings.UPSHIELD_TENANT_ID,
        "finding_id": finding.id,
        "file_path": finding.file_path,
        "file_name": finding.file_name,
        "entity_type": finding.entity_type,
        "is_sensitive": finding.is_sensitive,
        "resolved_at": finding.resolved_at.isoformat() if finding.resolved_at else None,
        "resolved_by": finding.resolved_by,
        "resolution_method": finding.resolution_method,
        "resolution_notes": finding.resolution_notes,
        "timestamp": datetime.utcnow().isoformat(),
    }

    success, _, _ = send_request_with_backoff("POST", "/api/edge/sync/resolution", payload)
    return success

def sync_dsar_response(rut: str, dsar_data: dict) -> bool:
    """
    Envía la respuesta DSAR al SaaS central cuando la plataforma solicita
    información de un titular. Envía los datos descifrados para que la
    plataforma pueda consolidar la solicitud ARSOP.
    """
    payload = {
        "tenant_id": settings.UPSHIELD_TENANT_ID,
        "rut_consultado": rut,
        "timestamp": datetime.utcnow().isoformat(),
        "resumen": dsar_data.get("resumen", {}),
        "mapa_de_datos": dsar_data.get("mapa_de_datos", {}),
    }

    success, _, _ = send_request_with_backoff("POST", "/api/edge/sync/dsar-response", payload)
    return success


def run_heartbeat_loop():
    """Loop continuo que ejecuta health checks locales y los envía a la API central."""
    # Esperamos unos segundos al inicio para que FastAPI y la base de datos arranquen completamente
    time.sleep(5)
    
    from app.database import SessionLocal
    from sqlalchemy import text
    from app.services import tika_service, presidio_service
    
    logger.info("Iniciando loop de heartbeat para UpShield Central...")
    while True:
        try:
            # 1. Verificar base de datos
            db_status = "healthy"
            db_message = None
            db = SessionLocal()
            try:
                db.execute(text("SELECT 1"))
            except Exception as e:
                db_status = "unhealthy"
                db_message = str(e)
            finally:
                db.close()

            # 2. Verificar Tika
            tika_ok = tika_service.check_health()
            tika_status = "healthy" if tika_ok else "unhealthy"
            tika_message = None if tika_ok else "No hay respuesta de Apache Tika en el puerto 9998"

            # 3. Verificar Presidio
            presidio_ok = presidio_service.check_health()
            presidio_status = "healthy" if presidio_ok else "unhealthy"
            presidio_message = None if presidio_ok else "No hay respuesta de Microsoft Presidio en el puerto 5001"

            # 4. Determinar estado general
            overall_status = "ok" if (db_status == "healthy" and tika_status == "healthy" and presidio_status == "healthy") else "degraded"
            if db_status != "healthy":
                overall_status = "error"

            payload = {
                "status": overall_status,
                "service": "upshield-edge-agent",
                "version": "1.0.0",
                "environment": settings.ENVIRONMENT,
                "timestamp": datetime.utcnow().isoformat(),
                "services": {
                    "database": {"status": db_status, "message": db_message},
                    "tika": {"status": tika_status, "message": tika_message},
                    "presidio": {"status": presidio_status, "message": presidio_message}
                }
            }

            sync_health(payload)
        except Exception as e:
            logger.error(f"Error en loop de heartbeat: {str(e)}")

        # Esperar el intervalo configurado
        time.sleep(settings.UPSHIELD_SYNC_INTERVAL)

