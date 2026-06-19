from pydantic import BaseModel
from typing import Dict, Optional

class ServiceHealthStatus(BaseModel):
    status: str
    message: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str
    services: Dict[str, ServiceHealthStatus]
