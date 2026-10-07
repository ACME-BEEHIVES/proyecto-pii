from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey
from app.database import Base
from datetime import datetime

class ScanFinding(Base):
    """Modelo para registrar los hallazgos de PII (tabla hallazgos)."""
    __tablename__ = "hallazgos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_job_id = Column(Integer, ForeignKey("scan_jobs.id"), nullable=True, index=True)
    file_path = Column("archivo_nombre", String(1024), nullable=True, index=True)
    file_name = Column(String(255), nullable=True)
    entity_type = Column("tipo_entidad", String(50), nullable=True, index=True)
    detected_text = Column("texto_detectado", Text, nullable=True)
    search_hash = Column(String(64), nullable=True, index=True)
    confidence_score = Column("puntaje_certeza", Float, nullable=True)
    is_sensitive = Column(Boolean, default=False, nullable=True, index=True)
    is_resolved = Column(Boolean, default=False, nullable=True, index=True)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String(100), nullable=True)
    resolution_method = Column(String(50), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column("fecha_deteccion", DateTime, default=datetime.utcnow)
