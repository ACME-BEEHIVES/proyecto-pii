import os
import requests
import mysql.connector
from concurrent.futures import ThreadPoolExecutor

# --- CONFIGURACIÓN ---
TIKA_URL = "http://localhost:9998/tika"
PRESIDIO_URL = "http://localhost:5001/analyze"
DB_CONFIG = {
    'user': 'root',
    'password': '',
    'host': '127.0.0.1',
    'database': 'pii_discovery'
}

EXTENSIONES_INTERES = ['.pdf', '.docx', '.xlsx', '.xls', '.doc', '.txt', '.jpg', '.png', '.csv']
# Ajusta este número según tu CPU y RAM (10 es un buen punto de partida)
MAX_WORKERS = 10 

def procesar_archivo(ruta_archivo):
    """Función atómica para procesar un solo archivo."""
    try:
        with open(ruta_archivo, 'rb') as f:
            res_tika = requests.put(TIKA_URL, data=f)
            texto = res_tika.text

        payload = {
            "text": texto,
            "language": "en",
            "entities": ["PERSON", "EMAIL_ADDRESS", "CHILE_RUT"],
            "ad_hoc_recognizers": [{
                "name": "Chilean RUT",
                "patterns": [{"name": "rut", "regex": r"\b(\d{1,2}(?:\.?\d{3}){2}-[\dkK])\b", "score": 0.8}],
                "supported_entity": "CHILE_RUT", "supported_language": "en"
            }]
        }
        res_presidio = requests.post(PRESIDIO_URL, json=payload).json()

        if res_presidio:
            # Creamos una conexión por hilo para evitar colisiones
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            for h in res_presidio:
                texto_real = texto[h['start']:h['end']]
                query = "INSERT INTO hallazgos (archivo_nombre, tipo_entidad, texto_detectado, puntaje_certeza) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (ruta_archivo, h['entity_type'], texto_real, h['score']))
            conn.commit()
            cursor.close()
            conn.close()
            print(f"[OK] {ruta_archivo}: {len(res_presidio)} hallazgos.")
    except Exception as e:
        print(f"[ERROR] {ruta_archivo}: {e}")

def escanear_y_lanzar(ruta_raiz):
    """Busca archivos y los reparte entre los trabajadores en paralelo."""
    archivos_a_procesar = []
    
    print(f"Buscando archivos en: {ruta_raiz}...")
    for raiz, _, archivos in os.walk(ruta_raiz):
        for nombre in archivos:
            if os.path.splitext(nombre)[1].lower() in EXTENSIONES_INTERES:
                archivos_a_procesar.append(os.path.join(raiz, nombre))

    print(f"Total de archivos detectados: {len(archivos_a_procesar)}")
    print(f"Iniciando procesamiento paralelo con {MAX_WORKERS} hilos...\n")

    # Aquí ocurre la magia del paralelismo
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(procesar_archivo, archivos_a_procesar)

if __name__ == "__main__":
    ruta_a_revisar = r"C:\Users\CarlosCavieres\Documents\pruebas\proyecto-pii"
    escanear_y_lanzar(ruta_a_revisar)