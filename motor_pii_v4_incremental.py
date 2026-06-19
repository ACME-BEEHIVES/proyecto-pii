import os
import hashlib
import requests
import mysql.connector
import time
from concurrent.futures import ThreadPoolExecutor
from cryptography.fernet import Fernet

# --- CONFIGURACIÓN DE SEGURIDAD ---
LLAVE_MAESTRA = b'zF1o9C82M9W6qG7N2x4V_Y8u_K1p3j5H0r9B3m6Z4wA='
cipher_suite = Fernet(LLAVE_MAESTRA)

ENTIDADES_SENSIBLES = ["DATA_SALUD", "DATA_ETNIA", "DATA_POLITICA", "DATA_RELIGION", "DATA_SEXUALIDAD"]

# --- CONFIGURACIÓN DE SERVICIOS ---
TIKA_URL = "http://localhost:9998/tika"
PRESIDIO_URL = "http://localhost:5001/analyze"
PRESIDIO_HEALTH = "http://localhost:5001/health"

DB_CONFIG = {
    'user': 'root',
    'password': '', # <--- Asegúrate de poner tu clave
    'host': '127.0.0.1',
    'database': 'pii_discovery',
    'auth_plugin': 'mysql_native_password' 
}

EXTENSIONES_INTERES = ['.pdf', '.docx', '.xlsx', '.xls', '.doc', '.txt', '.jpg', '.png', '.csv']
MAX_WORKERS = 1 

def esperar_servicios():
    print("--- Verificando estado de los motores ---")
    for i in range(15):
        try:
            res = requests.get(PRESIDIO_HEALTH, timeout=5)
            if res.status_code == 200:
                print("¡Motores de upshield listos! Iniciando escaneo INCREMENTAL...\n")
                return True
        except:
            pass
        time.sleep(2)
    return False

def calcular_hash_contenido(ruta_archivo):
    hasher = hashlib.md5()
    try:
        with open(ruta_archivo, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()
    except Exception:
        return None

def procesar_archivo(ruta_archivo):
    try:
        # 1. LÓGICA INCREMENTAL AVANZADA
        hash_actual = calcular_hash_contenido(ruta_archivo)
        if not hash_actual:
            return

        hash_ruta = hashlib.md5(ruta_archivo.encode('utf-8')).hexdigest()

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("SELECT hash_archivo FROM control_archivos WHERE hash_ruta = %s", (hash_ruta,))
        registro = cursor.fetchone()

        if registro:
            hash_bd = registro[0]
            if hash_bd == hash_actual:
                cursor.close()
                conn.close()
                return # Archivo sin cambios, ignorar silenciosamente
            else:
                print(f"🔄 [MODIFICADO] Cambio detectado en: {os.path.basename(ruta_archivo)}")
                cursor.execute("DELETE FROM hallazgos WHERE archivo_nombre = %s", (ruta_archivo,))
        else:
            print(f"📄 [NUEVO] Escaneando: {os.path.basename(ruta_archivo)}")

        # 2. Extraer texto con Tika
        headers = {"Accept": "text/plain"}
        with open(ruta_archivo, 'rb') as f:
            res_tika = requests.put(TIKA_URL, data=f, headers=headers, timeout=180)
            texto = res_tika.content.decode('utf-8', errors='ignore')

        # Si el archivo no tiene texto (ej. imagen borrosa), igual guardamos su Hash para no volver a intentar
        if not texto or len(texto.strip()) < 3:
            query_control = "INSERT INTO control_archivos (hash_ruta, archivo_nombre, hash_archivo) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE hash_archivo = %s"
            cursor.execute(query_control, (hash_ruta, ruta_archivo, hash_actual, hash_actual))
            conn.commit()
            print(f"   ✅ [LIMPIO] Archivo sin texto legible.")
            cursor.close()
            conn.close()
            return

        # 3. Analizar con Presidio
        payload = {
            "text": texto,
            "language": "en", 
            "entities": ["CHILE_RUT", "EMAIL_ADDRESS", "PERSON", "DATA_SALUD", "DATA_ETNIA", "DATA_POLITICA", "DATA_RELIGION", "DATA_SEXUALIDAD"],
            "ad_hoc_recognizers": [
                {"name": "DetectorRUT", "supported_entity": "CHILE_RUT", "supported_language": "en", "patterns": [{"name": "rut", "regex": r"\b\d{1,2}\.?\d{3}\.?\d{3}-[\dkK]\b", "score": 0.95}]},
                {"name": "DetectorEmail", "supported_entity": "EMAIL_ADDRESS", "supported_language": "en", "patterns": [{"name": "email", "regex": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "score": 0.95}]},
                {"name": "DetectorSalud", "supported_entity": "DATA_SALUD", "supported_language": "en", "patterns": [{"name": "medico", "regex": r"(?i)\b(cáncer|cancer|vih|sida|diabetes|depresión|depresion|biopsia|alzheimer)\b", "score": 0.4}], "context": ["paciente", "diagnóstico", "clínica", "hospital", "doctor", "médico", "examen", "licencia", "resultados", "informe", "positivo", "arroja", "presencia", "tratamiento"]},
                {"name": "DetectorEtnia", "supported_entity": "DATA_ETNIA", "supported_language": "en", "patterns": [{"name": "pueblos", "regex": r"(?i)\b(mapuche|aymara|rapa nui|diaguita|atacameño|colla|kawésqar|yagán|indígena)\b", "score": 0.4}], "context": ["conadi", "certificado", "ascendencia", "origen", "pueblo", "etnia", "comunidad", "beca", "subsidio", "pertenece"]},
                {"name": "DetectorPolitica", "supported_entity": "DATA_POLITICA", "supported_language": "en", "patterns": [{"name": "politica", "regex": r"(?i)\b(sindicato|sindical|cut|partido comunista|udi|renovación nacional|rn|frente amplio|partido socialista|dc|democracia cristiana|republicano)\b", "score": 0.4}], "context": ["militante", "afiliado", "cuota", "descuento", "planilla", "votación", "delegado", "padrón", "inscripción", "huelga", "aportes", "partido", "política"]},
                {"name": "DetectorReligion", "supported_entity": "DATA_RELIGION", "supported_language": "en", "patterns": [{"name": "religiones", "regex": r"(?i)\b(católico|catolico|evangélico|evangelico|judío|judio|musulmán|musulman|mormón|testigo de jehová)\b", "score": 0.4}], "context": ["bautizo", "sacramento", "diezmo", "iglesia", "parroquia", "culto", "congregación", "retiro", "capellán", "religión", "creencia", "fe", "perteneciente"]},
                {"name": "DetectorSexualidad", "supported_entity": "DATA_SEXUALIDAD", "supported_language": "en", "patterns": [{"name": "sexualidad", "regex": r"(?i)\b(homosexual|heterosexual|bisexual|transgénero|transgenero|lesbiana|gay)\b", "score": 0.4}], "context": ["orientación", "identidad", "género", "pareja", "convivencia", "discriminación", "transición", "acuerdo de unión civil"]}
            ]
        }
        
        response = requests.post(PRESIDIO_URL, json=payload, timeout=60)
        res_presidio = response.json()

        # 4. Guardar Hallazgos
        hallazgos_guardados = 0
        if isinstance(res_presidio, list) and len(res_presidio) > 0:
            for h in res_presidio:
                if h['score'] >= 0.5:
                    texto_original = texto[h['start']:h['end']]
                    
                    if h['entity_type'] in ENTIDADES_SENSIBLES:
                        texto_a_guardar = cipher_suite.encrypt(texto_original.encode('utf-8')).decode('utf-8')
                        status = "🔒 CIFRADO"
                    else:
                        texto_a_guardar = texto_original
                        status = "👁️ PLANO"
                    
                    query = "INSERT INTO hallazgos (archivo_nombre, tipo_entidad, texto_detectado, puntaje_certeza) VALUES (%s, %s, %s, %s)"
                    cursor.execute(query, (ruta_archivo, h['entity_type'], texto_a_guardar, h['score']))
                    hallazgos_guardados += 1
        
        # 5. Registrar Hash de Control (¡Ahora se ejecuta SIEMPRE!)
        query_control = """
            INSERT INTO control_archivos (hash_ruta, archivo_nombre, hash_archivo) 
            VALUES (%s, %s, %s) 
            ON DUPLICATE KEY UPDATE hash_archivo = %s
        """
        cursor.execute(query_control, (hash_ruta, ruta_archivo, hash_actual, hash_actual))
        conn.commit()
        
        if hallazgos_guardados > 0:
            print(f"   🚀 Terminó con {hallazgos_guardados} registros detectados.\n")
        else:
            print(f"   ✅ [LIMPIO] Analizado sin encontrar datos confidenciales.\n")
            
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"[ERROR] {os.path.basename(ruta_archivo)}: {str(e)}\n")

def escanear_y_lanzar(ruta_raiz):
    archivos = []
    for raiz, _, files in os.walk(ruta_raiz):
        for n in files:
            ext = os.path.splitext(n)[1].lower()
            if ext in EXTENSIONES_INTERES:
                archivos.append(os.path.join(raiz, n))
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(procesar_archivo, archivos)

    print("\n--- Escaneo de upshield Finalizado ---")

if __name__ == "__main__":
    CARPETA_A_ESCANEAR = r"C:\Users\PabloOrtizCollados\Desktop\proyecto-pii\CARPETA_PRUEBA_MASIVA"
    if esperar_servicios():
        escanear_y_lanzar(CARPETA_A_ESCANEAR)