from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configuracion del Edge Agent. Lee de .env automaticamente."""

    # Base de Datos
    DATABASE_URL: str = "mysql+mysqlconnector://root:@127.0.0.1:3306/pii_discovery"

    # Cifrado PII
    PII_ENCRYPTION_KEY: str = ""

    # Servicios Docker
    TIKA_URL: str = "http://localhost:9998/tika"
    PRESIDIO_URL: str = "http://localhost:5001/analyze"
    PRESIDIO_HEALTH_URL: str = "http://localhost:5001/health"

    # UpShield Central
    UPSHIELD_API_URL: str = ""
    UPSHIELD_API_KEY: str = ""
    UPSHIELD_TENANT_ID: str = ""
    UPSHIELD_SYNC_INTERVAL: int = 60

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    ENVIRONMENT: str = "development"

    # Alertas por Correo (SMTP)
    ALERT_EMAILS_ENABLED: bool = False
    ALERT_CHECK_INTERVAL: int = 60
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""
    SMTP_TO: str = ""

    # Scan defaults
    MAX_WORKERS: int = 1
    SCAN_EXTENSIONS: str = ".pdf,.docx,.xlsx,.xls,.doc,.txt,.jpg,.png,.csv"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"



@lru_cache()
def get_settings() -> Settings:
    return Settings()
