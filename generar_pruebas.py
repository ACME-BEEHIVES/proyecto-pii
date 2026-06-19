import pandas as pd
from fpdf import FPDF

# 1. Crear un Excel con PII
df = pd.DataFrame({
    'Nombre': ['Juan Perez', 'Karla Schmidt'],
    'RUT': ['12.345.678-9', '18.999.888-K'],
    'Correo': ['juan.perez@empresa.cl', 'k.schmidt@gmail.com']
})
df.to_excel("prueba_empleados.xlsx", index=False)

# 2. Crear un PDF de "Contrato"
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="CONTRATO DE PRESTACION DE SERVICIOS", ln=True, align='C')
pdf.multi_cell(0, 10, txt="Entre Don Pedro Marmol, RUT 11.222.333-4, domiciliado en Santiago...")
pdf.output("contrato_servicio.pdf")

print("Archivos de prueba generados: prueba_empleados.xlsx y contrato_servicio.pdf")
