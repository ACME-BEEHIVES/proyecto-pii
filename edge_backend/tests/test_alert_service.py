import pytest
from unittest.mock import patch, MagicMock
from app.services import alert_service
from app.config import Settings

def test_send_email_alert_disabled():
    """Verifica que no se envíen alertas si ALERT_EMAILS_ENABLED es False."""
    settings = Settings(ALERT_EMAILS_ENABLED=False)
    res = alert_service.send_email_alert("Test Subject", "Test Body", settings)
    assert res is False

@patch("smtplib.SMTP")
def test_send_email_alert_enabled_tls(mock_smtp):
    """Verifica el envío de correo usando SMTP con STARTTLS (puerto 587)."""
    settings = Settings(
        ALERT_EMAILS_ENABLED=True,
        SMTP_HOST="smtp.test.com",
        SMTP_PORT=587,
        SMTP_USERNAME="user@test.com",
        SMTP_PASSWORD="password",
        SMTP_FROM="alerts@test.com",
        SMTP_TO="admin@test.com"
    )
    
    mock_server = MagicMock()
    mock_smtp.return_value = mock_server

    res = alert_service.send_email_alert("Test Subject", "Test Body", settings)
    
    assert res is True
    mock_smtp.assert_called_once_with("smtp.test.com", 587, timeout=10)
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with("user@test.com", "password")
    mock_server.sendmail.assert_called_once()
    mock_server.quit.assert_called_once()

@patch("smtplib.SMTP_SSL")
def test_send_email_alert_enabled_ssl(mock_smtp_ssl):
    """Verifica el envío de correo usando SMTP SSL directo (puerto 465)."""
    settings = Settings(
        ALERT_EMAILS_ENABLED=True,
        SMTP_HOST="smtp.test.com",
        SMTP_PORT=465,
        SMTP_USERNAME="user@test.com",
        SMTP_PASSWORD="password",
        SMTP_FROM="alerts@test.com",
        SMTP_TO="admin@test.com"
    )
    
    mock_server = MagicMock()
    mock_smtp_ssl.return_value = mock_server

    res = alert_service.send_email_alert("Test Subject", "Test Body", settings)
    
    assert res is True
    mock_smtp_ssl.assert_called_once_with("smtp.test.com", 465, timeout=10)
    mock_server.login.assert_called_once_with("user@test.com", "password")
    mock_server.sendmail.assert_called_once()
    mock_server.quit.assert_called_once()

@patch("app.services.tika_service.check_health")
@patch("app.services.presidio_service.check_health")
@patch("app.services.alert_service.SessionLocal")
def test_check_service_health(mock_session, mock_presidio_health, mock_tika_health):
    """Prueba la lógica de chequeo individual de cada servicio."""
    # Mock Database healthy
    mock_db = MagicMock()
    mock_session.return_value = mock_db
    mock_db.execute.return_value = None
    
    db_healthy, db_msg = alert_service.check_service_health("database")
    assert db_healthy is True
    assert db_msg == ""

    # Mock Database unhealthy
    mock_db.execute.side_effect = Exception("Conexion perdida")
    db_healthy, db_msg = alert_service.check_service_health("database")
    assert db_healthy is False
    assert "Conexion perdida" in db_msg

    # Mock Tika
    mock_tika_health.return_value = True
    tika_healthy, tika_msg = alert_service.check_service_health("tika")
    assert tika_healthy is True
    
    mock_tika_health.return_value = False
    tika_healthy, tika_msg = alert_service.check_service_health("tika")
    assert tika_healthy is False
    assert "Tika" in tika_msg

    # Mock Presidio
    mock_presidio_health.return_value = True
    presidio_healthy, presidio_msg = alert_service.check_service_health("presidio")
    assert presidio_healthy is True

    mock_presidio_health.return_value = False
    presidio_healthy, presidio_msg = alert_service.check_service_health("presidio")
    assert presidio_healthy is False
    assert "Presidio" in presidio_msg

@patch("app.services.alert_service.send_email_alert")
@patch("app.services.alert_service.check_service_health")
@patch("app.services.alert_service.get_settings")
@patch("time.sleep")
def test_monitoring_loop_transitions(mock_sleep, mock_get_settings, mock_check_health, mock_send_email):
    """Verifica que el bucle de monitoreo envíe correos solo en cambios de estado (transiciones)."""
    settings = Settings(ALERT_EMAILS_ENABLED=True, ALERT_CHECK_INTERVAL=60)
    mock_get_settings.return_value = settings

    # Estado inicial en memoria: todos saludables
    alert_service.previous_states = {
        "database": True,
        "tika": True,
        "presidio": True,
        "watcher": True
    }

    # Iteración 1: Todo sigue saludable -> No se deben enviar correos
    mock_check_health.return_value = (True, "")
    
    # Hacemos que sleep lance una excepción para romper el bucle infinito tras una iteración
    mock_sleep.side_effect = [None, KeyboardInterrupt()] 

    try:
        alert_service.run_alert_monitoring_loop()
    except KeyboardInterrupt:
        pass

    assert mock_send_email.call_count == 0
    assert alert_service.previous_states["tika"] is True

    # Iteración 2: Tika se cae -> Debe enviar un correo de alerta
    # Configuramos para simular caída de tika
    def check_health_side_effect(service_name):
        if service_name == "tika":
            return False, "Tika caido"
        return True, ""
    
    mock_check_health.side_effect = check_health_side_effect
    mock_sleep.side_effect = [None, KeyboardInterrupt()]
    mock_send_email.reset_mock()

    try:
        alert_service.run_alert_monitoring_loop()
    except KeyboardInterrupt:
        pass

    # Se debió llamar 1 vez (para alertar sobre Tika)
    assert mock_send_email.call_count == 1
    # Asunto contiene alerta y TIKA
    args, kwargs = mock_send_email.call_args
    assert "ALERTA" in args[0]
    assert "TIKA" in args[0]
    assert alert_service.previous_states["tika"] is False

    # Iteración 3: Tika sigue caído -> No debe enviar ningún correo nuevo (prevención de spam)
    mock_sleep.side_effect = [None, KeyboardInterrupt()]
    mock_send_email.reset_mock()

    try:
        alert_service.run_alert_monitoring_loop()
    except KeyboardInterrupt:
        pass

    assert mock_send_email.call_count == 0
    assert alert_service.previous_states["tika"] is False

    # Iteración 4: Tika se recupera -> Debe enviar un correo de recuperación
    def check_health_recovered(service_name):
        return True, ""
    
    mock_check_health.side_effect = check_health_recovered
    mock_sleep.side_effect = [None, KeyboardInterrupt()]
    mock_send_email.reset_mock()

    try:
        alert_service.run_alert_monitoring_loop()
    except KeyboardInterrupt:
        pass

    # Se debió llamar 1 vez (para avisar la recuperación de Tika)
    assert mock_send_email.call_count == 1
    args, kwargs = mock_send_email.call_args
    assert "RECUPERACIÓN" in args[0]
    assert "TIKA" in args[0]
    assert alert_service.previous_states["tika"] is True
