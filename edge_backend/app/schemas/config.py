from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class ScanConfigBase(BaseModel):
    scan_paths: List[str]
    extensions: List[str]
    entities: List[str]
    max_workers: int = 1
    is_active: bool = True
    schedule_type: str = "none"
    schedule_time: str = "00:00"
    schedule_day: int = 0
    db_host: str = ""
    db_port: str = ""
    db_user: str = ""
    db_password: str = ""
    db_name: str = ""
    upshield_api_url: str = ""
    upshield_api_key: str = ""
    upshield_tenant_id: str = ""
    upshield_sync_interval: int = 60
    alert_emails_enabled: bool = False
    alert_check_interval: int = 60
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_to: str = ""

class ScanConfigUpdate(ScanConfigBase):
    pass

class ScanConfigResponse(ScanConfigBase):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True
