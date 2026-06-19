import os
import re
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.finding import ScanFinding
from app.services import redaction_service, crypto_service
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/redaction")

class RedactionRequest(BaseModel):
    file_path: str

def _normalize_rut(rut: str) -> str:
    """Normaliza un RUT quitando puntos, guiones y espacios."""
    return re.sub(r'[^0-9kK]', '', rut).lower()

@router.get("/search")
def search_files_for_redaction(q: str = Query(..., min_length=2, description="Buscar por RUT, nombre o correo"), db: Session = Depends(get_db)):
    """Busca archivos que contengan hallazgos coincidentes con el query (RUT, nombre o correo)."""
    q_stripped = q.strip()
    q_norm = _normalize_rut(q_stripped)
    
    # 1. Buscar hallazgos no cifrados de archivos que coincidan (excluyendo bases de datos)
    findings = db.query(ScanFinding).filter(
        ScanFinding.is_sensitive == False,
        ScanFinding.detected_text.isnot(None),
        ~ScanFinding.file_path.like("db://%")
    ).all()
    
    matched_file_paths: dict[str, list[dict]] = {}
    
    for f in findings:
        text = f.detected_text or ""
        match = False
        
        # Match por RUT normalizado
        if f.entity_type == "CHILE_RUT":
            if _normalize_rut(text) == q_norm or q_norm in _normalize_rut(text) or _normalize_rut(text) in q_norm:
                match = True
        
        # Match por nombre (case-insensitive, parcial)
        if f.entity_type == "PERSON" and q_stripped.lower() in text.lower():
            match = True
        
        # Match por email (case-insensitive, parcial)
        if f.entity_type == "EMAIL_ADDRESS" and q_stripped.lower() in text.lower():
            match = True
        
        # Match genérico en texto plano
        if not match and q_stripped.lower() in text.lower():
            match = True
        
        if match and f.file_path:
            if f.file_path not in matched_file_paths:
                matched_file_paths[f.file_path] = []
            matched_file_paths[f.file_path].append({
                "id": f.id,
                "entity_type": f.entity_type,
                "text": text,
                "file_name": f.file_name or os.path.basename(f.file_path),
            })
    
    # 2. Agrupar por archivo
    results = []
    for file_path, file_findings in matched_file_paths.items():
        entity_types = list(set(ff["entity_type"] for ff in file_findings))
        # Contar total de hallazgos en ese archivo (no solo los que coinciden)
        total_in_file = db.query(func.count(ScanFinding.id)).filter(ScanFinding.file_path == file_path).scalar()
        results.append({
            "file_path": file_path,
            "file_name": file_findings[0]["file_name"],
            "matched_findings": len(file_findings),
            "total_findings_in_file": total_in_file,
            "entity_types": entity_types,
            "sample_texts": [ff["text"] for ff in file_findings[:5]],
        })
    
    # Ordenar por cantidad de coincidencias descendente
    results.sort(key=lambda x: x["matched_findings"], reverse=True)
    
    return {"query": q_stripped, "total_files": len(results), "files": results}

@router.post("/preview")
def preview_redaction(payload: RedactionRequest, db: Session = Depends(get_db)):
    """Muestra una vista previa de qué términos de datos personales serian censurados."""
    from app.services.path_service import translate_path
    translated_path = translate_path(payload.file_path)
    
    if not os.path.exists(translated_path):
        raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {payload.file_path}")
        
    texts = redaction_service.get_texts_to_redact(translated_path, db)
    findings = db.query(ScanFinding).filter(ScanFinding.file_path == translated_path).all()
    
    details = []
    for f in findings:
        text = crypto_service.decrypt(f.detected_text) if f.is_sensitive else f.detected_text
        details.append({
            "id": f.id,
            "entity_type": f.entity_type,
            "text": text,
            "is_sensitive": f.is_sensitive
        })
        
    return {
        "file_path": payload.file_path,
        "findings_count": len(details),
        "texts_to_redact": texts,
        "details": details
    }

@router.post("/generate")
def generate_redacted_file(payload: RedactionRequest, db: Session = Depends(get_db)):
    """Genera y descarga una copia censurada del archivo."""
    from app.services.path_service import translate_path
    translated_path = translate_path(payload.file_path)
    
    try:
        # Carpeta local en el workspace
        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        output_dir = os.path.join(app_dir, "redacted_files")
        
        output_path = redaction_service.redact_file(translated_path, db, output_dir)
        
        return FileResponse(
            path=output_path,
            filename=os.path.basename(output_path),
            media_type="application/octet-stream"
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al censurar archivo: {str(e)}")

@router.post("/in-place")
def redact_in_place(payload: RedactionRequest, db: Session = Depends(get_db)):
    """Censura y sobreescribe directamente el archivo original en el host."""
    from app.services.path_service import translate_path
    translated_path = translate_path(payload.file_path)
    try:
        redaction_service.redact_file_in_place(translated_path, db)
        return {"status": "ok", "message": "Archivo censurado in-situ correctamente."}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en remediación in-situ: {str(e)}")

@router.post("/quarantine")
def quarantine(payload: RedactionRequest, db: Session = Depends(get_db)):
    """Mueve el archivo original a la carpeta de cuarentena y deja un placeholder."""
    from app.services.path_service import translate_path
    translated_path = translate_path(payload.file_path)
    try:
        new_path = redaction_service.quarantine_file(translated_path, db)
        return {"status": "ok", "message": "Archivo movido a cuarentena correctamente.", "new_path": new_path}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al mover a cuarentena: {str(e)}")
