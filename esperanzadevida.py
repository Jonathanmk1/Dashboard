import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
import matplotlib.pyplot as plt

# Cargar el archivo CSV
file_path = "Esperanza de vida al nacer_1950_2070_limpio.csv"
df = pd.read_csv(file_path)

# Filtrar datos para la "República Mexicana" y separar por sexo
df_mexico = df[df['ENTIDAD'] == 'República Mexicana']
df_hombres = df_mexico[df_mexico['SEXO'] == 'Hombres']
df_mujeres = df_mexico[df_mexico['SEXO'] == 'Mujeres']

# Seleccionar las columnas de interés
X_hombres = df_hombres[['AÑO']].values
y_hombres = df_hombres['EV'].values
X_mujeres = df_mujeres[['AÑO']].values
y_mujeres = df_mujeres['EV'].values

# Crear rango de años para predicciones (2021-2070)
predict_years = np.arange(2021, 2071).reshape(-1, 1)

# Crear y entrenar el modelo Gradient Boosting
model_hombres = GradientBoostingRegressor(n_estimators=200, random_state=42)
model_hombres.fit(X_hombres, y_hombres)
y_pred_hombres = model_hombres.predict(predict_years)

model_mujeres = GradientBoostingRegressor(n_estimators=200, random_state=42)
model_mujeres.fit(X_mujeres, y_mujeres)
y_pred_mujeres = model_mujeres.predict(predict_years)

# Crear la gráfica tipo "filled area chart"
plt.figure(figsize=(14, 8))
plt.fill_between(X_hombres.flatten(), y_hombres, color='blue', alpha=0.3, label='Datos Históricos - Hombres')
plt.fill_between(X_mujeres.flatten(), y_mujeres, color='purple', alpha=0.3, label='Datos Históricos - Mujeres')
plt.fill_between(predict_years.flatten(), y_pred_hombres, color='red', alpha=0.5, label='Predicción - Hombres (Gradient Boosting)')
plt.fill_between(predict_years.flatten(), y_pred_mujeres, color='orange', alpha=0.5, label='Predicción - Mujeres (Gradient Boosting)')

# Ajustes de la gráfica
plt.title("Predicción de la Esperanza de Vida al Nacer en México (1950-2070) - Filled Area Chart", fontsize=16)
plt.xlabel("Año", fontsize=14)
plt.ylabel("Esperanza de Vida (Años)", fontsize=14)
plt.grid(True)
plt.legend(title="Leyenda", fontsize=12)
plt.show()
