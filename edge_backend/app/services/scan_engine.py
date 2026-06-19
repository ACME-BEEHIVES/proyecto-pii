import os
import hashlib
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.scan_job import ScanJob
from app.models.file_control import FileControl
from app.models.finding import ScanFinding
from app.models.scan_config import ScanConfig
from app.services import tika_service, presidio_service, crypto_service, upshield_sync

# Bloqueo global para actualizar las estadísticas de ScanJob desde los hilos de ejecución
scan_lock = threading.Lock()

# Conjunto global para almacenar IDs de escaneos cancelados
cancelled_jobs = set()

def get_file_md5(file_path: str) -> str:
    """Calcula el hash MD5 del contenido de un archivo."""
    hasher = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return ""

def process_file(file_path: str, scan_job_id: int, entities: list[str]):
    """Procesa un archivo individual: verifica cambios, extrae texto, analiza PII y guarda hallazgos."""
    # Abrimos sesión propia para este hilo
    db = SessionLocal()
    try:
        # Verificar si el escaneo fue cancelado
        if scan_job_id and scan_job_id in cancelled_jobs:
            db.query(ScanJob).filter(ScanJob.id == scan_job_id).update({
                ScanJob.files_skipped: ScanJob.files_skipped + 1
            })
            db.commit()
            return

        # 1. Calcular hash de control
        content_hash = get_file_md5(file_path)
        if not content_hash:
            if scan_job_id:
                db.query(ScanJob).filter(ScanJob.id == scan_job_id).update({
                    ScanJob.files_skipped: ScanJob.files_skipped + 1
                })
                db.commit()
            return

        path_hash = hashlib.md5(file_path.encode('utf-8')).hexdigest()
        file_control = db.query(FileControl).filter(FileControl.hash_ruta == path_hash).first()

        # Saltearse si no ha cambiado (escaneo incremental)
        if file_control and file_control.content_hash == content_hash:
            if scan_job_id:
                db.query(ScanJob).filter(ScanJob.id == scan_job_id).update({
                    ScanJob.files_skipped: ScanJob.files_skipped + 1
                })
                db.commit()
            return

        is_modified = file_control is not None

        # 2. Extraer texto con Apache Tika
        try:
            texto = tika_service.extract_text(file_path)
        except Exception:
            texto = ""

        # Si el texto es nulo o vacío, registramos control pero sin hallazgos
        if not texto or len(texto.strip()) < 3:
            if not file_control:
                file_control = FileControl(hash_ruta=path_hash, file_path=file_path, content_hash=content_hash)
                db.add(file_control)
            else:
                file_control.content_hash = content_hash
                file_control.last_scanned_at = datetime.utcnow()
            db.commit()

            if scan_job_id:
                db.query(ScanJob).filter(ScanJob.id == scan_job_id).update({
                    ScanJob.files_scanned: ScanJob.files_scanned + 1
                })
                db.commit()
            return

        # 3. Analizar PII con Presidio
        findings = presidio_service.analyze_text(texto, entities)

        # Si el archivo fue modificado, eliminamos los hallazgos anteriores para evitar duplicados
        if is_modified:
            db.query(ScanFinding).filter(ScanFinding.file_path == file_path).delete()
            db.commit()

        hallazgos_guardados = 0
        if isinstance(findings, list) and len(findings) > 0:
            for h in findings:
                if h.get('score', 0) >= 0.5:
                    start = h['start']
                    end = h['end']
                    texto_original = texto[start:end]
                    entity_type = h['entity_type']

                    is_sensitive = crypto_service.is_sensitive_entity(entity_type)
                    if not is_sensitive and crypto_service.check_text_contains_sensitive(texto_original, entity_type):
                        is_sensitive = True

                    if is_sensitive:
                        texto_a_guardar = crypto_service.encrypt(texto_original)
                    else:
                        texto_a_guardar = texto_original

                    finding = ScanFinding(
                        scan_job_id=scan_job_id,
                        file_path=file_path,
                        file_name=os.path.basename(file_path),
                        entity_type=entity_type,
                        detected_text=texto_a_guardar,
                        confidence_score=h['score'],
                        is_sensitive=is_sensitive,
                        is_resolved=False,
                        created_at=datetime.utcnow()
                    )
                    db.add(finding)
                    hallazgos_guardados += 1
            db.commit()

        # 4. Actualizar control_archivos
        if not file_control:
            file_control = FileControl(
                hash_ruta=path_hash,
                file_path=file_path,
                content_hash=content_hash,
                last_scanned_at=datetime.utcnow()
            )
            db.add(file_control)
        else:
            file_control.content_hash = content_hash
            file_control.last_scanned_at = datetime.utcnow()
        db.commit()

        # 5. Actualizar el progreso del Job
        if scan_job_id:
            db.query(ScanJob).filter(ScanJob.id == scan_job_id).update({
                ScanJob.files_scanned: ScanJob.files_scanned + 1,
                ScanJob.findings_count: ScanJob.findings_count + hallazgos_guardados
            })
            db.commit()

    except Exception as e:
        print(f"Error procesando {file_path}: {str(e)}")
    finally:
        db.close()

def run_scan_async(scan_job_id: int, scan_paths: list[str], extensions: list[str], entities: list[str], max_workers: int):
    """Ejecuta el escaneo completo en segundo plano."""
    db = SessionLocal()
    try:
        # Verificar salud de los motores antes de empezar
        if not tika_service.check_health() or not presidio_service.check_health():
            job = db.query(ScanJob).filter(ScanJob.id == scan_job_id).first()
            if job:
                job.status = "failed"
                job.error_message = "Servicios externos (Tika o Presidio) no responden. Escaneo abortado."
                job.completed_at = datetime.utcnow()
                db.commit()
                # Reportar fallo inicial a UpShield
                upshield_sync.sync_scan_status(job)
            return

        # Recorrer directorios configurados
        from app.services.path_service import translate_path

        archivos = []
        for path in scan_paths:
            # Traducir ruta del host a la ruta accesible en el contenedor
            check_path = translate_path(path)
            if not os.path.exists(check_path):
                print(f"Ruta omitida por no existir en el contenedor: {path} (traducida a: {check_path})")
                continue
            for raiz, _, files in os.walk(check_path):
                for n in files:
                    ext = os.path.splitext(n)[1].lower()
                    if ext in extensions:
                        archivos.append(os.path.join(raiz, n))

        # Registrar la cantidad total de archivos a escanear
        job = db.query(ScanJob).filter(ScanJob.id == scan_job_id).first()
        if not job:
            return

        # Estimación de celdas a escanear en bases de datos activas
        from app.models.db_config import DbConfig
        from app.services.db_scan_engine import estimate_db_config_cells, scan_single_db_config

        active_dbs = db.query(DbConfig).filter(DbConfig.is_active == True).all()
        db_cells_total = 0
        for db_config in active_dbs:
            db_cells_total += estimate_db_config_cells(db_config)

        total_to_scan = len(archivos) + db_cells_total
        job.files_total = total_to_scan
        job.status = "running"
        db.commit()
        # Reportar inicio de ejecución
        upshield_sync.sync_scan_status(job)

        if total_to_scan == 0:
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            db.commit()
            # Reportar completitud (0 elementos)
            upshield_sync.sync_scan_status(job)
            upshield_sync.sync_findings(job.id, db)
            return

        # Cleanup stale files that no longer exist on disk
        translated_paths = [translate_path(p).replace('\\', '/') for p in scan_paths]
        all_controls = db.query(FileControl).all()
        for fc in all_controls:
            is_under_scan_paths = False
            for tp in translated_paths:
                if fc.file_path.replace('\\', '/').startswith(tp):
                    is_under_scan_paths = True
                    break
            if is_under_scan_paths and fc.file_path not in archivos:
                db.query(ScanFinding).filter(ScanFinding.file_path == fc.file_path).delete()
                db.delete(fc)
        db.commit()

        # Lanzar la pool de hilos para archivos físicos
        if len(archivos) > 0:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(process_file, f, scan_job_id, entities) for f in archivos]
                for fut in futures:
                    fut.result()

        # Escanear las bases de datos SQL activas secuencialmente
        for db_config in active_dbs:
            if scan_job_id in cancelled_jobs:
                break
            try:
                # Actualizar dinámicamente el root_path del job
                job = db.query(ScanJob).filter(ScanJob.id == scan_job_id).first()
                if job:
                    job.root_path = f"{job.root_path}, db://{db_config.name}"
                    db.commit()

                # Escanear base de datos usando el lock de scan_engine
                scan_single_db_config(db_config, scan_job_id, db, scan_lock, entities=entities)
            except Exception as e:
                print(f"Error escaneando base de datos {db_config.name} en escaneo global: {e}")

        # Completar ejecución del Job
        job = db.query(ScanJob).filter(ScanJob.id == scan_job_id).first()
        if job:
            if scan_job_id in cancelled_jobs:
                job.status = "cancelled"
                cancelled_jobs.discard(scan_job_id)
            else:
                job.status = "completed"
            db.refresh(job)
            job.files_total = job.files_scanned + job.files_skipped
            job.completed_at = datetime.utcnow()
            db.commit()
            # Reportar fin de ejecución
            upshield_sync.sync_scan_status(job)
            if job.status == "completed":
                upshield_sync.sync_findings(job.id, db)

    except Exception as e:
        job = db.query(ScanJob).filter(ScanJob.id == scan_job_id).first()
        if job:
            job.status = "failed"
            job.error_message = f"Error crítico en el motor de escaneo: {str(e)}"
            db.refresh(job)
            job.files_total = job.files_scanned + job.files_skipped
            job.completed_at = datetime.utcnow()
            db.commit()
            # Reportar error a UpShield
            upshield_sync.sync_scan_status(job)
    finally:
        db.close()

def start_scan(db: Session, config: ScanConfig) -> ScanJob:
    """Inicia un escaneo y retorna el job creado. Ejecuta la lógica en background thread."""
    import json
    scan_paths = json.loads(config.scan_paths)
    extensions = json.loads(config.extensions)
    entities = json.loads(config.entities)

    job = ScanJob(
        status="pending",
        root_path=", ".join(scan_paths),
        started_at=datetime.utcnow(),
        files_total=0,
        files_scanned=0,
        files_skipped=0,
        findings_count=0
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Iniciar hilo de escaneo en background
    thread = threading.Thread(
        target=run_scan_async,
        args=(job.id, scan_paths, extensions, entities, config.max_workers),
        daemon=True
    )
    thread.start()

    return job

def cancel_scan(scan_job_id: int, db: Session) -> bool:
    """Solicita la cancelación de un scan job activo."""
    job = db.query(ScanJob).filter(ScanJob.id == scan_job_id).first()
    if not job or job.status not in ["pending", "running"]:
        return False

    cancelled_jobs.add(scan_job_id)
    job.status = "cancelled"
    job.completed_at = datetime.utcnow()
    db.commit()
    return True
