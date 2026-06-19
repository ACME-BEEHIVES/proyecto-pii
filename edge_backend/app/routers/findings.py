import os
import re
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.database import get_db
from app.models.finding import ScanFinding
from app.models.file_control import FileControl
from app.schemas.finding import ScanFindingResponse, FindingStats, ResolveRequest
from app.services import crypto_service
from app.services import upshield_sync
from datetime import datetime
from typing import List, Optional

router = APIRouter(prefix="/findings")

@router.get("", response_model=List[ScanFindingResponse])
def get_findings(
    entity_type: Optional[str] = None,
    is_resolved: Optional[bool] = None,
    file_path: Optional[str] = None,
    is_sensitive: Optional[bool] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Obtiene un listado paginado de hallazgos. No descifra los datos sensibles (cumple CHK-PII-002)."""
    query = db.query(ScanFinding)
    if entity_type:
        query = query.filter(ScanFinding.entity_type == entity_type)
    if is_resolved is not None:
        query = query.filter(ScanFinding.is_resolved == is_resolved)
    if is_sensitive is not None:
        query = query.filter(ScanFinding.is_sensitive == is_sensitive)
    if file_path:
        search_term = file_path.strip()
        # Normalizar: quitar puntos y guiones para buscar RUTs flexiblemente
        normalized_search = re.sub(r'[^0-9kK]', '', search_term).lower()
        
        # Construir condiciones de búsqueda
        conditions = [
            ScanFinding.file_path.like(f"%{search_term}%"),
            ScanFinding.file_name.like(f"%{search_term}%"),
            (ScanFinding.is_sensitive == False) & (ScanFinding.detected_text.like(f"%{search_term}%")),
        ]
        
        # Si parece un RUT (solo dígitos+k), buscar también con formato
        if normalized_search and len(normalized_search) >= 4:
            # Buscar el patrón normalizado contra texto detectado de RUTs
            # Reconstruir posibles formatos: 8565137 -> buscar con LIKE %565137%
            conditions.append(
                (ScanFinding.is_sensitive == False) & 
                (ScanFinding.entity_type == 'CHILE_RUT') &
                (ScanFinding.detected_text.like(f"%{normalized_search[:-1]}%"))  # sin dígito verificador
            )
            # También buscar con puntos si tiene formato parcial
            if len(normalized_search) >= 7:
                # Intentar formato X.XXX.XXX
                digits = normalized_search
                if len(digits) >= 8:  # e.g. 85651374
                    body = digits[:-1]  # 8565137
                    dv = digits[-1]  # 4
                    # Buscar como X.XXX.XXX-D
                    if len(body) >= 7:
                        formatted = f"{body[:-6]}.{body[-6:-3]}.{body[-3:]}-{dv}"
                        conditions.append(
                            (ScanFinding.is_sensitive == False) & 
                            (ScanFinding.detected_text == formatted)
                        )
        
        query = query.filter(or_(*conditions))

    findings = query.order_by(ScanFinding.created_at.desc()).offset(skip).limit(limit).all()
    return findings

@router.get("/stats", response_model=FindingStats)
def get_findings_stats(db: Session = Depends(get_db)):
    """Genera estadísticas generales y KPIs para el dashboard."""
    # 1. Totales generales
    total_findings = db.query(ScanFinding).count()
    active_findings = db.query(ScanFinding).filter(ScanFinding.is_resolved == False).count()
    resolved_findings = total_findings - active_findings

    # 2. Desglose de elementos escaneados
    scanned_files_count = db.query(FileControl).filter(~FileControl.file_path.like("db://%")).count()
    scanned_db_cells_count = db.query(FileControl).filter(FileControl.file_path.like("db://%")).count()

    from app.models.db_config import DbConfig
    active_db_configs_count = db.query(DbConfig).filter(DbConfig.is_active == True).count()

    # 3. Desglose de hallazgos activos por origen
    findings_in_files_count = db.query(ScanFinding).filter(
        ScanFinding.is_resolved == False,
        ~ScanFinding.file_path.like("db://%")
    ).count()
    findings_in_db_count = db.query(ScanFinding).filter(
        ScanFinding.is_resolved == False,
        ScanFinding.file_path.like("db://%")
    ).count()

    # 4. Agrupación por tipo de entidad (solo activos)
    by_type_query = db.query(ScanFinding.entity_type, func.count(ScanFinding.id)).filter(ScanFinding.is_resolved == False).group_by(ScanFinding.entity_type).all()
    findings_by_type = {t: count for t, count in by_type_query if t}

    # 5. Agrupación por severidad (solo activos)
    # ALTO: is_sensitive == True, MODERADO: is_sensitive == False
    alto_count = db.query(ScanFinding).filter(
        ScanFinding.is_resolved == False,
        ScanFinding.is_sensitive == True
    ).count()
    moderado_count = db.query(ScanFinding).filter(
        ScanFinding.is_resolved == False,
        ScanFinding.is_sensitive == False
    ).count()

    total_scanned_elements = scanned_files_count + scanned_db_cells_count
    distinct_affected_paths = db.query(ScanFinding.file_path).filter(ScanFinding.is_resolved == False).distinct().count()

    findings_by_severity = {
        "ALTO": alto_count,
        "MODERADO": moderado_count,
        "LIMPIO": total_scanned_elements - distinct_affected_paths
    }
    if findings_by_severity["LIMPIO"] < 0:
        findings_by_severity["LIMPIO"] = 0

    # 6. Agrupación por carpeta/tabla (solo activos)
    findings_by_folder = {}
    all_findings_paths = db.query(ScanFinding.file_path).filter(ScanFinding.is_resolved == False).all()
    for (f_path,) in all_findings_paths:
        if f_path:
            if f_path.startswith("db://"):
                parts = f_path.split("/")
                if len(parts) >= 4:
                    dir_name = "/".join(parts[:4]) # db://{db_config_name}/{table_name}
                else:
                    dir_name = "/".join(parts[:-1]) or "Base de Datos"
            else:
                dir_name = os.path.dirname(f_path) or "Raíz"
            findings_by_folder[dir_name] = findings_by_folder.get(dir_name, 0) + 1

    # 7. Determinar riesgo global
    has_active_sensitive = db.query(ScanFinding).filter(
        ScanFinding.is_resolved == False,
        ScanFinding.entity_type.in_(crypto_service.ENTIDADES_SENSIBLES)
    ).first() is not None

    if has_active_sensitive:
        global_risk_level = "ALTO"
    elif active_findings > 0:
        global_risk_level = "MODERADO"
    else:
        global_risk_level = "LIMPIO"

    return FindingStats(
        total_findings=total_findings,
        active_findings=active_findings,
        resolved_findings=resolved_findings,
        findings_by_type=findings_by_type,
        findings_by_severity=findings_by_severity,
        findings_by_folder=findings_by_folder,
        scanned_files_count=scanned_files_count,
        scanned_db_cells_count=scanned_db_cells_count,
        active_db_configs_count=active_db_configs_count,
        findings_in_files_count=findings_in_files_count,
        findings_in_db_count=findings_in_db_count,
        global_risk_level=global_risk_level
    )

@router.get("/{finding_id}", response_model=ScanFindingResponse)
def get_finding_detail(finding_id: int, db: Session = Depends(get_db)):
    """Obtiene el detalle de un hallazgo. Descifra el dato sensible al vuelo (cumple CHK-PII-002)."""
    finding = db.query(ScanFinding).filter(ScanFinding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Hallazgo no encontrado.")

    # Convertimos a esquema Pydantic para no alterar la entidad de la BD directamente
    response = ScanFindingResponse.model_validate(finding)
    if finding.is_sensitive and finding.detected_text:
        response.detected_text = crypto_service.decrypt(finding.detected_text)

    return response

@router.patch("/{finding_id}/resolve", response_model=ScanFindingResponse)
def resolve_finding(finding_id: int, body: ResolveRequest, db: Session = Depends(get_db)):
    """Marca un hallazgo como resuelto con evidencia de mitigación."""
    finding = db.query(ScanFinding).filter(ScanFinding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Hallazgo no encontrado.")

    finding.is_resolved = True
    finding.resolved_at = datetime.utcnow()
    finding.resolved_by = body.resolved_by
    finding.resolution_method = body.resolution_method
    finding.resolution_notes = body.resolution_notes
    db.commit()
    db.refresh(finding)

    # Reportar resolución a UpShield Cloud (async-safe, offline-first)
    try:
        upshield_sync.sync_resolution(finding.id, db)
    except Exception:
        pass  # No bloquear la respuesta si la nube no responde

    return finding
