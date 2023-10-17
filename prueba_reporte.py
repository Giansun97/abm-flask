import pandas as pd
import random
import numpy as np
from datetime import datetime, timedelta
from fpdf import FPDF
import datetime
import matplotlib.pyplot as plt
import os
import tempfile
import plotly.graph_objs as go
import plotly.io as pio


# configuracion
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', 800)


def generar_datos_random():
    # Definir las fechas de inicio y fin
    fecha_inicio = datetime(2022, 8, 1)
    fecha_fin = datetime(2023, 8, 31)

    # Crear un rango de fechas mensuales desde agosto de 2022 hasta hoy
    fechas = [fecha_inicio + timedelta(days=30 * i) for i in range(13) if
              fecha_inicio + timedelta(days=30 * i) <= fecha_fin]

    # Crear una lista de diccionarios para almacenar los datos
    data = []

    # Llenar la lista con datos aleatorios
    for fecha in fechas[:-1]:
        ventas = round(random.uniform(117896, 916000), 2)
        compras = round(ventas * random.uniform(0.1, 0.9), 2)
        data.append({"cuit": 27000000006, "contribuyente": "prueba 1", "periodo": fecha.strftime("%b-%y"),
                     "actividad": "servicios", "ventas": ventas, "compras": compras})

    # Crear un DataFrame a partir de la lista de diccionarios
    df = pd.DataFrame(data)

    df.to_excel('datos_random.xlsx', index=False)

    return df


#  ----- Funcion generar datos random. -----
# df = generar_datos_random()

df = pd.read_excel('datos_random.xlsx')

df['diferencia'] = df['ventas'] - df['compras']

print(df)

# Clase para el informe PDF
class PDF(FPDF):
    def __init__(self):
        super().__init__()

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', '', 12)
        self.cell(0, 8, f'Página {self.page_no()}', 0, 0, 'C')


# Crear un objeto PDF
pdf = PDF()
pdf.add_page()

# ----- PAGINA 1 -----
total_ventas = round(df['ventas'].sum(), 2)
total_compras = round(df['compras'].sum(), 2)
ratio_compras_vs_ventas = round(total_compras / total_ventas * 100, 2)
ratio_compras_vs_ventas_servicios = 40

# Título del informe
pdf.set_font('Arial', 'B', 16)
pdf.cell(w=0, h=20, txt="Reporte control de Monotributistas (individual)", ln=1)

Hoy = datetime.datetime.now().strftime("%d/%m/%Y")

# Información del cliente
pdf.set_font('Arial', 'B', 12)
pdf.cell(0, 10, 'Información del Cliente', ln=1)
pdf.set_font('Arial', '', 12)
pdf.cell(60, 10, 'Nombre del Cliente:', 0, 0)
pdf.cell(0, 10, f'{df["contribuyente"].iloc[0]}', ln=1)
pdf.cell(60, 10, 'Cuit del Cliente:', 0, 0)
pdf.cell(0, 10, f'{df["cuit"].iloc[0]}', ln=1)
pdf.cell(60, 10, 'Actividad:', 0, 0)
pdf.cell(0, 10, f'{df["actividad"].iloc[0]}', ln=1)

# Separador
pdf.ln(5)
pdf.line(10, pdf.get_y(), 200, pdf.get_y())
pdf.ln(5)

# Títulos y totales
pdf.ln(5)
pdf.set_font('Arial', 'B', 14)
pdf.cell(0, 10, 'Totales del Periodo Analizado', ln=1)

# Estilo para los totales
pdf.set_font('Arial', '', 12)
pdf.set_fill_color(200, 200, 200)
pdf.cell(80, 10, f'Total de ventas del periodo analizado:', border=1, ln=0, align='L', fill=True)
pdf.cell(80, 10, f'{total_ventas}', border=1, ln=1, align='C', fill=True)
pdf.cell(80, 10, f'Total de compras del periodo analizado:', border=1, ln=0, align='L', fill=True)
pdf.cell(80, 10, f'{total_compras}', border=1, ln=1, align='C', fill=True)

# Separador
pdf.ln(10)

# ---- SI EL CONTRIBUYENTE POSEE ACTIVIDAD DE SERVICIO ----
actividad_servicios = (df['actividad'] == 'servicios').all()

if actividad_servicios and ratio_compras_vs_ventas > 40:
    pdf.set_fill_color(255, 0, 0)  # Establecer color de fondo en rojo
    pdf.set_text_color(255, 255, 255)  # Establecer color de texto en blanco
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Alerta: Fuera de los parámetros de AFIP', ln=1, fill=True)

    pdf.set_font('Arial', '', 12)
    pdf.set_fill_color(255, 255, 255)  # Restablecer color de fondo
    pdf.set_text_color(0, 0, 0)  # Restablecer color de texto
    pdf.cell(0, 10, 'El ratio de ventas vs compras supera el límite establecido por AFIP:', ln=1)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(100, 10, f'Ratio de tolerancia AFIP: {ratio_compras_vs_ventas_servicios}%', ln=1)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(100, 10, f'Ratio del periodo: {ratio_compras_vs_ventas}%', ln=1)

# Separador
pdf.ln(5)
pdf.line(10, pdf.get_y(), 200, pdf.get_y())
pdf.ln(5)

# Crear un gráfico de barras para ventas y compras por período
plt.figure(figsize=(12, 6))  # Tamaño del gráfico

# Ancho de las barras y separación entre barras
bar_positions = np.arange(len(df['periodo']))

color_ventas = '#1f77b4'  # Azul oscuro3
color_compras = '#ff7f0e'  # Naranja oscuro

bar_width = 0.25

# Crear barras para ventas y compras
plt.bar(bar_positions, df['ventas'], width=bar_width, label='Ventas', color='green', alpha=0.7)
plt.bar(bar_positions - bar_width, df['compras'], width=bar_width, label='Compras', color='red', alpha=0.7)
plt.bar(bar_positions + bar_width, df['diferencia'], width=bar_width, label='Diferencia', color='gray', alpha=0.7)

# Etiquetas y título
plt.xlabel('Período')
plt.ylabel('Monto')
plt.title('Compras, Ventas y Diferencia por Período')

# Añadir etiquetas de período en el eje X
plt.xticks(bar_positions, df['periodo'], rotation=45)
plt.legend()

# Ajustar el diseño del gráfico
plt.tight_layout()


# Crear un archivo temporal para la imagen
with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_image:
    plt.savefig(temp_image, format='png')
    temp_image_path = temp_image.name

pdf.image(temp_image_path, x=10, y=pdf.get_y(), w=190)

os.remove(temp_image_path)

# Cerrar el gráfico de Matplotlib
plt.close()

# ---- PAGINA 2 -----
pdf.add_page()

limite_categoria_anterior = 5382248.94
limite_categoria_actual = 6458698.71
limite_monotributo_servicios = 7996484.12

# a cuanto estoy de pasarme de categoria?
diferencia_pase_categoria = limite_categoria_actual - total_ventas
diferencia_exclusion = limite_monotributo_servicios - total_ventas

porcentaje_cumplimiento = (total_ventas / limite_categoria_actual) * 100

# Agregar espacio antes del título
pdf.ln(10)

# Agregar línea divisoria antes del título
pdf.line(10, pdf.get_y(), 200, pdf.get_y())
pdf.ln(10)

pdf.set_font('Arial', 'B', 14)
pdf.cell(0, 10, 'Analisis de Categoria del periodo', ln=1)

# Agregar línea divisoria después del título
pdf.line(10, pdf.get_y(), 200, pdf.get_y())
pdf.ln(10)

pdf.set_font('Arial', '', 12)
pdf.set_fill_color(200, 200, 200)
pdf.cell(80, 10, f'Total de ventas del periodo analizado:', border=1, ln=0, align='L', fill=True)
pdf.cell(80, 10, f'{total_ventas}', border=1, ln=1, align='C', fill=True)
pdf.set_font('Arial', '', 12)
pdf.cell(80, 10, f'Limite Categoria Actual:', border=1, ln=0, align='L', fill=True)
pdf.cell(80, 10, f'{limite_categoria_actual}', border=1, ln=1, align='C', fill=True)
pdf.set_font('Arial', 'B', 12)
pdf.ln(5)
pdf.cell(100, 10, f'Estas a {round(diferencia_pase_categoria, 2)}$ de pasarte de categoria.', ln=1)
# Separador
pdf.ln(5)
pdf.line(10, pdf.get_y(), 200, pdf.get_y())
pdf.ln(5)

# Crear el gráfico de medidor (gauge chart)
fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=porcentaje_cumplimiento,
    domain={'x': [0, 1], 'y': [0, 1]},
    gauge={'axis': {'range': [0, 100], 'tickvals': [0, 25, 50, 75, 100], 'tickwidth': 1, 'tickcolor': 'darkblue'},
           'bar': {'color': "darkblue"},
           'steps': [
               {'range': [0, 25], 'color': "lightgreen"},
               {'range': [25, 50], 'color': "lightgreen"},
               {'range': [50, 75], 'color': "lightsalmon"},
               {'range': [75, 100], 'color': "lightcoral"}]
           }
))

# Personalizar diseño
fig.update_layout(
    title="Cumplimiento de Límite de Categoría",
    title_x=0.5,  # Centrar el título horizontalmente
    font=dict(family='Arial', size=16),
    showlegend=False,
    margin=dict(t=50, b=50)  # Añadir margen superior para el título
)

# Exportar el gráfico de Plotly como una imagen PNG
img_file = 'gauge_chart.png'
pio.write_image(fig, img_file)
# Insertar la imagen en el PDF
pdf.image(img_file, x=10, y=pdf.get_y(), w=130)
os.remove(img_file)

# Guardar el informe en un archivo PDF
pdf_file = 'informe_monotributo.pdf'
pdf.output(pdf_file)

print(f'Informe guardado en {pdf_file}')


