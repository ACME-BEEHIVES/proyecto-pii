import requests
import mysql.connector
import json

# CONFIGURACIÓN DE LOS MOTORES (DOCKER)
TIKA_URL = "http://localhost:9998/tika"
PRESIDIO_URL = "http://localhost:5001/analyze"

# CONFIGURACIÓN DE TU MYSQL LOCAL
DB_CONFIG = {
    'user': 'root',           # <--- Cambia si tu usuario es distinto
    'password': '', # <--- Pon tu clave de MySQL
    'host': '127.0.0.1',
    'database': 'pii_discovery'
}

def procesar_archivo(ruta_archivo):
    print(f"\n--- Analizando: {ruta_archivo} ---")
    
    try:
        # 1. Extraer texto con Tika
        with open(ruta_archivo, 'rb') as f:
            res_tika = requests.put(TIKA_URL, data=f)
            texto = res_tika.text

        # 2. Analizar PII con Presidio (Incluyendo RUT Chileno)
        payload = {
            "text": texto,
            "language": "en", # <--- Cambia "es" por "en" temporalmente
            "entities": ["PERSON", "EMAIL_ADDRESS", "CHILE_RUT"],
            "ad_hoc_recognizers": [{
                "name": "Chilean RUT",
                "patterns": [{"name": "rut", "regex": r"\b(\d{1,2}(?:\.?\d{3}){2}-[\dkK])\b", "score": 0.8}],
                "supported_entity": "CHILE_RUT", "supported_language": "es"
            }]
        }
        res_presidio = requests.post(PRESIDIO_URL, json=payload).json()

        # 3. Guardar en MySQL
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        hallazgos_count = 0
        for hallazgo in res_presidio:
            start, end = hallazgo['start'], hallazgo['end']
            texto_real = texto[start:end]
            
            query = "INSERT INTO hallazgos (archivo_nombre, tipo_entidad, texto_detectado, puntaje_certeza) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (ruta_archivo, hallazgo['entity_type'], texto_real, hallazgo['score']))
            hallazgos_count += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Éxito: Se encontraron y guardaron {hallazgos_count} datos sensibles.")

    except Exception as e:
        print(f"Error procesando {ruta_archivo}: {e}")

if __name__ == "__main__":
    # Ejecutamos el análisis sobre los archivos que acabas de crear
    procesar_archivo("prueba_empleados.xlsx")
    procesar_archivo("contrato_servicio.pdf")
