import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.finding import ScanFinding
from app.models.scan_job import ScanJob
from app.models.scan_config import ScanConfig
from app.services import crypto_service
from unittest.mock import patch, MagicMock
import os
import json

client = TestClient(app)

@pytest.fixture(autouse=True)
def preserve_db_config():
    db = SessionLocal()
    original_config = db.query(ScanConfig).filter(ScanConfig.is_active == True).first()
    
    # Si existe una configuración, guardamos sus valores originales
    backup = None
    if original_config:
        backup = {
            "scan_paths": original_config.scan_paths,
            "extensions": original_config.extensions,
            "entities": original_config.entities,
            "max_workers": original_config.max_workers,
            "is_active": original_config.is_active,
            "schedule_type": original_config.schedule_type,
            "schedule_time": original_config.schedule_time,
            "schedule_day": original_config.schedule_day
        }
    db.close()
    
    yield
    
    # Al finalizar el test, restauramos los valores originales
    db = SessionLocal()
    if backup:
        current_config = db.query(ScanConfig).filter(ScanConfig.is_active == True).first()
        if current_config:
            current_config.scan_paths = backup["scan_paths"]
            current_config.extensions = backup["extensions"]
            current_config.entities = backup["entities"]
            current_config.max_workers = backup["max_workers"]
            current_config.is_active = backup["is_active"]
            current_config.schedule_type = backup["schedule_type"]
            current_config.schedule_time = backup["schedule_time"]
            current_config.schedule_day = backup["schedule_day"]
            db.commit()
    db.close()

# 1. Tests de Config Router
def test_config_router_endpoints():
    # GET config
    res_get = client.get("/api/config")
    assert res_get.status_code == 200
    data = res_get.json()
    assert "scan_paths" in data
    assert "extensions" in data
    assert "max_workers" in data

    # PUT config con datos válidos
    payload = {
        "scan_paths": [r"C:\Users\ClienteDemo\Documentos\CARPETA_PRUEBA_MASIVA"],
        "extensions": [".txt", ".pdf"],
        "entities": ["CHILE_RUT", "EMAIL_ADDRESS"],
        "max_workers": 2,
        "is_active": True
    }
    res_put = client.put("/api/config", json=payload)
    assert res_put.status_code == 200
    assert res_put.json()["max_workers"] == 2

    # PUT config con ruta del sistema prohibida (debe fallar)
    payload_invalid = payload.copy()
    payload_invalid["scan_paths"] = ["C:\\Windows\\System32"]
    res_put_invalid = client.put("/api/config", json=payload_invalid)
    assert res_put_invalid.status_code == 400

    # Test Path
    res_test_ok = client.post("/api/config/test-path", json={"path": "."})
    assert res_test_ok.status_code == 200
    assert res_test_ok.json()["status"] == "ok"

    res_test_sys = client.post("/api/config/test-path", json={"path": "C:\\Windows"})
    assert res_test_sys.status_code == 200
    assert res_test_sys.json()["status"] == "error"

# 2. Tests de Health Router
def test_health_router_endpoints():
    res_all = client.get("/api/health")
    assert res_all.status_code == 200
    assert "services" in res_all.json()
    assert "database" in res_all.json()["services"]

    res_db = client.get("/api/health/database")
    assert res_db.status_code == 200
    assert res_db.json()["status"] == "healthy"

# 3. Tests de DSAR Router
def test_dsar_router_mapping():
    db = SessionLocal()
    rut_test = "19.999.999-9"
    try:
        # Limpiar restos de una corrida anterior que haya fallado antes de
        # llegar a su propia limpieza (evita que este test quede roto para
        # siempre por un fallo previo que dejo filas huerfanas).
        db.query(ScanFinding).filter(ScanFinding.file_path == "/app/test_dsar/doc1.pdf").delete(synchronize_session=False)
        db.commit()

        # Guardar encriptado
        enc_salud = crypto_service.encrypt("Cáncer de pulmón")

        finding1 = ScanFinding(
            file_path="/app/test_dsar/doc1.pdf",
            file_name="doc1.pdf",
            entity_type="CHILE_RUT",
            detected_text=rut_test,
            confidence_score=0.99,
            is_sensitive=False
        )
        finding2 = ScanFinding(
            file_path="/app/test_dsar/doc1.pdf",
            file_name="doc1.pdf",
            entity_type="DATA_SALUD",
            detected_text=enc_salud,
            confidence_score=0.85,
            is_sensitive=True
        )
        db.add(finding1)
        db.add(finding2)
        db.commit()

        # Consultar DSAR
        res = client.get(f"/api/dsar/{rut_test}")
        assert res.status_code == 200
        data = res.json()
        assert data["rut_consultado"] == rut_test
        assert data["resumen"]["archivos_involucrados"] == 1
        assert data["resumen"]["alertas_datos_sensibles"] == 1
        assert "doc1.pdf" in data["mapa_de_datos"]

        # Consultar DSAR con formato alternativo (sin puntos)
        res_alt = client.get("/api/dsar/19999999-9")
        assert res_alt.status_code == 200
        data_alt = res_alt.json()
        assert data_alt["resumen"]["archivos_involucrados"] == 1
        assert "doc1.pdf" in data_alt["mapa_de_datos"]

        # Verificar descifrado
        items = data["mapa_de_datos"]["doc1.pdf"]
        salud_item = next(item for item in items if item["categoria_legal"] == "DATA_SALUD")
        assert salud_item["dato_encontrado"] == "Cáncer de pulmón"
        assert salud_item["estado_almacenamiento"] == "Cifrado en BD"
    finally:
        # Limpiar siempre (ambos hallazgos, no solo el RUT), incluso si una
        # aserción fallo arriba.
        db.query(ScanFinding).filter(ScanFinding.file_path == "/app/test_dsar/doc1.pdf").delete(synchronize_session=False)
        db.commit()
        db.close()

# 4. Tests de Redaction Router
def test_redaction_router_preview_and_generate():
    db = SessionLocal()
    try:
        # Create a dummy test file
        test_file = "dummy_test_redaction.txt"
        with open(test_file, "w") as f:
            f.write("Hola, mi RUT es 19.999.999-9.")

        finding = ScanFinding(
            file_path=os.path.abspath(test_file),
            file_name=test_file,
            entity_type="CHILE_RUT",
            detected_text="19.999.999-9",
            confidence_score=0.95,
            is_sensitive=False
        )
        db.add(finding)
        db.commit()

        # Preview
        res_prev = client.post("/api/redaction/preview", json={"file_path": os.path.abspath(test_file)})
        assert res_prev.status_code == 200
        assert res_prev.json()["findings_count"] == 1
        assert "19.999.999-9" in res_prev.json()["texts_to_redact"]

        # Generate Redaction
        res_gen = client.post("/api/redaction/generate", json={"file_path": os.path.abspath(test_file)})
        assert res_gen.status_code == 200
        assert res_gen.headers["content-type"] == "application/octet-stream"

        # Check redacted file exists and is redacted
        censured_name = f"dummy_test_redaction_censurado.txt"
        censured_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "redacted_files", censured_name)
        assert os.path.exists(censured_path)
        with open(censured_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "19.999.999-9" not in content
            assert "[REDACTADO]" in content

        # Limpiar
        db.delete(finding)
        db.commit()
        if os.path.exists(test_file):
            os.remove(test_file)
        if os.path.exists(censured_path):
            os.remove(censured_path)
    finally:
        db.close()
