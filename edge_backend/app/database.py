from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import get_settings

_engine = None
_SessionLocal = None

def get_engine():
    global _engine
    if _engine is None:
        db_url = get_settings().DATABASE_URL
        connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
        _engine = create_engine(
            db_url,
            connect_args=connect_args,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            pool_recycle=3600,
        )
    return _engine

def get_sessionmaker():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal

def recreate_db_engine(new_db_url: str):
    global _engine, _SessionLocal
    if _engine is not None:
        try:
            _engine.dispose()
        except Exception:
            pass
    connect_args = {"check_same_thread": False} if new_db_url.startswith("sqlite") else {}
    _engine = create_engine(
        new_db_url,
        connect_args=connect_args,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_recycle=3600,
    )
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

class DynamicEngine:
    def __getattr__(self, name):
        return getattr(get_engine(), name)

class DynamicSessionLocal:
    def __call__(self):
        return get_sessionmaker()()

engine = DynamicEngine()
SessionLocal = DynamicSessionLocal()

from sqlalchemy import MetaData

naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=naming_convention)
Base = declarative_base(metadata=metadata)



def get_db():
    """Dependency de FastAPI para inyectar sesion de BD."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
