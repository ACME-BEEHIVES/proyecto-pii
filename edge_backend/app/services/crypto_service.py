from cryptography.fernet import Fernet
from app.config import get_settings

settings = get_settings()

# Initialize the cipher suite. PII_ENCRYPTION_KEY should be passed as a bytes string or converted.
# We ensure the key is correctly encoded as bytes.
key = settings.PII_ENCRYPTION_KEY.encode('utf-8') if isinstance(settings.PII_ENCRYPTION_KEY, str) else settings.PII_ENCRYPTION_KEY
cipher_suite = Fernet(key)

ENTIDADES_SENSIBLES = {
    "DATA_SALUD", "DATA_ETNIA", "DATA_POLITICA", "DATA_RELIGION", "DATA_SEXUALIDAD",
    "DATA_SINDICAL", "DATA_SOCIOECONOMICO", "DATA_IDEOLOGIA", "DATA_BIOLOGICO", "DATA_BIOMETRICO",
    "DATA_PENAL"
}

def encrypt(text: str) -> str:
    """Cifra un texto plano utilizando Fernet AES-256."""
    if not text:
        return ""
    return cipher_suite.encrypt(text.encode('utf-8')).decode('utf-8')

def decrypt(ciphertext: str) -> str:
    """Descifra un texto cifrado utilizando Fernet AES-256."""
    if not ciphertext:
        return ""
    try:
        return cipher_suite.decrypt(ciphertext.encode('utf-8')).decode('utf-8')
    except Exception:
        # En caso de error de descifrado, devolvemos un texto de error o el original enmascarado
        return "[ERROR AL DESCIFRAR]"

def is_sensitive_entity(entity_type: str) -> bool:
    """Verifica si un tipo de entidad se considera sensible bajo la regulación."""
    return entity_type in ENTIDADES_SENSIBLES

def check_text_contains_sensitive(text: str, entity_type: str = None) -> bool:
    """Verifica si un texto contiene términos correspondientes a alguna categoría sensible.
    
    Si entity_type corresponde a una entidad básica (CHILE_RUT, EMAIL_ADDRESS, PERSON,
    PHONE_NUMBER, DATE_TIME), se omite el check secundario para evitar falsos positivos
    (ej: el regex de montos socioeconómicos coincide con el formato numérico de los RUT).
    """
    if not text:
        return False
    # Las entidades básicas ya fueron clasificadas correctamente por Presidio.
    # Sus patrones numéricos/textuales generan falsos positivos contra los regex sensibles.
    BASIC_ENTITIES = {"CHILE_RUT", "EMAIL_ADDRESS", "PERSON", "PHONE_NUMBER", "DATE_TIME", "DOMICILIO", "NACIONALIDAD", "PASAPORTE", "LICENCIA_CONDUCIR", "CUENTA_BANCARIA", "NUMERO_SERIE_DOC"}
    if entity_type and entity_type in BASIC_ENTITIES:
        return False
    import re
    from app.services.presidio_service import AD_HOC_RECOGNIZERS
    for rec in AD_HOC_RECOGNIZERS:
        if rec["supported_entity"] in ["CHILE_RUT", "EMAIL_ADDRESS"]:
            continue
        for pattern in rec.get("patterns", []):
            regex_str = pattern.get("regex")
            if regex_str:
                if re.search(regex_str, text, re.IGNORECASE):
                    return True
    return False


# ---------------------------------------------------------------------------
# Enmascaramiento de datos personales (Ley 21.719 — minimización de datos)
# ---------------------------------------------------------------------------
import hmac
import hashlib
import re as _re

def _normalize_for_hash(text: str, entity_type: str) -> str:
    """Normaliza el texto antes de calcular el hash de búsqueda.
    Cada tipo de entidad tiene su propia normalización para garantizar que
    búsquedas con formatos ligeramente distintos (ej. RUT con/sin puntos)
    generen el mismo hash.
    """
    if not text:
        return ""
    t = text.strip()
    if entity_type == "CHILE_RUT":
        # Solo dígitos + K, mayúscula
        return _re.sub(r'[^0-9kK]', '', t).upper()
    if entity_type == "EMAIL_ADDRESS":
        return t.lower()
    if entity_type == "PERSON":
        # Minúsculas, colapsar espacios
        return " ".join(t.lower().split())
    if entity_type == "PHONE_NUMBER":
        return _re.sub(r'[^0-9+]', '', t)
    # Genérico
    return " ".join(t.lower().split())


def compute_search_hash(text: str, entity_type: str) -> str:
    """Calcula un HMAC-SHA256 del valor normalizado usando la llave de cifrado
    como secreto. Permite buscar titulares por coincidencia exacta sin
    almacenar el dato personal real (pseudonimización).
    """
    normalized = _normalize_for_hash(text, entity_type)
    if not normalized:
        return ""
    return hmac.new(key, normalized.encode('utf-8'), hashlib.sha256).hexdigest()


def mask_text(text: str, entity_type: str) -> str:
    """Genera una versión enmascarada del dato personal que permite al operador
    *identificar* el hallazgo sin exponer el dato completo.

    Ejemplos:
      RUT  19.456.789-0  →  19.XXX.XXX-0
      Email juan@g.com   →  j***@g.com
      Nombre Juan Pérez  →  Juan P.
      Teléfono +56987654 →  +56 9 XXXX 4321
    """
    if not text:
        return ""
    t = text.strip()

    if entity_type == "CHILE_RUT":
        digits = _re.sub(r'[^0-9kK]', '', t).upper()
        if len(digits) >= 8:
            # Mostrar primeros 2 dígitos + DV, ocultar el resto
            return f"{digits[:2]}.XXX.XXX-{digits[-1]}"
        if len(digits) >= 2:
            return f"{digits[0]}{'X' * (len(digits) - 2)}-{digits[-1]}"
        return "X" * len(t)

    if entity_type == "EMAIL_ADDRESS":
        if "@" in t:
            local, domain = t.rsplit("@", 1)
            masked_local = local[0] + "***" if local else "***"
            return f"{masked_local}@{domain}"
        return t[0] + "***"

    if entity_type == "PERSON":
        parts = t.split()
        if len(parts) >= 2:
            # Primer nombre completo + iniciales del resto
            return parts[0] + " " + " ".join(p[0] + "." for p in parts[1:] if p)
        return t

    if entity_type == "PHONE_NUMBER":
        digits_only = _re.sub(r'[^0-9+]', '', t)
        if len(digits_only) >= 8:
            # Mostrar últimos 4 dígitos
            return digits_only[:len(digits_only) - 4] + " XXXX" if len(digits_only) <= 5 else digits_only[:len(digits_only) - 4] + "XXXX"
        return "X" * len(t)

    if entity_type == "DATE_TIME":
        # Las fechas no son sensibles per se, mostrar tal cual
        return t

    if entity_type in ("DOMICILIO", "NACIONALIDAD"):
        # Mostrar primeras palabras, ocultar el resto
        parts = t.split()
        if len(parts) > 3:
            return " ".join(parts[:2]) + " [...]"
        return t

    # Entidades sensibles: no deberían llegar aquí (se cifran), pero por si acaso
    if entity_type in ENTIDADES_SENSIBLES:
        return "[DATO SENSIBLE PROTEGIDO]"

    # Genérico: mostrar primeros 3 chars
    if len(t) > 6:
        return t[:3] + "***"
    return t
