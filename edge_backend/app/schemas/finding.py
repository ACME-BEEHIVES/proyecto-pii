from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict

class ScanFindingResponse(BaseModel):
    id: int
    scan_job_id: Optional[int] = None
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    entity_type: Optional[str] = None
    detected_text: Optional[str] = None
    confidence_score: Optional[float] = None
    is_sensitive: Optional[bool] = None
    is_resolved: Optional[bool] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolution_method: Optional[str] = None
    resolution_notes: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class FindingStats(BaseModel):
    total_findings: int
    active_findings: int
    resolved_findings: int
    findings_by_type: Dict[str, int]
    findings_by_severity: Dict[str, int] # ALTO, MODERADO, LIMPIO
    findings_by_folder: Dict[str, int]
    scanned_files_count: int
    scanned_db_cells_count: int
    active_db_configs_count: int
    findings_in_files_count: int
    findings_in_db_count: int
    global_risk_level: str

class ResolveRequest(BaseModel):
    """Body para la solicitud de resolución de hallazgo con evidencia."""
    resolved_by: str
    resolution_method: str
    resolution_notes: str = ""
