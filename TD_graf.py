import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans

# Cargar el archivo de datos
file_path = "TD_Nacional.xlsm"
data = pd.read_excel(file_path, sheet_name='Data')

# Limpiar y seleccionar columnas relevantes
df_clean = data[['Nom_Ent', 'Pobtot', 'Pobreza', 'Pobreza_E', 'Pobreza_M', 'Yhat_Plb', 'Yhat_Plbm']].dropna()

# Convertir las columnas a tipo numérico
df_clean[['Pobtot', 'Pobreza', 'Pobreza_E', 'Pobreza_M', 'Yhat_Plb', 'Yhat_Plbm']] = df_clean[
    ['Pobtot', 'Pobreza', 'Pobreza_E', 'Pobreza_M', 'Yhat_Plb', 'Yhat_Plbm']].apply(pd.to_numeric, errors='coerce')

# Filtrar datos para evitar filas con valores NaN
df_clean = df_clean.dropna()

# Seleccionar las características para el clustering
X = df_clean[['Pobreza', 'Pobreza_E', 'Pobreza_M', 'Yhat_Plb', 'Yhat_Plbm']]

# Aplicar K-means con 3 clusters
kmeans = KMeans(n_clusters=3, random_state=0)
df_clean['Cluster'] = kmeans.fit_predict(X)

# Crear gráfica de burbujas
plt.figure(figsize=(12, 8))
scatter = plt.scatter(
    df_clean['Pobreza'],
    df_clean['Yhat_Plb'],
    s=df_clean['Pobtot'] / 10000,  # Tamaño de burbuja basado en la población total
    c=df_clean['Cluster'],
    cmap='viridis',
    alpha=0.6,
    edgecolors='w'
)

# Añadir etiquetas y título
plt.title("Agrupamiento de Estados de México según Indicadores de Pobreza", fontsize=16)
plt.xlabel("Porcentaje de Pobreza", fontsize=14)
plt.ylabel("Yhat_Plb (Predicción de Pobreza)", fontsize=14)
plt.colorbar(scatter, label="Cluster")
plt.grid(True)

# Mostrar la gráfica
plt.show()
