from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from app.database import Base
from datetime import datetime

class DbConfig(Base):
    """Modelo para registrar las conexiones a bases de datos a escanear (tabla db_configs)."""
    __tablename__ = "db_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(191), unique=True, nullable=False)
    db_type = Column(String(50), nullable=False) # 'mysql', 'postgresql', 'mssql'
    connection_string = Column(Text, nullable=False) # Guardada cifrada con crypto_service
    tables_to_scan = Column(Text, nullable=False) # JSON: {"table": ["col1", "col2"]}
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
