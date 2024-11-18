import matplotlib.pyplot as plt
import numpy as np

# Datos del cambio promedio anual de la población en México
years = ['2000-2005', '2005-2010', '2010-2015', '2015-2020', '2020-2025',
         '2025-2030', '2030-2035', '2035-2040', '2040-2045', '2045-2050']
values = np.array([1.71, 1.96, 1.78, 1.59, 1.40, 1.22, 1.04, 0.88, 0.73, 0.59])

# Configurar el estilo moderno con fondo oscuro
plt.style.use('dark_background')

# Definir propiedades para el diseño moderno
boxprops = {"facecolor": "#1f77b4", "edgecolor": "#ff7f0e", "linewidth": 2}
medianprops = {"color": "#ffdd57", "linewidth": 2}
whiskerprops = {"color": "#ff7f0e", "linewidth": 2}
capprops = {"color": "#ff7f0e", "linewidth": 2}

# Crear la figura y el diagrama de caja y bigote
fig, ax = plt.subplots(figsize=(12, 7))
ax.boxplot(values, patch_artist=True, boxprops=boxprops, medianprops=medianprops,
           whiskerprops=whiskerprops, capprops=capprops, widths=0.7)

# Personalizar la gráfica
ax.set_title("Cambio Promedio Anual en México (2000-2050) - Estilo Moderno", fontsize=18, color="#ffdd57")
ax.set_xlabel("México", fontsize=14, color="#ffdd57")
ax.set_ylabel("Cambio Promedio Anual (%)", fontsize=14, color="#ffdd57")
ax.set_yticks(np.arange(0, 2.5, 0.5))
ax.grid(False)

# Añadir un fondo degradado
fig.patch.set_facecolor("#2a2a2a")
ax.set_facecolor("#1c1c1c")

# Mostrar la gráfica
plt.show()
