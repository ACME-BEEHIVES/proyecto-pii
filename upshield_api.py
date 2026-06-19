from fastapi import FastAPI, HTTPException
import mysql.connector
from cryptography.fernet import Fernet
import uvicorn
import os

# --- INICIALIZACIÓN DE LA API ---
app = FastAPI(
    title="Upshield Edge API",
    description="Microservicio local para consultas DSAR (Derechos ARCO) y Data Mapping.",
    version="1.0.0"
)

# --- CONFIGURACIÓN DE SEGURIDAD Y BD ---
LLAVE_MAESTRA = b'zF1o9C82M9W6qG7N2x4V_Y8u_K1p3j5H0r9B3m6Z4wA='
cipher_suite = Fernet(LLAVE_MAESTRA)

ENTIDADES_SENSIBLES = ["DATA_SALUD", "DATA_ETNIA", "DATA_POLITICA", "DATA_RELIGION", "DATA_SEXUALIDAD"]

DB_CONFIG = {
    'user': 'root',
    'password': '', # <--- Tu clave de MySQL
    'host': '127.0.0.1',
    'database': 'pii_discovery',
    'auth_plugin': 'mysql_native_password' 
}

def get_db_connection():
    try:
        # dictionary=True hace que los resultados de SQL sean diccionarios fáciles de convertir a JSON
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error conectando a BD local: {str(e)}")

# --- ENDPOINT DSAR: El motor de búsqueda ---
@app.get("/api/v1/dsar/{rut}", summary="Ejecutar Mapeo DSAR por RUT")
def mapeo_dsar(rut: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 1. Buscar en qué archivos aparece este RUT exacto
        query_archivos = """
            SELECT DISTINCT archivo_nombre 
            FROM hallazgos 
            WHERE tipo_entidad = 'CHILE_RUT' AND texto_detectado = %s
        """
        cursor.execute(query_archivos, (rut,))
        archivos_encontrados = [row['archivo_nombre'] for row in cursor.fetchall()]
        
        if not archivos_encontrados:
            return {"mensaje": "Titular no encontrado", "rut": rut, "archivos_involucrados": 0, "mapa": {}}

        # 2. Extraer todo el contexto (RUTs y Datos Sensibles) de esos archivos específicos
        format_strings = ','.join(['%s'] * len(archivos_encontrados))
        query_detalle = f"""
            SELECT archivo_nombre, tipo_entidad, texto_detectado 
            FROM hallazgos 
            WHERE archivo_nombre IN ({format_strings})
        """
        cursor.execute(query_detalle, tuple(archivos_encontrados))
        resultados_crudos = cursor.fetchall()

        # 3. Ensamblar la respuesta JSON y descifrar los datos sensibles al vuelo
        mapa_datos = {}
        alertas_sensibles = 0

        for fila in resultados_crudos:
            # Limpiamos la ruta larga para mostrar solo el nombre del documento
            nombre_doc = os.path.basename(fila['archivo_nombre'])
            entidad = fila['tipo_entidad']
            texto_guardado = fila['texto_detectado']
            
            if nombre_doc not in mapa_datos:
                mapa_datos[nombre_doc] = []
                
            # Lógica de Descifrado
            if entidad in ENTIDADES_SENSIBLES:
                alertas_sensibles += 1
                try:
                    texto_legible = cipher_suite.decrypt(texto_guardado.encode('utf-8')).decode('utf-8')
                    estado = "Descifrado para reporte"
                except:
                    texto_legible = "ERROR_DE_DESCIFRADO"
                    estado = "Fallo de Llave"
            else:
                texto_legible = texto_guardado
                estado = "Texto Plano"
                
            mapa_datos[nombre_doc].append({
                "categoria_legal": entidad,
                "dato_encontrado": texto_legible,
                "estado_almacenamiento": "Cifrado en BD" if entidad in ENTIDADES_SENSIBLES else "Sin Cifrar"
            })

        return {
            "rut_consultado": rut,
            "resumen": {
                "archivos_involucrados": len(archivos_encontrados),
                "alertas_datos_sensibles": alertas_sensibles,
                "nivel_riesgo_ley21719": "ALTO" if alertas_sensibles > 0 else "MODERADO"
            },
            "mapa_de_datos": mapa_datos
        }
        
    finally:
        cursor.close()
        conn.close()

# --- ARRANQUE DEL SERVIDOR ---
if __name__ == "__main__":
    print("Iniciando API Edge de upshield en el puerto 8001...")
    # Cambiamos el puerto de 8000 a 8001 para evitar el choque
    uvicorn.run(app, host="0.0.0.0", port=8001)