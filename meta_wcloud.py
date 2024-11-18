import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Cargar el archivo CSV
file_path = "Metadata_Country_API_SP.POP.TOTL_DS2_es_csv_v2_31996.csv"
df = pd.read_csv(file_path, skiprows=4)

# Filtrar el registro correspondiente a México
mexico_data = df[df['Unnamed: 0'] == 'México']

# Unir toda la información en una sola cadena de texto para el WordCloud
text = " ".join(str(value) for value in mexico_data.values.flatten() if pd.notna(value))

# Crear el WordCloud
wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='viridis').generate(text)

# Mostrar el WordCloud
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title("WordCloud para Datos de México")
plt.show()
