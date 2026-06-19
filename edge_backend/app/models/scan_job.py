from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database import Base
from datetime import datetime

class ScanJob(Base):
    """Modelo para registrar las ejecuciones de escaneo."""
    __tablename__ = "scan_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String(50), default="pending", nullable=False) # pending, running, completed, failed, cancelled
    root_path = Column(String(1024), nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    files_total = Column(Integer, default=0, nullable=False)
    files_scanned = Column(Integer, default=0, nullable=False)
    files_skipped = Column(Integer, default=0, nullable=False)
    findings_count = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
