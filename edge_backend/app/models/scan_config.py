from sqlalchemy import Column, Integer, Text, Boolean, DateTime, String
from app.database import Base
from datetime import datetime

class ScanConfig(Base):
    """Modelo para registrar la configuración dinámica de escaneo."""
    __tablename__ = "scan_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_paths = Column(Text, nullable=False) # JSON array, e.g., ["C:\\ruta1"]
    extensions = Column(Text, nullable=False) # JSON array, e.g., [".pdf", ".docx"]
    entities = Column(Text, nullable=False) # JSON array, e.g., ["CHILE_RUT", "EMAIL_ADDRESS"]
    max_workers = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    schedule_type = Column(String(50), default="none", server_default="none", nullable=False)
    schedule_time = Column(String(10), default="00:00", server_default="00:00", nullable=False)
    schedule_day = Column(Integer, default=0, server_default="0", nullable=False)
    last_scheduled_run = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
