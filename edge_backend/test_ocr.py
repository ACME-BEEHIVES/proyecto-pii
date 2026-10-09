import sys
import os

# Asegurar que importamos del path correcto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ocr_service import extract_text

def test_ocr(file_path):
    print(f"==================================================")
    print(f" Iniciando prueba OCR en: {file_path}")
    print(f"==================================================")
    
    if not os.path.exists(file_path):
        print(f"[ERROR] El archivo no existe en el contenedor: {file_path}")
        print("Asegúrate de poner la ruta de la carpeta compartida, por ejemplo:")
        print("python test_ocr.py /app/CARPETA_PRUEBA_MASIVA/carnet.jpg")
        return

    try:
        texto = extract_text(file_path)
        print("\n--- RESULTADO DE LA EXTRACCIÓN (LO QUE LEE LA IA) ---\n")
        print(texto)
        print("\n-----------------------------------------------------")
    except Exception as e:
        print(f"[ERROR] Ocurrió un error al procesar la imagen: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python test_ocr.py <ruta_del_archivo>")
    else:
        test_ocr(sys.argv[1])
