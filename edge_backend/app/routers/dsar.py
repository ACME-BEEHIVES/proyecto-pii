import os
import re
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel
from app.database import get_db
from app.models.finding import ScanFinding
from app.services import crypto_service
from app.services.identity_service import normalize_rut
from app.services import upshield_sync
from app.config import get_settings
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

router = APIRouter(prefix="/dsar")
settings = get_settings()


def _build_dsar_response(rut_or_email: str, archivos_encontrados: set, db: Session) -> dict:
    """Construye la respuesta DSAR a partir de los archivos encontrados."""
    if not archivos_encontrados:
        return {
            "rut_consultado": rut_or_email,
            "mensaje": "Titular no encontrado",
            "archivos_involucrados": 0,
            "resumen": {
                "archivos_involucrados": 0,
                "alertas_datos_sensibles": 0,
                "nivel_riesgo_ley21719": "LIMPIO"
            },
            "mapa_de_datos": {}
        }

    # Extraer todo el contexto de esos archivos específicos
    filters = []
    for path in archivos_encontrados:
        if path.startswith("db://"):
            parts = path.split("/")
            if len(parts) >= 5:
                prefix = "/".join(parts[:-2])
                row_id = parts[-1]
                pattern = f"{prefix}/%/{row_id}"
                filters.append(ScanFinding.file_path.like(pattern))
            else:
                filters.append(ScanFinding.file_path == path)
        else:
            filters.append(ScanFinding.file_path == path)

    if not filters:
        resultados = []
    else:
        resultados = db.query(ScanFinding).filter(or_(*filters)).all()

    mapa_datos: Dict[str, List[Dict[str, Any]]] = {}
    alertas_sensibles = 0

    for fila in resultados:
        if fila.file_path and fila.file_path.startswith("db://"):
            parts = fila.file_path.split("/")
            if len(parts) >= 5:
                db_config_name = parts[2]
                table_name = parts[3]
                row_id = parts[-1]
                nombre_doc = f"BD: {db_config_name} | Tabla: {table_name} (Fila ID: {row_id})"
            else:
                nombre_doc = fila.file_path
        else:
            nombre_doc = os.path.basename(fila.file_path) if fila.file_path else "documento_desconocido"

        entidad = fila.entity_type
        texto_guardado = fila.detected_text

        if nombre_doc not in mapa_datos:
            mapa_datos[nombre_doc] = []

        # Lógica de Descifrado
        if fila.is_sensitive:
            alertas_sensibles += 1
            texto_legible = crypto_service.decrypt(texto_guardado)
        else:
            texto_legible = texto_guardado

        mapa_datos[nombre_doc].append({
            "categoria_legal": entidad,
            "dato_encontrado": texto_legible,
            "estado_almacenamiento": "Cifrado en BD" if fila.is_sensitive else "Sin Cifrar",
            "fecha_deteccion": fila.created_at.astimezone().isoformat() if fila.created_at else None,
            "is_resolved": fila.is_resolved or False,
            "resolution_method": fila.resolution_method,
            "resolved_by": fila.resolved_by,
            "resolved_at": fila.resolved_at.astimezone().isoformat() if fila.resolved_at else None,
        })

    return {
        "rut_consultado": rut_or_email,
        "fecha_consulta": datetime.now().astimezone().isoformat(),
        "resumen": {
            "archivos_involucrados": len(archivos_encontrados),
            "alertas_datos_sensibles": alertas_sensibles,
            "nivel_riesgo_ley21719": "ALTO" if alertas_sensibles > 0 else "MODERADO"
        },
        "mapa_de_datos": mapa_datos
    }


def _find_files_by_rut(target_norm: str, db: Session) -> set:
    """Busca archivos que contengan hallazgos de un RUT normalizado."""
    all_rut_findings = db.query(ScanFinding).filter(
        ScanFinding.entity_type == "CHILE_RUT"
    ).all()

    archivos = set()
    for f in all_rut_findings:
        if f.is_sensitive and f.detected_text:
            rut_val = crypto_service.decrypt(f.detected_text)
        else:
            rut_val = f.detected_text or ""
        if normalize_rut(rut_val) == target_norm:
            if f.file_path:
                archivos.add(f.file_path)
    return archivos


def _find_files_by_email(email: str, db: Session) -> set:
    """Busca archivos que contengan hallazgos de un email."""
    email_lower = email.strip().lower()
    all_email_findings = db.query(ScanFinding).filter(
        ScanFinding.entity_type == "EMAIL_ADDRESS"
    ).all()

    archivos = set()
    for f in all_email_findings:
        if f.is_sensitive and f.detected_text:
            val = crypto_service.decrypt(f.detected_text)
        else:
            val = f.detected_text or ""
        if val.strip().lower() == email_lower:
            if f.file_path:
                archivos.add(f.file_path)
    return archivos


def _find_files_by_name(name: str, db: Session) -> set:
    """Busca archivos que contengan hallazgos PERSON que coincidan con el nombre.
    
    Requiere que TODAS las partes del nombre (>= 3 chars) aparezcan en
    hallazgos PERSON del MISMO archivo. Ejemplo: "Pablo Ortiz" solo matchea
    archivos donde exista un PERSON con "pablo" Y otro (o el mismo) con "ortiz".
    Esto evita falsos positivos en BDs con miles de registros.
    """
    name_parts = [p.strip().lower() for p in name.split() if len(p.strip()) >= 3]
    if not name_parts:
        return set()

    all_person_findings = db.query(ScanFinding).filter(
        ScanFinding.entity_type == "PERSON"
    ).all()

    # Agrupar textos PERSON por archivo
    file_texts: dict[str, list[str]] = {}
    for f in all_person_findings:
        if not f.file_path:
            continue
        if f.is_sensitive and f.detected_text:
            val = crypto_service.decrypt(f.detected_text)
        else:
            val = f.detected_text or ""
        val_lower = val.strip().lower()
        if val_lower:
            file_texts.setdefault(f.file_path, []).append(val_lower)

    # Solo incluir archivos donde TODAS las partes del nombre aparezcan
    archivos = set()
    for file_path, texts in file_texts.items():
        combined = " ".join(texts)
        if all(part in combined for part in name_parts):
            archivos.add(file_path)
    return archivos


@router.get("/{rut}")
def get_dsar_mapping(rut: str, name: Optional[str] = None, db: Session = Depends(get_db)):
    """Ejecuta el mapeo DSAR por RUT, descifrando los datos sensibles al vuelo.
    
    Opcionalmente acepta ?name=NombreCompleto para ampliar la búsqueda
    con hallazgos PERSON (útil cuando OCR no detecta RUT en imágenes).
    """
    rut_clean = rut.strip()
    target_norm = normalize_rut(rut_clean)

    if not target_norm or len(target_norm) < 7:
        return {
            "rut_consultado": rut_clean,
            "mensaje": "RUT inválido o muy corto",
            "archivos_involucrados": 0,
            "resumen": {
                "archivos_involucrados": 0,
                "alertas_datos_sensibles": 0,
                "nivel_riesgo_ley21719": "LIMPIO"
            },
            "mapa_de_datos": {}
        }

    archivos_encontrados = _find_files_by_rut(target_norm, db)

    # Ampliar búsqueda con nombre si se proporciona
    if name:
        archivos_encontrados.update(_find_files_by_name(name, db))

    response_data = _build_dsar_response(rut_clean, archivos_encontrados, db)

    # Sincronizar respuesta DSAR con UpShield Cloud
    try:
        upshield_sync.sync_dsar_response(rut_clean, response_data)
    except Exception:
        pass  # offline-first: no bloquear si la nube no responde

    return response_data


# -------------------------------------------------------------------------
# Endpoint para consultas DSAR desde UpShield Cloud (plataforma central)
# -------------------------------------------------------------------------
class CloudDsarRequest(BaseModel):
    """Solicitud DSAR originada desde la plataforma UpShield Central."""
    rut: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    request_type: str = "access"  # access, rectification, suppression, opposition, portability


@router.post("/cloud-query")
def cloud_dsar_query(
    body: CloudDsarRequest,
    db: Session = Depends(get_db),
    x_api_key: str = Header(None),
):
    """
    Endpoint que UpShield Central invoca para solicitar datos ARSOP de un titular.
    Autenticado via X-API-Key header.
    Soporta búsqueda por RUT, email, o ambos.
    """
    # Validar API key
    if not x_api_key or x_api_key != settings.UPSHIELD_API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida.")

    if not body.rut and not body.email and not body.name:
        raise HTTPException(status_code=400, detail="Debe proporcionar un RUT, email o nombre.")

    archivos_encontrados: set = set()

    # Buscar por RUT
    if body.rut:
        target_norm = normalize_rut(body.rut.strip())
        if target_norm and len(target_norm) >= 7:
            archivos_encontrados.update(_find_files_by_rut(target_norm, db))

    # Buscar por email
    if body.email:
        archivos_encontrados.update(_find_files_by_email(body.email, db))

    # Buscar por nombre
    if body.name:
        archivos_encontrados.update(_find_files_by_name(body.name, db))

    identifier = body.rut or body.email or body.name or ""
    response_data = _build_dsar_response(identifier, archivos_encontrados, db)
    response_data["request_type"] = body.request_type
    response_data["source"] = "edge-agent"
    response_data["tenant_id"] = settings.UPSHIELD_TENANT_ID

    return response_data
