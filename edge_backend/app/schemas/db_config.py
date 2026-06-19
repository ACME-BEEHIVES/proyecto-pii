from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Optional

class DbConfigBase(BaseModel):
    name: str
    db_type: str # 'mysql', 'postgresql', 'mssql'
    connection_string: str # En texto plano para entrada, el backend la cifra
    tables_to_scan: Dict[str, List[str]] # {"tabla1": ["col1", "col2"]}
    is_active: bool = True

class DbConfigCreate(DbConfigBase):
    pass

class DbConfigUpdate(BaseModel):
    name: Optional[str] = None
    db_type: Optional[str] = None
    connection_string: Optional[str] = None
    tables_to_scan: Optional[Dict[str, List[str]]] = None
    is_active: Optional[bool] = None

class DbConfigResponse(BaseModel):
    id: int
    name: str
    db_type: str
    tables_to_scan: Dict[str, List[str]]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
