import dash
from dash import html, dcc
import dash.dependencies as dd
import geemap.foliumap as geemap
import ee

# Autenticación e inicialización de Earth Engine
ee.Authenticate()
ee.Initialize(project='project-dashboard-440216')


# Función para crear el mapa base con una paleta de colores mejorada y fondo gris oscuro
def crear_mapa_base():
    # Crear el mapa con un centro y zoom definidos, utilizando el fondo 'HYBRID'
    mapa = geemap.Map(center=[18.5, -99.0], zoom=5, basemap='HYBRID')

    # Cargar la colección de imágenes de luces nocturnas y calcular la media
    viirs = ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG') \
        .select('avg_rad') \
        .filterDate('2023-01-01', '2023-12-31') \
        .mean()

    # Parámetros de visualización con una nueva paleta de colores simplificada
    vis_params = {
        'min': 0,
        'max': 60,
        'palette': ['#000033', '#002266', '#0044CC', '#66FFFF', '#FFFF66', '#FF9933', '#FF3333']
    }

    # Agregar la capa de luces nocturnas al mapa
    mapa.addLayer(viirs, vis_params, 'Night Lights 2023')
    return mapa


# Función para agregar los contornos de México al mapa con estilo mejorado
def agregar_contornos_mexico(mapa):
    # Cargar la colección de fronteras de México
    borders_mexico = ee.FeatureCollection("FAO/GAUL/2015/level1") \
        .filter(ee.Filter.eq('ADM0_NAME', 'Mexico'))

    # Estilo para los contornos nacionales y estatales
    country_border_style = {'color': '#FFD700', 'fillColor': '00000000', 'width': 2}  # Oro suave
    state_border_style = {'color': '#FFFFCC', 'fillColor': '00000000', 'width': 0.5}  # Amarillo claro

    # Agregar los contornos al mapa
    mapa.addLayer(borders_mexico.style(**country_border_style), {}, 'Mexico Border')
    mapa.addLayer(borders_mexico.style(**state_border_style), {}, 'State Borders')
    return mapa


# Crear el archivo HTML para el mapa base
mapa_base = crear_mapa_base()
mapa_base.save('mapa_base.html')

# Configuración del Dashboard de Dash
app = dash.Dash(__name__, title="Análisis del Crecimiento Urbano",
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}])

# Layout del Dashboard con estilo mejorado y degradado moderno
app.layout = html.Div(
    style={
        'background': 'linear-gradient(135deg, #1F1C2C, #928DAB)',  # Degradado azul oscuro a púrpura
        'padding': '20px',
        'fontFamily': 'Arial, sans-serif',
        'color': '#E0E0E0'  # Color de texto claro
    },
    children=[
        html.H1(
            "Análisis y Predicción del Crecimiento Urbano en México",
            style={
                'textAlign': 'center',
                'color': '#FFFFFF',  # Título en blanco
                'marginBottom': '20px',
                'fontWeight': 'bold'
            }
        ),
        html.Button(
            "Marcar",
            id="boton-marcar",
            n_clicks=0,
            style={
                'display': 'block',
                'margin': '0 auto',
                'padding': '10px 20px',
                'fontSize': '16px',
                'background': 'linear-gradient(135deg, #0F2027, #2C5364)',  # Degradado azul oscuro
                'color': '#E0FFFF',
                'border': 'none',
                'borderRadius': '10px',
                'cursor': 'pointer',
                'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.2)'
            }
        ),
        html.Iframe(
            id="map",
            srcDoc=open('mapa_base.html', 'r').read(),
            style={
                'width': '100%',
                'height': '80vh',
                'border': 'none',
                'marginTop': '20px',
                'borderRadius': '10px',
                'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.2)'
            }
        ),
        html.H2(
            "Animación del Crecimiento de la Población por País",
            style={
                'textAlign': 'center',
                'color': '#FFFFFF',
                'marginTop': '20px',
                'marginBottom': '20px'
            }
        ),
        html.Video(
            controls=True,
            src="assets/crecimiento_poblacion.mp4",
            style={
                'width': '100%',
                'height': 'auto',
                'borderRadius': '10px',
                'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.2)'
            }
        )
    ]
)


# Callback para actualizar el mapa cuando se presiona el botón
@app.callback(
    dd.Output('map', 'srcDoc'),
    [dd.Input('boton-marcar', 'n_clicks')]
)
def actualizar_mapa(n_clicks):
    if n_clicks > 0:
        # Crear un nuevo mapa con los contornos de México
        mapa_con_contornos = crear_mapa_base()
        mapa_con_contornos = agregar_contornos_mexico(mapa_con_contornos)
        mapa_con_contornos.save('mapa_con_contornos.html')
        return open('mapa_con_contornos.html', 'r').read()
    else:
        # Mostrar el mapa base
        return open('mapa_base.html', 'r').read()


# Ejecución del servidor
if __name__ == '__main__':
    app.run_server(debug=False, port=8050)
