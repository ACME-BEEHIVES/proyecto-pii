from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import identity_service
from typing import List, Dict, Any

router = APIRouter(prefix="/identity")

@router.get("/subjects", response_model=List[Dict[str, Any]])
def list_identity_subjects(db: Session = Depends(get_db)):
    """Retorna los sujetos identificados mediante la correlación de hallazgos (Gráfico de Identidad)."""
    try:
        subjects = identity_service.get_identity_subjects(db)
        return subjects
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener el gráfico de identidad: {str(e)}")
