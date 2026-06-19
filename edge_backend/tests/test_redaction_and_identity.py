import os
import shutil
import pytest
from app.database import SessionLocal
from app.models.finding import ScanFinding
from app.models.file_control import FileControl
from app.services import redaction_service, identity_service

@pytest.fixture
def temp_test_file():
    # Crear un archivo de texto temporal para pruebas de remediación
    file_path = "temp_test_remediation.txt"
    content = "El RUT de Juan Perez es 12.345.678-9 y su email es juan@gmail.com"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    yield file_path
    if os.path.exists(file_path):
        os.remove(file_path)
    if os.path.exists(file_path + ".quarantine.txt"):
        os.remove(file_path + ".quarantine.txt")

def test_redact_file_in_place(temp_test_file):
    db = SessionLocal()
    try:
        # Limpiar posibles registros previos
        db.query(ScanFinding).filter(ScanFinding.file_path == temp_test_file).delete()
        db.commit()

        # 1. Crear hallazgos ficticios asociados al archivo
        f1 = ScanFinding(
            file_path=temp_test_file,
            file_name=os.path.basename(temp_test_file),
            entity_type="PERSON",
            detected_text="Juan Perez",
            confidence_score=0.9,
            is_sensitive=False,
            is_resolved=False
        )
        db.add(f1)
        db.commit()
        db.refresh(f1)

        # Guardar ID localmente antes de cerrar sesión
        f1_id = f1.id

        # 2. Ejecutar censura in-situ
        res = redaction_service.redact_file_in_place(temp_test_file, db)
        assert res is True

        # Re-evaluar base de datos
        db.commit()
        db.close()
        db = SessionLocal()

        updated_f1 = db.query(ScanFinding).filter(ScanFinding.id == f1_id).first()
        assert updated_f1.is_resolved is True
        assert updated_f1.resolved_at is not None

        # Verificar que el archivo fue modificado
        with open(temp_test_file, "r", encoding="utf-8") as f:
            new_content = f.read()
        assert "Juan Perez" not in new_content
        assert "[REDACTADO]" in new_content

        # Cleanup
        db.delete(updated_f1)
        db.commit()

    finally:
        db.close()

def test_quarantine_file(temp_test_file):
    db = SessionLocal()
    try:
        # Limpiar posibles registros previos
        db.query(FileControl).filter(FileControl.hash_ruta == "temp_test_hash").delete()
        db.query(ScanFinding).filter(ScanFinding.file_path == temp_test_file).delete()
        db.query(ScanFinding).filter(ScanFinding.file_path.like("%temp_test_remediation.txt")).delete()
        db.query(FileControl).filter(FileControl.file_path.like("%temp_test_remediation.txt")).delete()
        db.commit()

        # 1. Crear control de archivo y hallazgo ficticio
        fc = FileControl(
            hash_ruta="temp_test_hash",
            file_path=temp_test_file,
            content_hash="content_hash_123"
        )
        f1 = ScanFinding(
            file_path=temp_test_file,
            file_name=os.path.basename(temp_test_file),
            entity_type="CHILE_RUT",
            detected_text="12.345.678-9",
            confidence_score=0.95,
            is_sensitive=False,
            is_resolved=False
        )
        db.add(fc)
        db.add(f1)
        db.commit()
        db.refresh(fc)
        db.refresh(f1)

        # Guardar IDs localmente antes de cerrar sesión
        f1_id = f1.id
        fc_hash = fc.hash_ruta

        # 2. Ejecutar cuarentena
        dest_path = redaction_service.quarantine_file(temp_test_file, db)
        assert os.path.exists(dest_path)
        assert os.path.exists(temp_test_file + ".quarantine.txt")
        assert not os.path.exists(temp_test_file)

        # Re-evaluar base de datos
        db.commit()
        db.close()
        db = SessionLocal()

        updated_f1 = db.query(ScanFinding).filter(ScanFinding.id == f1_id).first()
        assert updated_f1.is_resolved is True
        assert updated_f1.file_path == dest_path
        assert updated_f1.file_name == os.path.basename(dest_path)

        updated_fc = db.query(FileControl).filter(FileControl.hash_ruta == fc_hash).first()
        assert updated_fc.file_path == dest_path

        # Cleanup
        if os.path.exists(dest_path):
            os.remove(dest_path)
        db.delete(updated_f1)
        db.delete(updated_fc)
        db.commit()

    finally:
        db.close()

def test_identity_subjects_correlation(temp_test_file):
    db = SessionLocal()
    try:
        # Limpiar posibles hallazgos previos del mismo archivo y del RUT de prueba
        db.query(ScanFinding).filter(ScanFinding.file_path == temp_test_file).delete()
        db.query(ScanFinding).filter(ScanFinding.detected_text == "99.999.999-9").delete()
        db.commit()

        # Crear hallazgos de RUT, PERSON y EMAIL en el mismo archivo para verificar la correlación
        rut_find = ScanFinding(
            file_path=temp_test_file,
            file_name=os.path.basename(temp_test_file),
            entity_type="CHILE_RUT",
            detected_text="99.999.999-9",
            confidence_score=0.9,
            is_sensitive=False,
            is_resolved=False
        )
        person_find = ScanFinding(
            file_path=temp_test_file,
            file_name=os.path.basename(temp_test_file),
            entity_type="PERSON",
            detected_text="Juan Perez",
            confidence_score=0.9,
            is_sensitive=False,
            is_resolved=False
        )
        email_find = ScanFinding(
            file_path=temp_test_file,
            file_name=os.path.basename(temp_test_file),
            entity_type="EMAIL_ADDRESS",
            detected_text="juan@gmail.com",
            confidence_score=0.9,
            is_sensitive=False,
            is_resolved=False
        )
        db.add(rut_find)
        db.add(person_find)
        db.add(email_find)
        db.commit()

        # Ejecutar correlación
        subjects = identity_service.get_identity_subjects(db)
        assert len(subjects) > 0
        
        # Buscar el RUT formateado
        target_sub = next((s for s in subjects if s["rut"] == "99.999.999-9"), None)
        assert target_sub is not None
        assert "Juan Perez" in target_sub["names"]
        assert "juan@gmail.com" in target_sub["emails"]
        assert os.path.basename(temp_test_file) in target_sub["files"]
        assert target_sub["findings_count"] == 3

        # Cleanup
        db.delete(rut_find)
        db.delete(person_find)
        db.delete(email_find)
        db.commit()

    finally:
        db.close()
