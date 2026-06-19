import re
import os
from sqlalchemy.orm import Session
from app.models.finding import ScanFinding
from app.services import crypto_service
from typing import Dict, Any, List

def normalize_rut(rut_str: str) -> str:
    """Normaliza un RUT eliminando puntos, guiones y espacios, y pasando la K a mayúscula."""
    if not rut_str:
        return ""
    clean = re.sub(r'[^0-9kK]', '', rut_str)
    return clean.upper()

def format_rut(rut_str: str) -> str:
    """Formatea un RUT a formato estándar 12.345.678-K."""
    clean = normalize_rut(rut_str)
    if not clean or len(clean) < 2:
        return rut_str
    dv = clean[-1]
    nums = clean[:-1]
    try:
        formatted_nums = f"{int(nums):,}".replace(",", ".")
        return f"{formatted_nums}-{dv}"
    except ValueError:
        return rut_str

def are_paths_related(path1: str, path2: str) -> bool:
    """Verifica si dos rutas lógicas son idénticas o corresponden al mismo registro en base de datos."""
    if path1 == path2:
        return True
    if path1 and path2 and path1.startswith("db://") and path2.startswith("db://"):
        parts1 = path1.split("/")
        parts2 = path2.split("/")
        if len(parts1) >= 5 and len(parts2) >= 5:
            # Compara: db_config, tabla y row_id
            return parts1[2] == parts2[2] and parts1[3] == parts2[3] and parts1[-1] == parts2[-1]
    return False

def get_identity_subjects(db: Session) -> List[Dict[str, Any]]:
    """Agrupa y correlaciona hallazgos para construir perfiles de sujetos (Ley 21.719) en memoria, O(N)."""
    # 1. Subconsulta para obtener las rutas que tienen al menos un RUT
    subquery = db.query(ScanFinding.file_path).filter(
        ScanFinding.entity_type == "CHILE_RUT"
    ).distinct().subquery()
    
    # 2. Consultar solo las columnas necesarias uniendo con la subconsulta
    results = db.query(
        ScanFinding.id,
        ScanFinding.file_path,
        ScanFinding.entity_type,
        ScanFinding.detected_text,
        ScanFinding.is_sensitive
    ).join(
        subquery,
        ScanFinding.file_path == subquery.c.file_path
    ).all()
    
    findings_by_group: Dict[str, List[tuple]] = {}
    rut_findings_by_group: Dict[str, List[tuple]] = {}
    
    for f_id, f_path, f_entity_type, f_detected_text, f_is_sensitive in results:
        if not f_path:
            continue
            
        # Determinar clave de grupo
        # Para archivos: la ruta del archivo es el grupo.
        # Para bases de datos: db://{db_config}/{table_name}/{col_name}/{row_id} -> grupo: db://{db_config}/{table_name}/{row_id}
        if f_path.startswith("db://"):
            parts = f_path.split("/")
            if len(parts) >= 5:
                group_key = f"db://{parts[2]}/{parts[3]}/{parts[-1]}"
            else:
                group_key = f_path
        else:
            group_key = f_path
            
        f_tuple = (f_id, f_path, f_entity_type, f_detected_text, f_is_sensitive)
        
        if group_key not in findings_by_group:
            findings_by_group[group_key] = []
        findings_by_group[group_key].append(f_tuple)
        
        if f_entity_type == "CHILE_RUT":
            if group_key not in rut_findings_by_group:
                rut_findings_by_group[group_key] = []
            rut_findings_by_group[group_key].append(f_tuple)
            
    subjects: Dict[str, Dict[str, Any]] = {}
    
    # 2. Correlacionar hallazgos del mismo grupo
    for group_key, rufs in rut_findings_by_group.items():
        group_findings = findings_by_group.get(group_key, [])
        for rf_id, rf_path, rf_entity_type, rf_detected_text, rf_is_sensitive in rufs:
            rut_val = crypto_service.decrypt(rf_detected_text) if rf_is_sensitive else rf_detected_text
            if not rut_val:
                continue
                
            norm_rut = normalize_rut(rut_val)
            if not norm_rut:
                continue
                
            if norm_rut not in subjects:
                subjects[norm_rut] = {
                    "rut": format_rut(rut_val),
                    "names": set(),
                    "emails": set(),
                    "phones": set(),
                    "birth_dates": set(),
                    "files": set(),
                    "risk_level": "MODERADO",
                    "findings_count": 0,
                    "findings_ids": []
                }
                
            subjects[norm_rut]["files"].add(rf_path)
            if rf_id not in subjects[norm_rut]["findings_ids"]:
                subjects[norm_rut]["findings_ids"].append(rf_id)
                subjects[norm_rut]["findings_count"] += 1
            if rf_is_sensitive:
                subjects[norm_rut]["risk_level"] = "ALTO"
                
            for gf_id, gf_path, gf_entity_type, gf_detected_text, gf_is_sensitive in group_findings:
                decrypted = crypto_service.decrypt(gf_detected_text) if gf_is_sensitive else gf_detected_text
                if not decrypted:
                    continue
                    
                if gf_entity_type == "PERSON":
                    if len(decrypted.strip()) > 3:
                        subjects[norm_rut]["names"].add(decrypted.strip())
                elif gf_entity_type == "EMAIL_ADDRESS":
                    subjects[norm_rut]["emails"].add(decrypted.strip().lower())
                elif gf_entity_type == "PHONE_NUMBER":
                    subjects[norm_rut]["phones"].add(decrypted.strip())
                elif gf_entity_type == "DATE_TIME":
                    subjects[norm_rut]["birth_dates"].add(decrypted.strip())
                    
                if gf_is_sensitive or gf_entity_type in ["DATA_SALUD", "DATA_SEXUALIDAD", "DATA_POLITICA", "DATA_RELIGION", "DATA_ETNIA"]:
                    subjects[norm_rut]["risk_level"] = "ALTO"
                    
                if gf_id not in subjects[norm_rut]["findings_ids"]:
                    subjects[norm_rut]["findings_ids"].append(gf_id)
                    subjects[norm_rut]["findings_count"] += 1

    # 3. Formatear resultados para retorno JSON
    results_list = []
    for norm_rut, sub in subjects.items():
        display_files = []
        for f in sub["files"]:
            if f.startswith("db://"):
                parts = f.split("/")
                if len(parts) >= 5:
                    display_files.append(f"BD: {parts[2]} | Tabla: {parts[3]}")
                else:
                    display_files.append(f)
            else:
                display_files.append(os.path.basename(f))
                
        results_list.append({
            "rut": sub["rut"],
            "names": list(sub["names"]),
            "emails": list(sub["emails"]),
            "phones": list(sub["phones"]),
            "birth_dates": list(sub["birth_dates"]),
            "files": display_files,
            "file_paths": list(sub["files"]),
            "risk_level": sub["risk_level"],
            "findings_count": sub["findings_count"]
        })
        
    return results_list
