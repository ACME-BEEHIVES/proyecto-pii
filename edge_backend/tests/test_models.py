from app.database import SessionLocal
from app.models.scan_job import ScanJob
from app.models.scan_config import ScanConfig
from app.models.finding import ScanFinding
from app.models.file_control import FileControl
from datetime import datetime

def test_db_connection_and_models():
    db = SessionLocal()
    try:
        # 1. Test ScanJob model
        job = ScanJob(
            status="completed",
            root_path="C:\\test_path",
            files_total=10,
            files_scanned=8,
            files_skipped=2,
            findings_count=3,
            completed_at=datetime.utcnow()
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        
        assert job.id is not None
        assert job.status == "completed"
        
        # 2. Test ScanFinding model (referencing job.id)
        finding = ScanFinding(
            scan_job_id=job.id,
            file_path="C:\\test_path\\test.txt",
            file_name="test.txt",
            entity_type="CHILE_RUT",
            detected_text="12.345.678-9",
            confidence_score=0.95,
            is_sensitive=False,
            is_resolved=False
        )
        db.add(finding)
        db.commit()
        db.refresh(finding)
        
        assert finding.id is not None
        assert finding.scan_job_id == job.id
        
        # 3. Test FileControl model
        control = FileControl(
            hash_ruta="test_hash_ruta",
            file_path="C:\\test_path\\test.txt",
            content_hash="test_content_hash"
        )
        db.add(control)
        db.commit()
        db.refresh(control)
        
        assert control.hash_ruta == "test_hash_ruta"
        
        # 4. Test ScanConfig model
        config = ScanConfig(
            scan_paths='["C:\\\\test_path"]',
            extensions='[".txt", ".pdf"]',
            entities='["CHILE_RUT", "EMAIL_ADDRESS"]',
            max_workers=2,
            is_active=True
        )
        db.add(config)
        db.commit()
        db.refresh(config)
        
        assert config.id is not None
        
        # Clean up
        db.delete(finding)
        db.delete(job)
        db.delete(control)
        db.delete(config)
        db.commit()
        
    finally:
        db.close()
