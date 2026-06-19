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
    # 1. Obtener todos los hallazgos (incluyendo resueltos, un titular sigue siendo titular)
    all_findings = db.query(ScanFinding).all()
    
    findings_by_group: Dict[str, List[ScanFinding]] = {}
    rut_findings_by_group: Dict[str, List[ScanFinding]] = {}
    
    for f in all_findings:
        f_path = f.file_path
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
            
        if group_key not in findings_by_group:
            findings_by_group[group_key] = []
        findings_by_group[group_key].append(f)
        
        if f.entity_type == "CHILE_RUT":
            if group_key not in rut_findings_by_group:
                rut_findings_by_group[group_key] = []
            rut_findings_by_group[group_key].append(f)
            
    subjects: Dict[str, Dict[str, Any]] = {}
    
    # 2. Correlacionar hallazgos del mismo grupo
    for group_key, rufs in rut_findings_by_group.items():
        group_findings = findings_by_group.get(group_key, [])
        for rf in rufs:
            rut_val = crypto_service.decrypt(rf.detected_text) if rf.is_sensitive else rf.detected_text
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
                
            subjects[norm_rut]["files"].add(rf.file_path)
            if rf.id not in subjects[norm_rut]["findings_ids"]:
                subjects[norm_rut]["findings_ids"].append(rf.id)
                subjects[norm_rut]["findings_count"] += 1
            if rf.is_sensitive:
                subjects[norm_rut]["risk_level"] = "ALTO"
                
            for gf in group_findings:
                decrypted = crypto_service.decrypt(gf.detected_text) if gf.is_sensitive else gf.detected_text
                if not decrypted:
                    continue
                    
                if gf.entity_type == "PERSON":
                    if len(decrypted.strip()) > 3:
                        subjects[norm_rut]["names"].add(decrypted.strip())
                elif gf.entity_type == "EMAIL_ADDRESS":
                    subjects[norm_rut]["emails"].add(decrypted.strip().lower())
                elif gf.entity_type == "PHONE_NUMBER":
                    subjects[norm_rut]["phones"].add(decrypted.strip())
                elif gf.entity_type == "DATE_TIME":
                    subjects[norm_rut]["birth_dates"].add(decrypted.strip())
                    
                if gf.is_sensitive or gf.entity_type in ["DATA_SALUD", "DATA_SEXUALIDAD", "DATA_POLITICA", "DATA_RELIGION", "DATA_ETNIA"]:
                    subjects[norm_rut]["risk_level"] = "ALTO"
                    
                if gf.id not in subjects[norm_rut]["findings_ids"]:
                    subjects[norm_rut]["findings_ids"].append(gf.id)
                    subjects[norm_rut]["findings_count"] += 1

    # 3. Formatear resultados para retorno JSON
    results = []
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
                
        results.append({
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
        
    return results
