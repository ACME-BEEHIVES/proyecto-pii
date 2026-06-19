import os
import random
import pandas as pd
from fpdf import FPDF

# Configuración del estrés
TOTAL_ARCHIVOS = 100
CARPETAS_NIVELES = ["Finanzas", "RRHH", "Contratos", "Legal", "Clientes", "Operaciones", "Respaldos"]
NOMBRES_BASE = ["Juan", "Maria", "Pedro", "Carla", "Diego", "Francisca", "Ricardo", "Loreto"]
APELLIDOS_BASE = ["Perez", "Gonzalez", "Munoz", "Rojas", "Jimenez", "Soto", "Silva", "Sepulveda"]

def generar_rut_falso():
    numero = random.randint(5000000, 25000000)
    dv = random.choice(['0','1','2','3','4','5','6','7','8','9','K'])
    return f"{numero:,}-{dv}".replace(",", ".")

def crear_estructura_y_archivos():
    base_dir = "CARPETA_PRUEBA_MASIVA"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    print(f"Generando {TOTAL_ARCHIVOS} archivos de prueba...")

    for i in range(TOTAL_ARCHIVOS):
        # 1. Crear ruta aleatoria profunda
        sub_niveles = [random.choice(CARPETAS_NIVELES) for _ in range(random.randint(1, 4))]
        ruta_final = os.path.join(base_dir, *sub_niveles)
        os.makedirs(ruta_final, exist_ok=True)

        tipo = random.choice(["pdf", "xlsx", "txt"])
        nombre_persona = f"{random.choice(NOMBRES_BASE)} {random.choice(APELLIDOS_BASE)}"
        rut = generar_rut_falso()
        email = f"{nombre_persona.lower().replace(' ', '.')}@empresa.cl"
        
        archivo_path = os.path.join(ruta_final, f"documento_{i}.{tipo}")

        # 2. Crear contenido según tipo
        if tipo == "txt":
            with open(archivo_path, "w", encoding="utf-8") as f:
                f.write(f"Informacion confidencial de {nombre_persona}.\nRUT: {rut}\nContacto: {email}")
        
        elif tipo == "xlsx":
            df = pd.DataFrame({'Dato': ['Nombre', 'Identidad', 'Email'], 'Valor': [nombre_persona, rut, email]})
            df.to_excel(archivo_path, index=False)
        
        elif tipo == "pdf":
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"EXPEDIENTE {i}", ln=True, align='C')
            pdf.multi_cell(0, 10, txt=f"Este documento pertenece a {nombre_persona}, con identificacion RUT {rut}. Su correo es {email}.")
            pdf.output(archivo_path)

    print(f"¡Listo! Se han creado los archivos en la carpeta '{base_dir}'.")

if __name__ == "__main__":
    crear_estructura_y_archivos()
