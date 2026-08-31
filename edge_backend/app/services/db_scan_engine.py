import json
import os
import hashlib
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.scan_job import ScanJob
from app.models.file_control import FileControl
from app.models.finding import ScanFinding
from app.models.db_config import DbConfig
from app.services import presidio_service, crypto_service, upshield_sync

# Bloqueo para estadísticas de escaneos
db_scan_lock = threading.Lock()

# Separador para concatenar columnas de una fila en un solo texto
_COL_SEPARATOR = "\n---COL_SEP---\n"

# Cantidad de celdas procesadas antes de hacer commit + actualizar progreso
_BATCH_COMMIT_SIZE = 500

# Workers para paralelizar el análisis de filas
_DB_SCAN_WORKERS = 4


def estimate_db_config_cells(db_config: DbConfig) -> int:
    """Calcula la cantidad total de celdas de texto que serán escaneadas para esta configuración de BD."""
    try:
        conn_str = crypto_service.decrypt(db_config.connection_string)
        tables_map = json.loads(db_config.tables_to_scan) if isinstance(db_config.tables_to_scan, str) else db_config.tables_to_scan
    except Exception as e:
        print(f"Error decodificando o descifrando config para estimar celdas: {e}")
        return 0

    total_cells = 0
    try:
        engine = create_engine(conn_str, pool_pre_ping=True)
        inspector = inspect(engine)
        for table_name, columns in tables_map.items():
            if not columns:
                continue

            pk_cols = inspector.get_pk_constraint(table_name).get("constrained_columns", [])
            pk_name = pk_cols[0] if pk_cols else None
            if not pk_name:
                table_columns = [col["name"] for col in inspector.get_columns(table_name)]
                for common_id in ["id", "ID", "code", "codigo"]:
                    if common_id in table_columns:
                        pk_name = common_id
                        break
                if not pk_name and table_columns:
                    pk_name = table_columns[0]
            if not pk_name:
                continue

            # Para contar las filas
            table_escaped = f"`{table_name}`" if db_config.db_type in ["mysql", "mssql"] else f'"{table_name}"'
            query_str = f"SELECT COUNT(*) FROM {table_escaped}"
            with engine.connect() as conn:
                res = conn.execute(text(query_str)).fetchone()
                row_count = res[0] if res else 0

            # Las columnas de texto a escanear (excluyendo la clave primaria)
            scanned_cols_count = len([c for c in columns if c != pk_name])
            total_cells += row_count * scanned_cols_count
        engine.dispose()
    except Exception as e:
        print(f"Error estimando celdas para {db_config.name}: {e}")
    return total_cells


def _analyze_row_batch(
    row_dict: dict,
    pk_name: str,
    columns: list[str],
    db_config_name: str,
    table_name: str,
    hash_cache: dict[str, str],
    entities: list[str] = None
) -> list[dict]:
    """
    Analiza todas las columnas de una fila en una sola llamada a Presidio.
    Retorna una lista de resultados para persistir, sin tocar la BD.
    
    Optimización clave: concatena todas las columnas con separador y envía
    1 sola llamada HTTP a Presidio por fila en vez de N llamadas (una por columna).
    """
    row_id = row_dict.get(pk_name)
    if row_id is None:
        return []

    # Recopilar columnas con contenido válido
    col_data = []  # [(col_name, value, logical_path, cell_hash, path_hash, is_modified)]
    for col_name in columns:
        if col_name == pk_name:
            continue

        val = str(row_dict.get(col_name) or "").strip()
        logical_path = f"db://{db_config_name}/{table_name}/{col_name}/{row_id}"
        path_hash = hashlib.md5(logical_path.encode('utf-8')).hexdigest()

        if len(val) < 3:
            col_data.append({
                "col_name": col_name, "val": val, "logical_path": logical_path,
                "path_hash": path_hash, "cell_hash": "", "skip": True, "is_modified": False
            })
            continue

        cell_hash = hashlib.md5(val.encode('utf-8')).hexdigest()

        # Verificar control incremental en caché (en vez de query a BD)
        cached_hash = hash_cache.get(path_hash)
        if cached_hash and cached_hash == cell_hash:
            col_data.append({
                "col_name": col_name, "val": val, "logical_path": logical_path,
                "path_hash": path_hash, "cell_hash": cell_hash, "skip": True, "is_modified": False
            })
            continue

        is_modified = cached_hash is not None
        col_data.append({
            "col_name": col_name, "val": val, "logical_path": logical_path,
            "path_hash": path_hash, "cell_hash": cell_hash, "skip": False, "is_modified": is_modified
        })

    # Separar celdas que necesitan análisis vs las que se saltan
    cells_to_analyze = [c for c in col_data if not c["skip"]]
    cells_skipped = [c for c in col_data if c["skip"]]

    results = []

    # Agregar skipped al resultado
    for c in cells_skipped:
        results.append({"type": "skip", **c})

    if not cells_to_analyze:
        return results

    # Concatenar todas las columnas en un solo texto con separador
    # y trackear los offsets para mapear hallazgos a su columna original
    combined_text = ""
    col_offsets = []  # [(start_offset, end_offset, col_data_entry)]
    context_words = []

    for c in cells_to_analyze:
        start = len(combined_text)
        combined_text += c["val"]
        end = len(combined_text)
        col_offsets.append((start, end, c))
        combined_text += _COL_SEPARATOR
        # Agregar nombre de columna como contexto
        if c["col_name"]:
            context_words.extend(c["col_name"].split("_"))

    # 1 sola llamada a Presidio para toda la fila
    try:
        findings = presidio_service.analyze_text(
            combined_text,
            entities=entities,
            context=context_words if context_words else None
        )
    except Exception as e:
        print(f"Error analizando fila {row_id} de {table_name}: {e}")
        findings = []

    # Mapear hallazgos a sus columnas originales
    findings_by_col: dict[str, list[dict]] = {c["col_name"]: [] for c in cells_to_analyze}

    if isinstance(findings, list):
        for h in findings:
            if h.get('score', 0) < 0.5:
                continue
            h_start = h['start']
            h_end = h['end']
            # Determinar a qué columna pertenece este hallazgo
            for col_start, col_end, col_entry in col_offsets:
                if h_start >= col_start and h_end <= col_end:
                    # Ajustar offsets relativos a la columna
                    local_start = h_start - col_start
                    local_end = h_end - col_start
                    texto_original = col_entry["val"][local_start:local_end]
                    entity_type = h['entity_type']

                    is_sensitive = crypto_service.is_sensitive_entity(entity_type)
                    if not is_sensitive and crypto_service.check_text_contains_sensitive(texto_original, entity_type):
                        is_sensitive = True

                    findings_by_col[col_entry["col_name"]].append({
                        "entity_type": entity_type,
                        "detected_text": crypto_service.encrypt(texto_original) if is_sensitive else crypto_service.mask_text(texto_original, entity_type),
                        "search_hash": crypto_service.compute_search_hash(texto_original, entity_type),
                        "confidence_score": h['score'],
                        "is_sensitive": is_sensitive
                    })
                    break

    # Construir resultados para persistir
    for c in cells_to_analyze:
        results.append({
            "type": "analyzed",
            "findings": findings_by_col.get(c["col_name"], []),
            **c
        })

    return results


def scan_single_db_config(db_config: DbConfig, scan_job_id: int, local_db: Session, lock: threading.Lock, entities: list[str] = None) -> tuple[int, int]:
    """
    Escanea las tablas y columnas configuradas en la conexión de base de datos dada.
    OPTIMIZADO: Agrupa columnas por fila, pre-carga hashes, paraleliza con ThreadPool.
    """
    if entities is None:
        from app.models.scan_config import ScanConfig
        active_config = local_db.query(ScanConfig).filter(ScanConfig.is_active == True).first()
        if active_config and active_config.entities:
            try:
                entities = json.loads(active_config.entities)
            except Exception as e:
                print(f"Error parsing scan config entities in scan_single_db_config: {e}")

    # 1. Descifrar connection string
    conn_str = crypto_service.decrypt(db_config.connection_string)

    # Parsear las tablas y columnas a escanear
    tables_map = json.loads(db_config.tables_to_scan) if isinstance(db_config.tables_to_scan, str) else db_config.tables_to_scan

    # 2. Conectar a la base de datos externa
    external_engine = create_engine(conn_str, pool_pre_ping=True)
    inspector = inspect(external_engine)

    # 3. PRE-CARGAR todos los hashes de FileControl en memoria (1 query en vez de N)
    all_controls = local_db.query(FileControl.hash_ruta, FileControl.content_hash).filter(
        FileControl.file_path.like(f"db://{db_config.name}/%")
    ).all()
    hash_cache = {fc.hash_ruta: fc.content_hash for fc in all_controls}
    print(f"db_scan_engine: Pre-cargados {len(hash_cache)} hashes de control para {db_config.name}")

    total_cells_scanned = 0
    total_findings_found = 0

    # Acumuladores batch para reducir queries UPDATE
    batch_scanned = 0
    batch_skipped = 0
    batch_findings = 0

    for table_name, columns in tables_map.items():
        from app.services.scan_engine import cancelled_jobs
        if scan_job_id in cancelled_jobs:
            print(f"db_scan_engine: Scan job {scan_job_id} cancelled. Aborting table loop.")
            break
        if not columns:
            continue

        # Obtener clave primaria de la tabla
        pk_cols = inspector.get_pk_constraint(table_name).get("constrained_columns", [])
        pk_name = pk_cols[0] if pk_cols else None

        if not pk_name:
            table_columns = [col["name"] for col in inspector.get_columns(table_name)]
            for common_id in ["id", "ID", "code", "codigo"]:
                if common_id in table_columns:
                    pk_name = common_id
                    break
            if not pk_name and table_columns:
                pk_name = table_columns[0]

        if not pk_name:
            print(f"No se pudo determinar clave primaria para la tabla {table_name}. Se omite.")
            continue

        # Construir consulta select
        select_cols = [pk_name] + [c for c in columns if c != pk_name]
        select_cols_str = ", ".join([f"`{c}`" if db_config.db_type in ["mysql", "mssql"] else f'"{c}"' for c in select_cols])
        table_escaped = f"`{table_name}`" if db_config.db_type in ["mysql", "mssql"] else f'"{table_name}"'
        query_str = f"SELECT {select_cols_str} FROM {table_escaped}"

        try:
            with external_engine.connect() as conn:
                result = conn.execute(text(query_str))
                rows = result.fetchall()
        except Exception as e:
            print(f"Error ejecutando query en tabla {table_name}: {e}")
            continue

        print(f"db_scan_engine: Tabla {table_name}: {len(rows)} filas × {len(columns)-1} cols = {len(rows) * (len(columns)-1)} celdas")

        # Procesar filas en paralelo con ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=_DB_SCAN_WORKERS) as pool:
            futures = {}
            for row in rows:
                from app.services.scan_engine import cancelled_jobs
                if scan_job_id in cancelled_jobs:
                    break
                row_dict = dict(zip(select_cols, row))
                future = pool.submit(
                    _analyze_row_batch,
                    row_dict, pk_name, columns, db_config.name, table_name,
                    hash_cache, entities
                )
                futures[future] = row_dict.get(pk_name)

            # Procesar resultados a medida que terminan
            for future in as_completed(futures):
                from app.services.scan_engine import cancelled_jobs
                if scan_job_id in cancelled_jobs:
                    break

                try:
                    row_results = future.result(timeout=120)
                except Exception as e:
                    print(f"Error procesando fila: {e}")
                    continue

                for cell_result in row_results:
                    total_cells_scanned += 1

                    if cell_result["type"] == "skip":
                        batch_skipped += 1
                    else:
                        batch_scanned += 1
                        logical_path = cell_result["logical_path"]
                        logical_name = f"{table_name} : {cell_result['col_name']} (ID:{cell_result.get('val', '')[:20]})"
                        path_hash = cell_result["path_hash"]
                        cell_hash = cell_result["cell_hash"]

                        # Eliminar hallazgos anteriores si fue modificada
                        if cell_result.get("is_modified"):
                            local_db.query(ScanFinding).filter(ScanFinding.file_path == logical_path).delete()

                        # Guardar nuevos hallazgos
                        cell_findings = cell_result.get("findings", [])
                        for hf in cell_findings:
                            finding = ScanFinding(
                                scan_job_id=scan_job_id,
                                file_path=logical_path,
                                file_name=f"{table_name} : {cell_result['col_name']} (ID:{futures[future]})",
                                entity_type=hf["entity_type"],
                                detected_text=hf["detected_text"],
                                search_hash=hf.get("search_hash", ""),
                                confidence_score=hf["confidence_score"],
                                is_sensitive=hf["is_sensitive"],
                                is_resolved=True,
                                resolved_at=datetime.utcnow(),
                                resolution_method="Auto-mitigado",
                                created_at=datetime.utcnow()
                            )
                            local_db.add(finding)
                            batch_findings += 1
                            total_findings_found += 1

                        # Actualizar control_archivos
                        file_control = local_db.query(FileControl).filter(FileControl.hash_ruta == path_hash).first()
                        if not file_control:
                            file_control = FileControl(
                                hash_ruta=path_hash,
                                file_path=logical_path,
                                content_hash=cell_hash,
                                last_scanned_at=datetime.utcnow()
                            )
                            local_db.add(file_control)
                        else:
                            file_control.content_hash = cell_hash
                            file_control.last_scanned_at = datetime.utcnow()

                        # Actualizar hash_cache para evitar re-análisis en la misma sesión
                        hash_cache[path_hash] = cell_hash

                    # Batch commit + progreso cada N celdas
                    if (batch_scanned + batch_skipped) >= _BATCH_COMMIT_SIZE:
                        local_db.query(ScanJob).filter(ScanJob.id == scan_job_id).update({
                            ScanJob.files_scanned: ScanJob.files_scanned + batch_scanned,
                            ScanJob.files_skipped: ScanJob.files_skipped + batch_skipped,
                            ScanJob.findings_count: ScanJob.findings_count + batch_findings
                        })
                        local_db.commit()
                        batch_scanned = 0
                        batch_skipped = 0
                        batch_findings = 0

    # Flush final de acumuladores
    if (batch_scanned + batch_skipped) > 0:
        local_db.query(ScanJob).filter(ScanJob.id == scan_job_id).update({
            ScanJob.files_scanned: ScanJob.files_scanned + batch_scanned,
            ScanJob.files_skipped: ScanJob.files_skipped + batch_skipped,
            ScanJob.findings_count: ScanJob.findings_count + batch_findings
        })
        local_db.commit()

    external_engine.dispose()
    return total_cells_scanned, total_findings_found


def scan_database_connection(db_config_id: int, scan_job_id: int):
    """Escanea las tablas y columnas configuradas en la conexión de base de datos dada."""
    local_db = SessionLocal()
    try:
        print(f"db_scan_engine: Starting scan for config ID {db_config_id}, Job ID {scan_job_id}")
        config = local_db.query(DbConfig).filter(DbConfig.id == db_config_id).first()
        if not config:
            print("db_scan_engine: Config not found!")
            return
        if not config.is_active:
            print("db_scan_engine: Config not active!")
            return

        with db_scan_lock:
            job = local_db.query(ScanJob).filter(ScanJob.id == scan_job_id).first()
            if job:
                job.status = "running"
                local_db.commit()
                upshield_sync.sync_scan_status(job)

        # Obtener entidades de la configuración activa
        from app.models.scan_config import ScanConfig
        entities = None
        config_obj = local_db.query(ScanConfig).filter(ScanConfig.is_active == True).first()
        if config_obj and config_obj.entities:
            try:
                entities = json.loads(config_obj.entities)
            except Exception as e:
                print(f"Error parsing scan config entities in scan_database_connection: {e}")

        cells_scanned, findings_found = scan_single_db_config(config, scan_job_id, local_db, db_scan_lock, entities=entities)

        # Completar el job
        with db_scan_lock:
            job = local_db.query(ScanJob).filter(ScanJob.id == scan_job_id).first()
            if job:
                local_db.refresh(job)
                from app.services.scan_engine import cancelled_jobs
                if scan_job_id in cancelled_jobs:
                    job.status = "cancelled"
                    cancelled_jobs.discard(scan_job_id)
                else:
                    job.status = "completed"
                job.files_total = job.files_scanned + job.files_skipped
                job.completed_at = datetime.utcnow()
                local_db.commit()
                # Sincronizar reporte
                upshield_sync.sync_scan_status(job)
                if job.status == "completed":
                    upshield_sync.sync_findings(job.id, local_db)

    except Exception as e:
        print(f"Error durante el escaneo de base de datos {db_config_id}: {e}")
        with db_scan_lock:
            job = local_db.query(ScanJob).filter(ScanJob.id == scan_job_id).first()
            if job:
                local_db.refresh(job)
                job.status = "failed"
                job.error_message = f"Error crítico: {str(e)}"
                job.files_total = job.files_scanned + job.files_skipped
                job.completed_at = datetime.utcnow()
                local_db.commit()
                upshield_sync.sync_scan_status(job)
    finally:
        local_db.close()

def start_database_scan(db_config_id: int, db: Session) -> ScanJob:
    """Inicia un escaneo asíncrono para una base de datos externa."""
    config = db.query(DbConfig).filter(DbConfig.id == db_config_id).first()
    if not config:
        raise Exception("Configuración de base de datos no encontrada.")

    # Estimación de celdas a escanear en esta base de datos
    cells_est = estimate_db_config_cells(config)

    # Crear ScanJob representativo
    job = ScanJob(
        status="pending",
        root_path=f"db://{config.name}",
        started_at=datetime.utcnow(),
        files_total=max(1, cells_est),
        files_scanned=0,
        files_skipped=0,
        findings_count=0
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Lanzar hilo en background
    thread = threading.Thread(
        target=scan_database_connection,
        args=(db_config_id, job.id),
        daemon=True
    )
    thread.start()

    return job
