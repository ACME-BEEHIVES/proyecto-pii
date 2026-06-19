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

