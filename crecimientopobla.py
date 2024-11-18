import pandas as pd
import matplotlib.pyplot as plt

# Ruta del archivo Excel
file_path = "crecimientodelapoblacion.xlsx"

# Leer el archivo Excel y seleccionar la primera hoja
data = pd.read_excel(file_path, sheet_name='Sheet1')

# Limpiar los datos eliminando columnas innecesarias y estableciendo el índice
data_clean = data.drop(columns=["Country Code"]).set_index("Country Name").transpose()

# Convertir el índice (años) a tipo numérico
data_clean.index = pd.to_numeric(data_clean.index, errors='coerce')

# Convertir los datos a tipo numérico y rellenar valores NaN con 0
data_clean = data_clean.apply(pd.to_numeric, errors='coerce').fillna(0)

# Escalar los valores de población a millones
data_scaled = data_clean / 1e6
max_population = data_clean.max().max()

# Crear la figura y los ejes
fig, ax = plt.subplots(figsize=(14, 8))

# Configuración de la gráfica
ax.set_title("Crecimiento de la Población por País (1960-2023)", fontsize=16)
ax.set_xlabel("Año", fontsize=14)
ax.set_ylabel("Población (en millones)", fontsize=14)
ax.grid(visible=True, linestyle='--', linewidth=0.7)
ax.set_xlim([data_scaled.index.min(), data_scaled.index.max()])
ax.set_ylim([0, max_population / 1e6])
ax.tick_params(axis='x', rotation=45)

# Graficar líneas para cada país
for country in data_scaled.columns:
    ax.plot(data_scaled.index, data_scaled[country], label=country, linewidth=2, marker='o')

# Añadir la leyenda
ax.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=10)

# Mostrar la gráfica
plt.show()
