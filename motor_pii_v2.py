import os
import requests
import mysql.connector

# --- CONFIGURACIÓN ---
TIKA_URL = "http://localhost:9998/tika"
PRESIDIO_URL = "http://localhost:5001/analyze"
DB_CONFIG = {
    'user': 'root',
    'password': '',
    'host': '127.0.0.1',
    'database': 'pii_discovery'
}

# Extensiones que establece la ley como críticas
EXTENSIONES_INTERES = ['.pdf', '.docx', '.xlsx', '.xls', '.doc', '.txt', '.jpg', '.png', '.csv']

def procesar_archivo(ruta_archivo):
    """Envía el archivo a Tika y Presidio, luego guarda en MySQL."""
    try:
        with open(ruta_archivo, 'rb') as f:
            res_tika = requests.put(TIKA_URL, data=f)
            texto = res_tika.text

        payload = {
            "text": texto,
            "language": "en", # Cambia a "es" cuando instalemos el modelo español
            "entities": ["PERSON", "EMAIL_ADDRESS", "CHILE_RUT"],
            "ad_hoc_recognizers": [{
                "name": "Chilean RUT",
                "patterns": [{"name": "rut", "regex": r"\b(\d{1,2}(?:\.?\d{3}){2}-[\dkK])\b", "score": 0.8}],
                "supported_entity": "CHILE_RUT", "supported_language": "en"
            }]
        }
        res_presidio = requests.post(PRESIDIO_URL, json=payload).json()

        if res_presidio:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            for h in res_presidio:
                texto_real = texto[h['start']:h['end']]
                query = "INSERT INTO hallazgos (archivo_nombre, tipo_entidad, texto_detectado, puntaje_certeza) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (ruta_archivo, h['entity_type'], texto_real, h['score']))
            conn.commit()
            cursor.close()
            conn.close()
            return len(res_presidio)
    except Exception as e:
        print(f"Error en {ruta_archivo}: {e}")
    return 0

def escanear_directorio(ruta_raiz):
    """Recorre carpetas y subcarpetas buscando archivos válidos."""
    print(f"Iniciando escaneo en: {ruta_raiz}")
    conteo_total = 0
    
    # os.walk recorre todo el árbol automáticamente
    for raiz, directorios, archivos in os.walk(ruta_raiz):
        for nombre_archivo in archivos:
            extension = os.path.splitext(nombre_archivo)[1].lower()
            
            if extension in EXTENSIONES_INTERES:
                ruta_completa = os.path.join(raiz, nombre_archivo)
                print(f"Procesando: {ruta_completa}...", end="\r")
                
                hallazgos = procesar_archivo(ruta_completa)
                conteo_total += hallazgos

    print(f"\n\nEscaneo finalizado.")
    print(f"Total de datos sensibles encontrados y guardados: {conteo_total}")

if __name__ == "__main__":
    # AQUÍ PONES LA CARPETA QUE QUIERES ESCANEAR
    # Puedes usar '.' para la carpeta actual o una ruta completa
    ruta_a_revisar = r"C:\Users\CarlosCavieres\Documents\pruebas\proyecto-pii" 
    escanear_directorio(ruta_a_revisar)