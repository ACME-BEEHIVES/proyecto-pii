import pytest
from unittest.mock import patch, MagicMock
from app.database import SessionLocal
from app.models.db_config import DbConfig
from app.models.scan_job import ScanJob
from app.models.finding import ScanFinding
from app.models.file_control import FileControl
from app.services import db_scan_engine
import json

@patch("app.services.db_scan_engine.create_engine")
@patch("app.services.db_scan_engine.inspect")
@patch("app.services.presidio_service.analyze_text")
@patch("app.services.upshield_sync.sync_scan_status")
@patch("app.services.upshield_sync.sync_findings")
def test_scan_database_connection(
    mock_sync_findings,
    mock_sync_status,
    mock_analyze_text,
    mock_inspect,
    mock_create_engine
):
    db_session = SessionLocal()
    try:
        # Limpiar posibles registros colgados de corridas fallidas previas
        db_session.query(ScanFinding).filter(ScanFinding.file_path.like("db://test_conn/%")).delete()
        db_session.query(FileControl).filter(FileControl.file_path.like("db://test_conn/%")).delete()
        db_session.query(ScanJob).filter(ScanJob.root_path == "db://test_conn").delete()
        db_session.query(DbConfig).filter(DbConfig.name == "test_conn").delete()
        db_session.commit()

        # Setup mocks
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            (1, "Juan Perez", "juan.perez@email.com")
        ]
        mock_conn.execute.return_value = mock_result
        
        mock_engine = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_create_engine.return_value = mock_engine

        mock_inspector = MagicMock()
        mock_inspector.get_pk_constraint.return_value = {"constrained_columns": ["id"]}
        mock_inspect.return_value = mock_inspector

        mock_analyze_text.return_value = [
            {"start": 0, "end": 10, "entity_type": "PERSON", "score": 0.85}
        ]

        from app.services import crypto_service
        # Create dummy DbConfig in database
        db_config = DbConfig(
            name="test_conn",
            db_type="mysql",
            connection_string=crypto_service.encrypt("sqlite:///:memory:"),
            tables_to_scan=json.dumps({"clientes": ["id", "nombre", "correo"]}),
            is_active=True
        )
        db_session.add(db_config)
        db_session.commit()

        # Create dummy ScanJob
        job = ScanJob(
            status="pending",
            root_path="db://test_conn",
            files_total=1,
            files_scanned=0,
            files_skipped=0,
            findings_count=0
        )
        db_session.add(job)
        db_session.commit()

        # Guardar los IDs en variables locales antes de cerrar la sesión
        job_id = job.id
        db_config_id = db_config.id

        # Run scan
        db_scan_engine.scan_database_connection(db_config_id, job_id)

        # Recreamos la sesión para poder ver los cambios commiteados en la otra transacción (REPEATABLE READ)
        db_session.commit()
        db_session.close()
        db_session = SessionLocal()

        # Verify that finding was created
        findings = db_session.query(ScanFinding).filter(ScanFinding.scan_job_id == job_id).all()
        assert len(findings) > 0
        assert findings[0].entity_type == "PERSON"
        assert findings[0].file_path == "db://test_conn/clientes/nombre/1"
        assert findings[0].file_name == "clientes : nombre (ID:1)"

        # Clean up
        db_session.query(ScanFinding).filter(ScanFinding.scan_job_id == job_id).delete()
        job_to_del = db_session.query(ScanJob).filter(ScanJob.id == job_id).first()
        if job_to_del:
            db_session.delete(job_to_del)
        config_to_del = db_session.query(DbConfig).filter(DbConfig.id == db_config_id).first()
        if config_to_del:
            db_session.delete(config_to_del)
        db_session.commit()

    finally:
        db_session.close()


@patch("app.services.db_scan_engine.create_engine")
@patch("app.services.db_scan_engine.inspect")
def test_estimate_db_config_cells(mock_inspect, mock_create_engine):
    mock_conn = MagicMock()
    mock_result = MagicMock()
    mock_result.fetchone.return_value = (50,) # 50 rows
    mock_conn.execute.return_value = mock_result
    
    mock_engine = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn
    mock_create_engine.return_value = mock_engine

    mock_inspector = MagicMock()
    mock_inspector.get_pk_constraint.return_value = {"constrained_columns": ["id"]}
    mock_inspect.return_value = mock_inspector

    from app.services import crypto_service
    db_config = DbConfig(
        name="test_estimate",
        db_type="mysql",
        connection_string=crypto_service.encrypt("sqlite:///:memory:"),
        tables_to_scan=json.dumps({"clientes": ["id", "nombre", "correo"]}),
        is_active=True
    )

    cells = db_scan_engine.estimate_db_config_cells(db_config)
    # columns to scan are nombre and correo (2 columns). 50 rows * 2 columns = 100 cells.
    assert cells == 100


@patch("app.services.db_scan_engine.create_engine")
@patch("app.services.db_scan_engine.inspect")
@patch("app.services.presidio_service.analyze_text")
def test_scan_single_db_config_filters_entities(
    mock_analyze_text,
    mock_inspect,
    mock_create_engine
):
    import threading
    db_session = SessionLocal()
    try:
        # Limpiar posibles registros colgados de corridas previas
        db_session.query(ScanFinding).filter(ScanFinding.file_path.like("db://test_conn_filter/%")).delete()
        db_session.query(FileControl).filter(FileControl.file_path.like("db://test_conn_filter/%")).delete()
        db_session.query(DbConfig).filter(DbConfig.name == "test_conn_filter").delete()
        db_session.commit()

        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            (1, "Juan Perez", "juan.perez@email.com")
        ]
        mock_conn.execute.return_value = mock_result
        
        mock_engine = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_create_engine.return_value = mock_engine

        mock_inspector = MagicMock()
        mock_inspector.get_pk_constraint.return_value = {"constrained_columns": ["id"]}
        mock_inspect.return_value = mock_inspector

        mock_analyze_text.return_value = []

        from app.services import crypto_service
        db_config = DbConfig(
            name="test_conn_filter",
            db_type="mysql",
            connection_string=crypto_service.encrypt("sqlite:///:memory:"),
            tables_to_scan=json.dumps({"clientes": ["id", "nombre", "correo"]}),
            is_active=True
        )
        db_session.add(db_config)
        db_session.commit()

        lock = threading.Lock()
        entities_filter = ["EMAIL_ADDRESS"]

        # Run scan_single_db_config with custom entities
        db_scan_engine.scan_single_db_config(db_config, None, db_session, lock, entities=entities_filter)

        # With row-batching optimization, analyze_text is called once per row
        # with all columns concatenated. Verify entities filter was passed.
        assert mock_analyze_text.called, "analyze_text should have been called"
        for call in mock_analyze_text.call_args_list:
            args, kwargs = call
            # Verify the entities filter is always passed correctly
            assert kwargs.get("entities") == entities_filter, \
                f"Expected entities={entities_filter}, got {kwargs.get('entities')}"
            # Verify the concatenated text contains both column values
            text_arg = args[0] if args else kwargs.get("text", "")
            assert "Juan Perez" in text_arg or "juan.perez@email.com" in text_arg, \
                f"Expected row data in text, got: {text_arg[:100]}"

        # Clean up
        db_session.delete(db_config)
        db_session.commit()
    finally:
        db_session.close()
