import time
import threading
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.header import Header
from sqlalchemy import text

from app.database import SessionLocal
from app.config import get_settings
from app.services import tika_service, presidio_service

# Estado en memoria para transición de alertas (evita spam).
# Se inicializa en True para que si un servicio está caído al iniciar, se envíe la alerta (cambio de True a False).
previous_states = {
    "database": True,
    "tika": True,
    "presidio": True,
    "watcher": True
}

def send_email_alert(subject: str, body: str, settings) -> bool:
    """Envía un correo de alerta utilizando la configuración SMTP especificada."""
    if not settings.ALERT_EMAILS_ENABLED:
        return False

    if not settings.SMTP_HOST or not settings.SMTP_TO:
        print("[AlertService] Configuración SMTP incompleta (SMTP_HOST o SMTP_TO vacíos). Alerta no enviada.")
        return False

    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = Header(subject, "utf-8")
        msg["From"] = settings.SMTP_FROM or settings.SMTP_USERNAME
        msg["To"] = settings.SMTP_TO

        # Determinar si usar conexión SSL directa o STARTTLS
        use_ssl = settings.SMTP_PORT == 465
        if use_ssl:
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)
            if settings.SMTP_PORT == 587:
                server.starttls()

        if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)

        server.sendmail(msg["From"], [settings.SMTP_TO], msg.as_string())
        server.quit()
        print(f"[AlertService] Correo enviado con éxito: '{subject}' a {settings.SMTP_TO}")
        return True
    except Exception as e:
        print(f"[AlertService] Error al enviar correo de alerta por SMTP: {str(e)}")
        return False

def check_service_health(service_name: str) -> tuple[bool, str]:
    """Verifica el estado de un servicio específico. Retorna (es_saludable, mensaje_de_error)."""
    settings = get_settings()

    if service_name == "database":
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            return True, ""
        except Exception as e:
            return False, f"Error de conexión MySQL: {str(e)}"
        finally:
            db.close()

    elif service_name == "tika":
        tika_ok = tika_service.check_health()
        return tika_ok, "Apache Tika no responde en el puerto 9998" if not tika_ok else ""

    elif service_name == "presidio":
        presidio_ok = presidio_service.check_health()
        return presidio_ok, "Microsoft Presidio no responde en el puerto 5001" if not presidio_ok else ""

    elif service_name == "watcher":
        try:
            from app.services.realtime_watcher import watcher
            if watcher and watcher.active:
                # Si hay rutas configuradas, el observer de watchdog debería estar vivo
                if len(watcher.current_paths) > 0:
                    if watcher.observer and watcher.observer.is_alive():
                        return True, ""
                    else:
                        return False, "El observador de archivos en tiempo real está inactivo"
                return True, ""
            return False, "El servicio de monitoreo en tiempo real está inactivo"
        except Exception as e:
            return False, f"Error al verificar watcher: {str(e)}"

    return False, f"Servicio desconocido: {service_name}"

def run_alert_monitoring_loop():
    """Bucle principal de monitoreo de servicios con detección de transiciones."""
    print("[AlertService] Iniciando bucle de monitoreo de alertas...")
    
    # Espera inicial para permitir la inicialización de los servicios de docker al arrancar
    time.sleep(10)

    while True:
        try:
            settings = get_settings()
            if not settings.ALERT_EMAILS_ENABLED:
                time.sleep(10)
                continue

            for service_name in ["database", "tika", "presidio", "watcher"]:
                is_healthy, error_msg = check_service_health(service_name)
                prev_healthy = previous_states.get(service_name, True)

                # Transición: De Saludable a Caído
                if prev_healthy and not is_healthy:
                    previous_states[service_name] = False
                    subject = f"[UpShield Edge Agent] ALERTA: El servicio {service_name.upper()} se ha detenido"
                    body = (
                        f"Hola Administrador,\n\n"
                        f"Te notificamos que el servicio '{service_name}' del UpShield Edge Agent ha dejado de responder.\n\n"
                        f"Detalles del fallo:\n"
                        f"- Servicio: {service_name}\n"
                        f"- Estado actual: INACTIVO / CAÍDO\n"
                        f"- Mensaje: {error_msg}\n"
                        f"- Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"- Entorno: {settings.ENVIRONMENT}\n\n"
                        f"Por favor, revisa el estado del contenedor de docker o del servicio correspondiente.\n"
                    )
                    send_email_alert(subject, body, settings)

                # Transición: De Caído a Recuperado
                elif not prev_healthy and is_healthy:
                    previous_states[service_name] = True
                    subject = f"[UpShield Edge Agent] RECUPERACIÓN: El servicio {service_name.upper()} vuelve a estar operativo"
                    body = (
                        f"Hola Administrador,\n\n"
                        f"Te notificamos que el servicio '{service_name}' del UpShield Edge Agent se ha recuperado y vuelve a estar operativo.\n\n"
                        f"Detalles de la recuperación:\n"
                        f"- Servicio: {service_name}\n"
                        f"- Estado actual: ACTIVO / SALUDABLE\n"
                        f"- Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"- Entorno: {settings.ENVIRONMENT}\n\n"
                        f"El servicio vuelve a procesar peticiones con normalidad.\n"
                    )
                    send_email_alert(subject, body, settings)

        except Exception as e:
            print(f"[AlertService] Error en ciclo de monitoreo: {str(e)}")

        # Esperar el intervalo configurado
        settings = get_settings()
        time.sleep(max(5, settings.ALERT_CHECK_INTERVAL))

def start_alert_monitoring():
    """Arranca el hilo de monitoreo en segundo plano."""
    thread = threading.Thread(target=run_alert_monitoring_loop, name="AlertMonitoringThread", daemon=True)
    thread.start()
    print("[AlertService] Hilo demonio de monitoreo de alertas iniciado exitosamente.")
