import os
import random

# --- RUTA DE TU CARPETA ---
CARPETA_DESTINO = r"C:\Users\PabloOrtizCollados\Desktop\proyecto-pii\CARPETA_PRUEBA_MASIVA"

# Listas de datos falsos para combinar
NOMBRES = ["Juan", "Maria", "Diego", "Carla", "Pedro", "Francisca", "Ricardo", "Loreto"]
APELLIDOS = ["Perez", "Gonzalez", "Soto", "Silva", "Rojas", "Jimenez", "Sepulveda", "Munoz"]
ENFERMEDADES = ["cáncer", "diabetes", "vih", "depresión", "biopsia", "esquizofrenia"]
CONTEXTOS_MEDICOS = ["paciente", "diagnóstico", "tratamiento", "clínica", "licencia", "resultados"]
EMPRESAS = ["empresa.cl", "corporacion.com", "negocios.cl", "salud.cl"]

def generar_rut_falso():
    numero = random.randint(5000000, 25000000)
    dv = random.choice("0123456789K")
    # Formatear con puntos (ej. 12.345.678-9)
    return f"{numero:,}".replace(",", ".") + f"-{dv}"

def generar_email(nombre, apellido):
    dominio = random.choice(EMPRESAS)
    return f"{nombre.lower()}.{apellido.lower()}@{dominio}"

def crear_archivos():
    # Asegurarnos de que la carpeta existe
    if not os.path.exists(CARPETA_DESTINO):
        os.makedirs(CARPETA_DESTINO)

    print(f"Generando documentos en: {CARPETA_DESTINO}...")

    for i in range(1, 51):
        tipo_doc = random.choice(["limpio", "pii_basico", "salud_real", "salud_falso_positivo"])
        nombre = random.choice(NOMBRES)
        apellido = random.choice(APELLIDOS)
        
        nombre_archivo = f"doc_prueba_{i:03d}_{tipo_doc}.txt"
        ruta_completa = os.path.join(CARPETA_DESTINO, nombre_archivo)

        contenido = ""

        # 1. Documentos Limpios (Sin datos personales)
        if tipo_doc == "limpio":
            contenido = "Minuta de la reunión semanal. Se discutieron los objetivos trimestrales y la estrategia de marketing para el próximo año. Por favor revisar el presupuesto adjunto antes del viernes."
        
        # 2. Documentos con RUT y Email (Nivel Básico)
        elif tipo_doc == "pii_basico":
            rut = generar_rut_falso()
            email = generar_email(nombre, apellido)
            contenido = f"Contrato de prestación de servicios.\nEl contratista {nombre} {apellido}, cédula de identidad {rut}, se compromete a entregar los informes mensuales. Para notificaciones, escribir a {email}."

        # 3. Datos Sensibles REALES (Enfermedad + Contexto) -> Debería disparar la alerta
        elif tipo_doc == "salud_real":
            enfermedad = random.choice(ENFERMEDADES)
            contexto = random.choice(CONTEXTOS_MEDICOS)
            rut = generar_rut_falso()
            contenido = f"INFORME MÉDICO CONFIDENCIAL\nSe confirma que el {contexto} de {nombre} {apellido} (RUT: {rut}) indica presencia de {enfermedad}. Se recomienda iniciar procedimiento a la brevedad."

        # 4. Falso Positivo de Salud (Enfermedad sin contexto) -> Debería ser ignorado por el "score" bajo
        elif tipo_doc == "salud_falso_positivo":
            contenido = f"Revista Astral: Las personas del signo cáncer tendrán un mes excelente en lo laboral. Evite el exceso de azúcar para prevenir la diabetes. Además, la película sobre la depresión ganó un Oscar."

        # Guardar el archivo
        with open(ruta_completa, "w", encoding="utf-8") as f:
            f.write(contenido)

    # Crear un archivo CSV para que Tika también lea tablas
    ruta_csv = os.path.join(CARPETA_DESTINO, "base_datos_clientes.csv")
    with open(ruta_csv, "w", encoding="utf-8") as f:
        f.write("ID,Nombre,RUT,Email\n")
        for _ in range(5):
            n, a = random.choice(NOMBRES), random.choice(APELLIDOS)
            f.write(f"{random.randint(100,999)},{n} {a},{generar_rut_falso()},{generar_email(n, a)}\n")

    print("\n¡Listo! Se han generado 50 archivos .txt y 1 archivo .csv en la carpeta.")
    print("Tipos de documentos creados:")
    print("- Limpios (Sin PII)")
    print("- PII Básico (RUT y Correos)")
    print("- Salud Sensible (Contexto Médico Real)")
    print("- Falsos Positivos de Salud (Sin contexto médico)")

if __name__ == "__main__":
    crear_archivos()