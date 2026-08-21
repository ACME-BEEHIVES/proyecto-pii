import os
import random

# --- RUTA DE TU CARPETA ---
CARPETA_DESTINO = r"C:\Users\CarlosCavieres\Documents\pruebas\proyecto-pii\CARPETA_PRUEBA_MASIVA"

# Listas de datos para combinar
NOMBRES = ["Juan", "Maria", "Diego", "Carla", "Pedro", "Francisca", "Ricardo", "Loreto", "Camila", "Javier"]
APELLIDOS = ["Perez", "Gonzalez", "Soto", "Silva", "Rojas", "Jimenez", "Sepulveda", "Munoz", "Tapia", "Contreras"]
EMPRESAS = ["empresa.cl", "corporacion.com", "negocios.cl", "salud.cl", "gob.cl"]

# Diccionarios por categoría para generar documentos reales
CAT_SALUD = {"claves": ["cáncer", "vih", "diabetes", "biopsia", "depresión"], "contextos": ["paciente", "diagnóstico", "licencia", "resultados"]}
CAT_ETNIA = {"claves": ["mapuche", "aymara", "rapa nui", "indígena"], "contextos": ["conadi", "certificado", "comunidad", "ascendencia"]}
CAT_POLITICA = {"claves": ["sindicato", "frente amplio", "partido comunista", "udi", "cut"], "contextos": ["militante", "cuota", "descuento", "planilla"]}
CAT_RELIGION = {"claves": ["católico", "evangélico", "judío", "mormón"], "contextos": ["bautizo", "diezmo", "sacramento", "iglesia"]}
CAT_SEXUALIDAD = {"claves": ["homosexual", "transgénero", "bisexual"], "contextos": ["identidad", "género", "convivencia", "transición"]}

# Falsos Positivos para engañar a la IA (Palabra clave SIN contexto sensible)
FALSOS_POSITIVOS = [
    "El signo cáncer es de agua y rige la astrología de este mes.",
    "El frente amplio de masas de aire frío traerá lluvias a la capital.",
    "La arquitectura de estilo mormón en el siglo XIX.",
    "El sindicato de actores de Hollywood entró en huelga ayer.",
    "La película trata sobre un detective mapuche en la época colonial."
]

def generar_rut_falso():
    numero = random.randint(5000000, 25000000)
    dv = random.choice("0123456789K")
    return f"{numero:,}".replace(",", ".") + f"-{dv}"

def crear_archivos_masivos():
    if not os.path.exists(CARPETA_DESTINO):
        os.makedirs(CARPETA_DESTINO)

    print(f"Generando 100 documentos de prueba de la Ley 21.719 en: {CARPETA_DESTINO}...\n")

    for i in range(1, 101):
        # Distribución de probabilidad de los documentos
        tipo_doc = random.choices(
            ["limpio", "pii_basico", "salud", "etnia", "politica", "religion", "sexualidad", "falso_positivo"],
            weights=[20, 20, 10, 10, 10, 10, 10, 10], k=1
        )[0]
        
        nombre = random.choice(NOMBRES)
        apellido = random.choice(APELLIDOS)
        rut = generar_rut_falso()
        email = f"{nombre.lower()}.{apellido.lower()}@{random.choice(EMPRESAS)}"
        
        nombre_archivo = f"doc_prueba_{i:03d}_{tipo_doc}.txt"
        ruta_completa = os.path.join(CARPETA_DESTINO, nombre_archivo)
        contenido = ""

        if tipo_doc == "limpio":
            contenido = "Estimados, adjunto la minuta de la reunión semanal. Favor revisar los presupuestos para la campaña de marketing del Q3."
        
        elif tipo_doc == "pii_basico":
            contenido = f"CONTRATO DE SERVICIOS\nEl trabajador {nombre} {apellido}, RUT {rut}, acepta las condiciones. Correo: {email}."

        elif tipo_doc == "salud":
            c, ctx = random.choice(CAT_SALUD["claves"]), random.choice(CAT_SALUD["contextos"])
            contenido = f"INFORME MÉDICO: El {ctx} de {nombre} {apellido} (RUT: {rut}) arroja positivo para {c}."

        elif tipo_doc == "etnia":
            c, ctx = random.choice(CAT_ETNIA["claves"]), random.choice(CAT_ETNIA["contextos"])
            contenido = f"FORMULARIO: Se adjunta el {ctx} que acredita que el señor {nombre} {apellido} pertenece al pueblo {c}."

        elif tipo_doc == "politica":
            c, ctx = random.choice(CAT_POLITICA["claves"]), random.choice(CAT_POLITICA["contextos"])
            contenido = f"RRHH: Autorizo el {ctx} mensual de mi salario para aportes al {c}. Mi RUT es {rut}."

        elif tipo_doc == "religion":
            c, ctx = random.choice(CAT_RELIGION["claves"]), random.choice(CAT_RELIGION["contextos"])
            contenido = f"REGISTRO PARROQUIAL: Se emite certificado de {ctx} de la persona {nombre} {apellido}, religión {c}."

        elif tipo_doc == "sexualidad":
            c, ctx = random.choice(CAT_SEXUALIDAD["claves"]), random.choice(CAT_SEXUALIDAD["contextos"])
            contenido = f"ATENCIÓN PSICOLÓGICA: Proceso de {ctx} para paciente {c}, RUT {rut}."

        elif tipo_doc == "falso_positivo":
            contenido = random.choice(FALSOS_POSITIVOS)

        # Guardar el archivo
        with open(ruta_completa, "w", encoding="utf-8") as f:
            f.write(contenido)

    print("¡Listo! 100 documentos creados con éxito.")
    print("Revisa tu terminal al correr upshield para ver cómo clasifica cada categoría.")

if __name__ == "__main__":
    crear_archivos_masivos()