import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services import crypto_service, tika_service, presidio_service
from unittest.mock import patch, MagicMock

client = TestClient(app)

# 1. Tests de Crypto Service
def test_crypto_service_encryption_decryption():
    test_text = "Dato Confidencial 123"
    encrypted = crypto_service.encrypt(test_text)
    assert encrypted != test_text
    assert len(encrypted) > 0
    
    decrypted = crypto_service.decrypt(encrypted)
    assert decrypted == test_text

def test_crypto_service_sensitive_entities():
    sensitive_entities = [
        "DATA_SALUD", "DATA_ETNIA", "DATA_POLITICA", "DATA_RELIGION", "DATA_SEXUALIDAD",
        "DATA_SINDICAL", "DATA_SOCIOECONOMICO", "DATA_IDEOLOGIA", "DATA_BIOLOGICO", "DATA_BIOMETRICO"
    ]
    for entity in sensitive_entities:
        assert crypto_service.is_sensitive_entity(entity) is True
    assert crypto_service.is_sensitive_entity("CHILE_RUT") is False
    assert crypto_service.is_sensitive_entity("EMAIL_ADDRESS") is False
    assert crypto_service.is_sensitive_entity("PERSON") is False

def test_crypto_service_check_text_contains_sensitive():
    assert crypto_service.check_text_contains_sensitive("Carla Alvarez y su transexual") is True
    assert crypto_service.check_text_contains_sensitive("Tiene cáncer de colon") is True
    assert crypto_service.check_text_contains_sensitive("Perteneciente al pueblo mapuche") is True
    assert crypto_service.check_text_contains_sensitive("Es militante del partido comunista") is True
    assert crypto_service.check_text_contains_sensitive("Es católico") is True
    assert crypto_service.check_text_contains_sensitive("El adn fue extraído") is True
    assert crypto_service.check_text_contains_sensitive("Juan Pérez es una persona normal") is False
    assert crypto_service.check_text_contains_sensitive("correo@ejemplo.cl") is False


# 2. Tests de Tika Service
@patch("requests.put")
def test_tika_service_extract_text(mock_put):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"Texto extraido de prueba"
    mock_put.return_type = mock_response
    mock_put.return_value = mock_response

    # We mock opening a file to avoid actually needing one on disk during unit testing
    with patch("builtins.open", MagicMock()):
        extracted = tika_service.extract_text("dummy_path.pdf")
        assert extracted == "Texto extraido de prueba"

# 3. Tests de Presidio Service
@patch("app.services.presidio_service._session.post")
def test_presidio_service_analyze(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"start": 0, "end": 12, "entity_type": "CHILE_RUT", "score": 0.95}
    ]
    mock_post.return_value = mock_response

    findings = presidio_service.analyze_text("12.345.678-9", ["CHILE_RUT"])
    assert len(findings) == 1
    assert findings[0]["entity_type"] == "CHILE_RUT"
    assert findings[0]["score"] == 0.95

# 4. Tests de FastAPI Routers
@patch("app.services.tika_service.check_health", return_value=True)
@patch("app.services.presidio_service.check_health", return_value=True)
def test_health_check_endpoint(mock_presidio, mock_tika):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

def test_get_findings_endpoint():
    res = client.get("/api/findings")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_get_scan_status_endpoint():
    res = client.get("/api/scan/status")
    assert res.status_code == 200


def test_spanish_stemmer():
    # Test common prefixes/suffixes and plural stripping
    assert presidio_service.stem_word_es("diagnósticos") == "diagnos"
    assert presidio_service.stem_word_es("clínicas") == "clin"
    assert presidio_service.stem_word_es("afiliaciones") == "afili"
    assert presidio_service.stem_word_es("religioso") == "religi"
    assert presidio_service.stem_word_es("militantes") == "militant"


@patch("app.services.presidio_service._session.post")
def test_presidio_service_analyze_stems_context(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = []
    mock_post.return_value = mock_response

    # Analyze with custom context
    presidio_service.analyze_text("Test string", ["CHILE_RUT"], context=["diagnósticos", "clínicas"])

    # Verify _session.post payload contains both original context and stems
    assert mock_post.called
    kwargs = mock_post.call_args[1]
    payload = kwargs["json"]
    sent_context = payload["context"]
    
    assert "diagnósticos" in sent_context
    assert "diagnos" in sent_context
    assert "clínicas" in sent_context
    assert "clin" in sent_context
