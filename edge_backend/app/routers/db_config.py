from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.db_config import DbConfig
from app.schemas.db_config import DbConfigCreate, DbConfigResponse, DbConfigUpdate
from app.schemas.scan import ScanJobResponse
from app.services import crypto_service, db_scan_engine
from sqlalchemy import create_engine, text, inspect
from typing import List, Dict, Optional
import json
from pydantic import BaseModel

router = APIRouter(prefix="/db-config")

@router.post("", response_model=DbConfigResponse)
def create_db_config(payload: DbConfigCreate, db: Session = Depends(get_db)):
    """Crea una nueva configuración de escaneo de base de datos."""
    # Verificar si el nombre ya existe
    existing = db.query(DbConfig).filter(DbConfig.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe una conexión con este nombre.")

    # Cifrar la connection string antes de guardar
    try:
        encrypted_conn = crypto_service.encrypt(payload.connection_string)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cifrando las credenciales: {str(e)}")

    db_config = DbConfig(
        name=payload.name,
        db_type=payload.db_type,
        connection_string=encrypted_conn,
        tables_to_scan=json.dumps(payload.tables_to_scan),
        is_active=payload.is_active
    )
    db.add(db_config)
    db.commit()
    db.refresh(db_config)

    # Parsear tablas para el response
    response_data = DbConfigResponse(
        id=db_config.id,
        name=db_config.name,
        db_type=db_config.db_type,
        tables_to_scan=payload.tables_to_scan,
        is_active=db_config.is_active,
        created_at=db_config.created_at,
        updated_at=db_config.updated_at
    )
    return response_data

@router.get("", response_model=List[DbConfigResponse])
def list_db_configs(db: Session = Depends(get_db)):
    """Lista todas las conexiones de base de datos configuradas."""
    configs = db.query(DbConfig).all()
    results = []
    for c in configs:
        try:
            tables = json.loads(c.tables_to_scan) if isinstance(c.tables_to_scan, str) else c.tables_to_scan
        except Exception:
            tables = {}
        results.append(DbConfigResponse(
            id=c.id,
            name=c.name,
            db_type=c.db_type,
            tables_to_scan=tables,
            is_active=c.is_active,
            created_at=c.created_at,
            updated_at=c.updated_at
        ))
    return results

@router.get("/{config_id}", response_model=DbConfigResponse)
def get_db_config(config_id: int, db: Session = Depends(get_db)):
    """Obtiene el detalle de una conexión de base de datos específica."""
    c = db.query(DbConfig).filter(DbConfig.id == config_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Conexión de BD no encontrada.")

    try:
        tables = json.loads(c.tables_to_scan) if isinstance(c.tables_to_scan, str) else c.tables_to_scan
    except Exception:
        tables = {}

    return DbConfigResponse(
        id=c.id,
        name=c.name,
        db_type=c.db_type,
        tables_to_scan=tables,
        is_active=c.is_active,
        created_at=c.created_at,
        updated_at=c.updated_at
    )

@router.put("/{config_id}", response_model=DbConfigResponse)
def update_db_config(config_id: int, payload: DbConfigUpdate, db: Session = Depends(get_db)):
    """Actualiza una conexión de base de datos existente."""
    c = db.query(DbConfig).filter(DbConfig.id == config_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Conexión de BD no encontrada.")

    if payload.name is not None:
        # Verificar duplicidad de nombre
        dup = db.query(DbConfig).filter(DbConfig.name == payload.name, DbConfig.id != config_id).first()
        if dup:
            raise HTTPException(status_code=400, detail="Ya existe una conexión con este nombre.")
        c.name = payload.name

    if payload.db_type is not None:
        c.db_type = payload.db_type

    if payload.connection_string is not None and payload.connection_string.strip() != "":
        try:
            c.connection_string = crypto_service.encrypt(payload.connection_string)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error cifrando las credenciales: {str(e)}")

    if payload.tables_to_scan is not None:
        c.tables_to_scan = json.dumps(payload.tables_to_scan)

    if payload.is_active is not None:
        c.is_active = payload.is_active

    db.commit()
    db.refresh(c)

    try:
        tables = json.loads(c.tables_to_scan) if isinstance(c.tables_to_scan, str) else c.tables_to_scan
    except Exception:
        tables = {}

    return DbConfigResponse(
        id=c.id,
        name=c.name,
        db_type=c.db_type,
        tables_to_scan=tables,
        is_active=c.is_active,
        created_at=c.created_at,
        updated_at=c.updated_at
    )

@router.delete("/{config_id}")
def delete_db_config(config_id: int, db: Session = Depends(get_db)):
    """Elimina una conexión de base de datos configurada."""
    c = db.query(DbConfig).filter(DbConfig.id == config_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Conexión de BD no encontrada.")
    db.delete(c)
    db.commit()
    return {"message": "Conexión de BD eliminada correctamente."}

class DbTestRequest(BaseModel):
    db_type: str
    host: Optional[str] = None
    port: Optional[int] = None
    user: Optional[str] = None
    password: Optional[str] = ""
    database: Optional[str] = None
    connection_string: Optional[str] = None

class DbSchemaDiscoverRequest(BaseModel):
    db_type: str
    host: Optional[str] = None
    port: Optional[int] = None
    user: Optional[str] = None
    password: Optional[str] = ""
    database: Optional[str] = None
    connection_string: Optional[str] = None

@router.post("/test")
def test_db_connection(payload: DbTestRequest):
    """Prueba la conexión a una base de datos externa antes de guardarla."""
    import urllib.parse
    
    conn_str = payload.connection_string
    if conn_str and conn_str.strip():
        conn_str = conn_str.replace("@localhost", "@host.docker.internal").replace("@127.0.0.1", "@host.docker.internal")
    else:
        if not payload.host or not payload.database or not payload.user:
            return {"status": "error", "message": "Faltan parámetros de conexión necesarios (host, database, user)"}
        
        host_val = payload.host
        if host_val in ["localhost", "127.0.0.1"]:
            host_val = "host.docker.internal"
            
        escaped_password = urllib.parse.quote_plus(payload.password) if payload.password else ""
        escaped_user = urllib.parse.quote_plus(payload.user) if payload.user else ""
        
        if payload.db_type == "mysql":
            port_val = payload.port or 3306
            conn_str = f"mysql+mysqlconnector://{escaped_user}:{escaped_password}@{host_val}:{port_val}/{payload.database}"
        elif payload.db_type == "postgresql":
            port_val = payload.port or 5432
            conn_str = f"postgresql://{escaped_user}:{escaped_password}@{host_val}:{port_val}/{payload.database}"
        elif payload.db_type == "mssql":
            port_val = payload.port or 1433
            conn_str = f"mssql+pymssql://{escaped_user}:{escaped_password}@{host_val}:{port_val}/{payload.database}"
        else:
            return {"status": "error", "message": f"Tipo de base de datos no soportado: {payload.db_type}"}
            
    try:
        engine = create_engine(conn_str, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine.dispose()
        return {"status": "ok", "message": "Conexión establecida correctamente.", "connection_string": conn_str}
    except Exception as e:
        return {"status": "error", "message": f"Fallo al conectar: {str(e)}"}

@router.post("/discover-schema")
def discover_schema(payload: DbSchemaDiscoverRequest):
    """Obtiene el esquema de tablas y columnas (solo tipos de texto) de la BD especificada."""
    import urllib.parse
    
    conn_str = payload.connection_string
    if conn_str and conn_str.strip():
        conn_str = conn_str.replace("@localhost", "@host.docker.internal").replace("@127.0.0.1", "@host.docker.internal")
    else:
        if not payload.host or not payload.database or not payload.user:
            raise HTTPException(status_code=400, detail="Faltan parámetros de conexión necesarios (host, database, user)")
            
        host_val = payload.host
        if host_val in ["localhost", "127.0.0.1"]:
            host_val = "host.docker.internal"
            
        escaped_password = urllib.parse.quote_plus(payload.password) if payload.password else ""
        escaped_user = urllib.parse.quote_plus(payload.user) if payload.user else ""
        
        if payload.db_type == "mysql":
            port_val = payload.port or 3306
            conn_str = f"mysql+mysqlconnector://{escaped_user}:{escaped_password}@{host_val}:{port_val}/{payload.database}"
        elif payload.db_type == "postgresql":
            port_val = payload.port or 5432
            conn_str = f"postgresql://{escaped_user}:{escaped_password}@{host_val}:{port_val}/{payload.database}"
        elif payload.db_type == "mssql":
            port_val = payload.port or 1433
            conn_str = f"mssql+pymssql://{escaped_user}:{escaped_password}@{host_val}:{port_val}/{payload.database}"
        else:
            raise HTTPException(status_code=400, detail=f"Tipo de base de datos no soportado: {payload.db_type}")
            
    try:
        engine = create_engine(conn_str, pool_pre_ping=True)
        inspector = inspect(engine)
        
        tables_schema = {}
        table_names = inspector.get_table_names()
        
        for table in table_names:
            columns = inspector.get_columns(table)
            text_columns = []
            for col in columns:
                col_name = col["name"]
                col_type = str(col["type"]).upper()
                is_text = any(t in col_type for t in ["CHAR", "TEXT", "VARCHAR", "NCHAR", "NVARCHAR", "CLOB", "STRING"])
                is_numeric = any(t in col_type for t in ["DECIMAL", "NUMERIC", "FLOAT", "DOUBLE", "REAL"])
                is_date = any(t in col_type for t in ["DATE", "DATETIME", "TIMESTAMP"])
                if is_text or is_numeric or is_date:
                    text_columns.append(col_name)
                    
            if text_columns:
                tables_schema[table] = text_columns
                
        engine.dispose()
        return {"status": "ok", "tables": tables_schema, "connection_string": conn_str}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al conectar u obtener esquema: {str(e)}")
 
 
@router.post("/{config_id}/discover-schema")
def discover_schema_existing(config_id: int, db: Session = Depends(get_db)):
    """Obtiene el esquema de tablas y columnas de una conexión de BD existente."""
    c = db.query(DbConfig).filter(DbConfig.id == config_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Conexión de BD no encontrada.")
        
    try:
        conn_str = crypto_service.decrypt(c.connection_string)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error descifrando connection string: {str(e)}")
        
    try:
        engine = create_engine(conn_str, pool_pre_ping=True)
        inspector = inspect(engine)
        
        tables_schema = {}
        table_names = inspector.get_table_names()
        
        for table in table_names:
            columns = inspector.get_columns(table)
            text_columns = []
            for col in columns:
                col_name = col["name"]
                col_type = str(col["type"]).upper()
                is_text = any(t in col_type for t in ["CHAR", "TEXT", "VARCHAR", "NCHAR", "NVARCHAR", "CLOB", "STRING"])
                is_numeric = any(t in col_type for t in ["DECIMAL", "NUMERIC", "FLOAT", "DOUBLE", "REAL"])
                is_date = any(t in col_type for t in ["DATE", "DATETIME", "TIMESTAMP"])
                if is_text or is_numeric or is_date:
                    text_columns.append(col_name)
                    
            if text_columns:
                tables_schema[table] = text_columns
                
        engine.dispose()
        return {"status": "ok", "tables": tables_schema}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al conectar u obtener esquema: {str(e)}")


@router.post("/{config_id}/scan", response_model=ScanJobResponse)
def run_db_scan(config_id: int, db: Session = Depends(get_db)):
    """Inicia el proceso de escaneo asíncrono para la conexión especificada."""
    try:
        job = db_scan_engine.start_database_scan(config_id, db)
        return job
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error iniciando el escaneo de BD: {str(e)}")
