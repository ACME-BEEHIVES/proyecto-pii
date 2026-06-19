import pytest
import requests
from datetime import datetime
from unittest.mock import patch, MagicMock
from app.services import upshield_sync
from app.models.scan_job import ScanJob
from app.models.finding import ScanFinding
from app.database import SessionLocal

@pytest.fixture
def mock_settings():
    with patch("app.services.upshield_sync.settings") as mock:
        mock.UPSHIELD_API_URL = "https://api.upshield.io"
        mock.UPSHIELD_API_KEY = "test-api-key"
        mock.UPSHIELD_TENANT_ID = "test-tenant-id"
        mock.UPSHIELD_SYNC_INTERVAL = 1
        yield mock

# 1. Tests for send_request_with_backoff
@patch("requests.post")
def test_send_request_success(mock_post, mock_settings):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "ok"}
    mock_post.return_value = mock_response

    success, code, res = upshield_sync.send_request_with_backoff("POST", "/api/test", {"data": "val"})
    assert success is True
    assert code == 200
    assert res == {"status": "ok"}
    mock_post.assert_called_once()

@patch("requests.post")
@patch("time.sleep")  # Mock sleep to avoid delay in tests
def test_send_request_backoff_retry_success(mock_sleep, mock_post, mock_settings):
    # First attempt fails (500), second attempt succeeds (200)
    mock_response_fail = MagicMock()
    mock_response_fail.status_code = 500
    
    mock_response_success = MagicMock()
    mock_response_success.status_code = 200
    mock_response_success.json.return_value = {"status": "ok"}
    
    mock_post.side_effect = [mock_response_fail, mock_response_success]

    success, code, res = upshield_sync.send_request_with_backoff("POST", "/api/test", {"data": "val"})
    assert success is True
    assert code == 200
    assert res == {"status": "ok"}
    assert mock_post.call_count == 2
    mock_sleep.assert_called_once_with(1)

@patch("requests.post")
@patch("time.sleep")
def test_send_request_backoff_fail_eventually(mock_sleep, mock_post, mock_settings):
    # All 3 attempts fail with 500
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_post.return_value = mock_response

    success, code, res = upshield_sync.send_request_with_backoff("POST", "/api/test", {"data": "val"}, max_retries=3)
    assert success is False
    assert mock_post.call_count == 3
    assert mock_sleep.call_count == 2

@patch("requests.post")
def test_send_request_client_error_no_retry(mock_post, mock_settings):
    # 400 Bad Request should fail immediately without retry
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    mock_post.return_value = mock_response

    success, code, res = upshield_sync.send_request_with_backoff("POST", "/api/test", {"data": "val"}, max_retries=3)
    assert success is False
    assert code == 400
    assert mock_post.call_count == 1

# 2. Test sync_health
@patch("app.services.upshield_sync.send_request_with_backoff")
def test_sync_health(mock_send, mock_settings):
    mock_send.return_value = (True, 200, {})
    health_payload = {"status": "ok", "service": "upshield-edge-agent", "services": {}}
    
    success = upshield_sync.sync_health(health_payload)
    assert success is True
    mock_send.assert_called_once_with("POST", "/api/edge/sync/health", health_payload)

# 3. Test sync_scan_status
@patch("app.services.upshield_sync.send_request_with_backoff")
def test_sync_scan_status(mock_send, mock_settings):
    mock_send.return_value = (True, 200, {})
    
    job = ScanJob(
        id=123,
        status="running",
        root_path="/tmp/scan",
        files_total=10,
        files_scanned=2,
        files_skipped=1,
        findings_count=5,
        started_at=datetime(2026, 6, 4, 12, 0, 0),
        completed_at=None,
        error_message=None
    )
    
    success = upshield_sync.sync_scan_status(job)
    assert success is True
    
    mock_send.assert_called_once()
    payload = mock_send.call_args[0][2]
    assert payload["job_id"] == 123
    assert payload["status"] == "running"
    assert payload["files_total"] == 10
    assert payload["started_at"] == "2026-06-04T12:00:00"

# 4. Test sync_findings (Privacy & Aggregation)
@patch("app.services.upshield_sync.send_request_with_backoff")
def test_sync_findings(mock_send, mock_settings):
    mock_send.return_value = (True, 200, {})
    
    db = SessionLocal()
    try:
        # Primero creamos un ScanJob para cumplir con la restricción de clave foránea
        job = ScanJob(
            status="completed",
            root_path="C:\\sync_test",
            files_total=2,
            files_scanned=2,
            files_skipped=0,
            findings_count=4
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        # Create some findings to aggregate using the actual job.id
        # Same file, same entity type (should be aggregated)
        finding1 = ScanFinding(
            scan_job_id=job.id,
            file_path="C:\\sync_test\\file1.txt",
            file_name="file1.txt",
            entity_type="CHILE_RUT",
            detected_text="11.111.111-1",
            confidence_score=0.9,
            is_sensitive=False
        )
        finding2 = ScanFinding(
            scan_job_id=job.id,
            file_path="C:\\sync_test\\file1.txt",
            file_name="file1.txt",
            entity_type="CHILE_RUT",
            detected_text="22.222.222-2",
            confidence_score=0.95,
            is_sensitive=False
        )
        # Different entity type
        finding3 = ScanFinding(
            scan_job_id=job.id,
            file_path="C:\\sync_test\\file1.txt",
            file_name="file1.txt",
            entity_type="EMAIL_ADDRESS",
            detected_text="test@example.com",
            confidence_score=0.8,
            is_sensitive=False
        )
        # Different file, sensitive entity
        finding4 = ScanFinding(
            scan_job_id=job.id,
            file_path="C:\\sync_test\\file2.txt",
            file_name="file2.txt",
            entity_type="DATA_SALUD",
            detected_text="some-encrypted-health-info",
            confidence_score=0.85,
            is_sensitive=True
        )
        
        db.add(finding1)
        db.add(finding2)
        db.add(finding3)
        db.add(finding4)
        db.commit()
        
        success = upshield_sync.sync_findings(job.id, db)
        assert success is True
        
        mock_send.assert_called_once()
        sent_payload = mock_send.call_args[0][2]
        assert sent_payload["scan_job_id"] == job.id
        assert sent_payload["tenant_id"] == "test-tenant-id"
        
        findings = sent_payload["findings"]
        assert len(findings) == 3  # Aggregated into 3 groups
        
        # Verify that no text data (detected_text) was sent
        for item in findings:
            assert "detected_text" not in item
            assert "text" not in item
            
        # Verify aggregation details
        rut_group = next(f for f in findings if f["entity_type"] == "CHILE_RUT")
        assert rut_group["file_name"] == "file1.txt"
        assert rut_group["count"] == 2
        assert rut_group["max_confidence"] == 0.95
        assert rut_group["is_sensitive"] is False
        
        salud_group = next(f for f in findings if f["entity_type"] == "DATA_SALUD")
        assert salud_group["file_name"] == "file2.txt"
        assert salud_group["count"] == 1
        assert salud_group["max_confidence"] == 0.85
        assert salud_group["is_sensitive"] is True
        
        # Cleanup
        db.delete(finding1)
        db.delete(finding2)
        db.delete(finding3)
        db.delete(finding4)
        db.delete(job)
        db.commit()
    finally:
        db.close()


# 5. Test run_heartbeat_loop triggers health calls
@patch("time.sleep")
@patch("app.database.SessionLocal")
@patch("app.services.tika_service.check_health", return_value=True)
@patch("app.services.presidio_service.check_health", return_value=True)
@patch("app.services.upshield_sync.sync_health")
def test_heartbeat_loop_execution(mock_sync_health, mock_presidio, mock_tika, mock_db, mock_sleep, mock_settings):
    # Mock db execution to simulate healthy database
    mock_conn = MagicMock()
    mock_db.return_value = mock_conn
    
    # We want time.sleep to raise an exception on the second call to break the infinite loop
    mock_sleep.side_effect = [None, ValueError("Stop loop")]
    
    with pytest.raises(ValueError, match="Stop loop"):
        upshield_sync.run_heartbeat_loop()
        
    mock_sync_health.assert_called_once()
    payload = mock_sync_health.call_args[0][0]
    assert payload["status"] == "ok"
    assert payload["services"]["database"]["status"] == "healthy"
    assert payload["services"]["tika"]["status"] == "healthy"
    assert payload["services"]["presidio"]["status"] == "healthy"
