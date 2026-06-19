from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ScanJobBase(BaseModel):
    root_path: Optional[str] = None

class ScanJobResponse(ScanJobBase):
    id: int
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    files_total: int
    files_scanned: int
    files_skipped: int
    findings_count: int
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

class StopScanRequest(BaseModel):
    job_id: int
