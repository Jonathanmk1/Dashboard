import dash
from dash import html, dcc
import dash.dependencies as dd
import geemap.foliumap as geemap
import ee
import pandas as pd
import plotly.graph_objs as go

# Autenticación e inicialización de Earth Engine
ee.Authenticate()
ee.Initialize(project='project-dashboard-440216')

# Ruta del archivo Excel
file_path = "crecimientodelapoblacion.xlsx"

# Función para crear el mapa base
def crear_mapa_base():
    mapa = geemap.Map(center=[18.5, -99.0], zoom=5, basemap='HYBRID')
    viirs = ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG') \
        .select('avg_rad') \
        .filterDate('2023-01-01', '2023-12-31') \
        .mean()

    vis_params = {
        'min': 0,
        'max': 60,
        'palette': ['#000033', '#002266', '#0044CC', '#66FFFF', '#FFFF66', '#FF9933', '#FF3333']
    }

    mapa.addLayer(viirs, vis_params, 'Night Lights 2023')
    return mapa

# Función para agregar contornos de México
def agregar_contornos_mexico(mapa):
    borders_mexico = ee.FeatureCollection("FAO/GAUL/2015/level1") \
        .filter(ee.Filter.eq('ADM0_NAME', 'Mexico'))

    country_border_style = {'color': '#FFD700', 'fillColor': '00000000', 'width': 2}
    state_border_style = {'color': '#FFFFCC', 'fillColor': '00000000', 'width': 0.5}

    mapa.addLayer(borders_mexico.style(**country_border_style), {}, 'Mexico Border')
    mapa.addLayer(borders_mexico.style(**state_border_style), {}, 'State Borders')
    return mapa

# Crear el archivo HTML para el mapa base
mapa_base = crear_mapa_base()
mapa_base.save('mapa_base.html')

# Función para crear la gráfica interactiva
def crear_grafica():
    # Leer el archivo Excel y procesar los datos
    data = pd.read_excel(file_path, sheet_name='Sheet1')
    data_clean = data.drop(columns=["Country Code"]).set_index("Country Name").transpose()
    data_clean.index = pd.to_numeric(data_clean.index, errors='coerce')
    data_clean = data_clean.apply(pd.to_numeric, errors='coerce').fillna(0)
    data_scaled = data_clean / 1e6

    # Crear la gráfica usando Plotly
    fig = go.Figure()

    # Agregar trazos para cada país
    for country in data_scaled.columns:
        fig.add_trace(go.Scatter(
            x=data_scaled.index,
            y=data_scaled[country],
            mode='lines',
            name=country
        ))

    # Configuración de la gráfica
    fig.update_layout(
        title="Crecimiento de la Población por País (1960-2023)",
        xaxis_title="Año",
        yaxis_title="Población (en millones)",
        template="plotly_dark",
        legend_title="País",
        margin=dict(l=0, r=0, t=40, b=20)
    )

    return fig

# Configuración del Dashboard de Dash
app = dash.Dash(__name__, title="Análisis del Crecimiento Urbano",
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}])

# Layout del Dashboard
app.layout = html.Div(
    style={
        'background': 'linear-gradient(135deg, #1F1C2C, #928DAB)',
        'padding': '20px',
        'fontFamily': 'Arial, sans-serif',
        'color': '#E0E0E0'
    },
    children=[
        html.H1(
            "Análisis y Predicción del Crecimiento Urbano en México",
            style={'textAlign': 'center', 'color': '#FFFFFF', 'marginBottom': '20px', 'fontWeight': 'bold'}
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
                'background': 'linear-gradient(135deg, #0F2027, #2C5364)',
                'color': '#E0FFFF',
                'border': 'none',
                'borderRadius': '10px',
                'cursor': 'pointer'
            }
        ),
        html.Iframe(
            id="map",
            srcDoc=open('mapa_base.html', 'r').read(),
            style={'width': '100%', 'height': '80vh', 'border': 'none', 'marginTop': '20px'}
        ),
        html.H2(
            "Gráfica del Crecimiento de la Población",
            style={'textAlign': 'center', 'color': '#FFFFFF', 'marginTop': '20px'}
        ),
        dcc.Graph(id='grafica-poblacion'),
        dcc.Interval(
            id='intervalo-actualizacion',
            interval=20000,  # 20 segundos en milisegundos
            n_intervals=0
        )
    ]
)

# Callback para actualizar el mapa
@app.callback(
    dd.Output('map', 'srcDoc'),
    [dd.Input('boton-marcar', 'n_clicks')]
)
def actualizar_mapa(n_clicks):
    if n_clicks > 0:
        mapa_con_contornos = crear_mapa_base()
        mapa_con_contornos = agregar_contornos_mexico(mapa_con_contornos)
        mapa_con_contornos.save('mapa_con_contornos.html')
        return open('mapa_con_contornos.html', 'r').read()
    else:
        return open('mapa_base.html', 'r').read()

# Callback para actualizar la gráfica cada 3 minutos
@app.callback(
    dd.Output('grafica-poblacion', 'figure'),
    [dd.Input('intervalo-actualizacion', 'n_intervals')]
)
def actualizar_grafica(n_intervals):
    return crear_grafica()

# Ejecutar el servidor
if __name__ == '__main__':
    app.run_server(debug=False, port=8050)
