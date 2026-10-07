from sqlalchemy import Column, String, Text, DateTime, Index
from app.database import Base
from datetime import datetime

class FileControl(Base):
    """Modelo para control incremental de archivos (tabla control_archivos)."""
    __tablename__ = "control_archivos"

    hash_ruta = Column(String(64), primary_key=True)
    file_path = Column("archivo_nombre", String(1024), nullable=True, index=True)
    content_hash = Column("hash_archivo", String(64), nullable=True, index=True)
    last_scanned_at = Column("ultima_actualizacion", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
