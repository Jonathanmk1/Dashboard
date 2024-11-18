import pandas as pd
import matplotlib.pyplot as plt

# Cargar el archivo CSV
file_path = "The_World_Bank_Population_growth_(annual_).csv"
df = pd.read_csv(file_path)

# Filtrar países de América
americas_countries = [
    "Mexico", "United States", "Canada", "Brazil", "Argentina",
    "Colombia", "Chile", "Peru", "Venezuela", "Ecuador"
]

# Filtrar el DataFrame
df_americas = df[df['country_name'].isin(americas_countries)]

# Transformar el DataFrame para análisis temporal
df_melted_americas = df_americas.melt(id_vars=["country_name"], var_name="Year", value_name="Population Growth")

# Convertir el año a formato numérico
df_melted_americas["Year"] = pd.to_numeric(df_melted_americas["Year"], errors='coerce')
df_melted_americas = df_melted_americas.dropna(subset=["Year", "Population Growth"])
df_melted_americas["Year"] = df_melted_americas["Year"].astype(int)

# Crear la visualización
plt.figure(figsize=(14, 7))
color_palette = plt.get_cmap('tab10', len(americas_countries))

for i, country in enumerate(americas_countries):
    country_data = df_melted_americas[df_melted_americas['country_name'] == country]
    plt.plot(
        country_data['Year'],
        country_data['Population Growth'],
        label=country,
        color=color_palette(i),
        linewidth=2,
        alpha=0.8
    )

# Ajustes de la gráfica
plt.title("Tendencia del Crecimiento Poblacional (1961-2022) para Países de América", fontsize=16)
plt.xlabel("Año", fontsize=14)
plt.ylabel("Crecimiento Poblacional Anual (%)", fontsize=14)
plt.xticks(rotation=45)
plt.grid(True)
plt.legend(title="Países", loc='upper left', fontsize=12)
plt.show()
