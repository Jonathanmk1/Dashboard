import dash
from dash import html, dcc
import dash.dependencies as dd
import geemap.foliumap as geemap
import ee
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.ensemble import GradientBoostingRegressor
from datetime import datetime

# Autenticación e inicialización de Earth Engine
ee.Authenticate()
ee.Initialize(project='project-dashboard-440216')

# Función para crear el mapa base
def crear_mapa_base():
    mapa = geemap.Map(center=[18.5, -99.0], zoom=5, basemap='HYBRID')
    viirs = ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG').select('avg_rad').filterDate('2023-01-01', '2023-12-31').mean()
    vis_params = {'min': 0, 'max': 60, 'palette': ['#000033', '#002266', '#0044CC', '#66FFFF', '#FFFF66', '#FF9933', '#FF3333']}
    mapa.addLayer(viirs, vis_params, 'Night Lights 2023')
    return mapa

def agregar_contornos_mexico(mapa):
    borders_mexico = ee.FeatureCollection("FAO/GAUL/2015/level1").filter(ee.Filter.eq('ADM0_NAME', 'Mexico'))
    country_border_style = {'color': '#FFD700', 'fillColor': '00000000', 'width': 2}
    state_border_style = {'color': '#FFFFCC', 'fillColor': '00000000', 'width': 0.5}
    mapa.addLayer(borders_mexico.style(**country_border_style), {}, 'Mexico Border')
    mapa.addLayer(borders_mexico.style(**state_border_style), {}, 'State Borders')
    return mapa

# Crear archivo HTML para el mapa base
mapa_base = crear_mapa_base()
mapa_base.save('mapa_base.html')

# Lista de estados mexicanos, incluyendo "Estados Unidos Mexicanos"
estados_mexico = [
    "Estados Unidos Mexicanos", "Aguascalientes", "Baja California", "Baja California Sur",
    "Campeche", "Chiapas", "Chihuahua", "Ciudad de México", "Coahuila", "Colima",
    "Durango", "Guanajuato", "Guerrero", "Hidalgo", "Jalisco", "México", "Michoacán",
    "Morelos", "Nayarit", "Nuevo León", "Oaxaca", "Puebla", "Querétaro", "Quintana Roo",
    "San Luis Potosí", "Sinaloa", "Sonora", "Tabasco", "Tamaulipas", "Tlaxcala",
    "Veracruz", "Yucatán", "Zacatecas"
]

# Datos para gráfica de burbujas
file_path_burbujas = "TD_Nacional.xlsm"
data_burbujas = pd.read_excel(file_path_burbujas, sheet_name='Data')
df_clean = data_burbujas[['Nom_Ent', 'Pobtot', 'Pobreza', 'Pobreza_E', 'Pobreza_M', 'Yhat_Plb', 'Yhat_Plbm']].dropna()
df_clean[['Pobtot', 'Pobreza', 'Pobreza_E', 'Pobreza_M', 'Yhat_Plb', 'Yhat_Plbm']] = df_clean[
    ['Pobtot', 'Pobreza', 'Pobreza_E', 'Pobreza_M', 'Yhat_Plb', 'Yhat_Plbm']].apply(pd.to_numeric, errors='coerce')
df_clean = df_clean.dropna()
kmeans = KMeans(n_clusters=3, random_state=0)
df_clean['Cluster'] = kmeans.fit_predict(df_clean[['Pobreza', 'Pobreza_E', 'Pobreza_M', 'Yhat_Plb', 'Yhat_Plbm']])

# Datos para gráfica de población
file_path_poblacion = "crecimientodelapoblacion.xlsx"
data_poblacion = pd.read_excel(file_path_poblacion, sheet_name='Sheet1')
data_clean = data_poblacion.drop(columns=["Country Code"]).set_index("Country Name").transpose()
data_clean.index = pd.to_numeric(data_clean.index, errors='coerce')
data_clean = data_clean.apply(pd.to_numeric, errors='coerce').fillna(0)
data_scaled = data_clean / 1e6

# Datos para gráfica de esperanza de vida
file_path_vida = "Esperanza de vida al nacer_1950_2070_limpio.csv"
df_vida = pd.read_csv(file_path_vida)
df_mexico = df_vida[df_vida['ENTIDAD'] == 'República Mexicana']
df_hombres = df_mexico[df_mexico['SEXO'] == 'Hombres']
df_mujeres = df_mexico[df_mexico['SEXO'] == 'Mujeres']
X_hombres = df_hombres[['AÑO']].values
y_hombres = df_hombres['EV'].values
X_mujeres = df_mujeres[['AÑO']].values
y_mujeres = df_mujeres['EV'].values
predict_years = np.arange(2021, 2071).reshape(-1, 1)
model_hombres = GradientBoostingRegressor(n_estimators=200, random_state=42)
model_hombres.fit(X_hombres, y_hombres)
model_mujeres = GradientBoostingRegressor(n_estimators=200, random_state=42)
model_mujeres.fit(X_mujeres, y_mujeres)
df_pred_hombres = pd.DataFrame({'AÑO': predict_years.flatten(), 'EV': model_hombres.predict(predict_years)})
df_pred_mujeres = pd.DataFrame({'AÑO': predict_years.flatten(), 'EV': model_mujeres.predict(predict_years)})

# Configuración del Layout
app = dash.Dash(__name__, title="Análisis del Crecimiento Urbano")
app.layout = html.Div(
    style={
        'display': 'grid',
        'gridTemplateColumns': '1fr 1fr',
        'gridTemplateRows': 'auto 1fr 1fr',
        'height': '100vh',
        'gap': '10px',
        'padding': '10px',
        'background': 'linear-gradient(135deg, #1F1C2C, #00c9ff)'
    },
    children=[
        html.Div(
            style={'gridColumn': '1 / span 2', 'textAlign': 'center', 'padding': '10px', 'backgroundColor': 'rgba(0, 0, 0, 0.2)', 'borderRadius': '10px'},
            children=[
                html.H1("Análisis y Predicción del Crecimiento Urbano en México", style={'color': '#FFFFFF', 'fontWeight': 'bold'})
            ]
        ),
        html.Div(
            style={'gridColumn': '1 / span 2', 'display': 'flex', 'justifyContent': 'space-around', 'alignItems': 'center', 'padding': '10px', 'backgroundColor': 'rgba(255, 255, 255, 0.1)', 'borderRadius': '10px'},
            children=[
                html.Button(id='fecha-actual', children="Fecha Actual", style={'padding': '10px 20px', 'fontSize': '16px', 'background': '#2C5364', 'color': '#E0FFFF', 'border': 'none', 'borderRadius': '10px', 'cursor': 'pointer'}),
                html.Button(id="boton-marcar", children="Marcar", n_clicks=0, style={'padding': '10px 20px', 'fontSize': '16px', 'background': '#0F2027', 'color': '#E0FFFF', 'border': 'none', 'borderRadius': '10px', 'cursor': 'pointer'}),
                dcc.Dropdown(
                    id='dropdown-estado',
                    options=[{'label': estado, 'value': estado} for estado in estados_mexico],
                    placeholder="Seleccionar Estado",
                    style={'width': '200px', 'borderRadius': '10px'}
                )
            ]
        ),
        dcc.Graph(id='grafica-burbujas', style={'gridColumn': '1', 'gridRow': '2', 'height': '100%', 'borderRadius': '10px'}),
        html.Div(
            style={'gridColumn': '2', 'gridRow': '2', 'height': '100%', 'borderRadius': '10px', 'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.2)', 'overflow': 'hidden'},
            children=[
                html.Iframe(id="map", srcDoc=open('mapa_base.html', 'r').read(), style={'width': '100%', 'height': '100%', 'border': 'none'})
            ]
        ),
        dcc.Graph(id='grafica-poblacion', style={'gridColumn': '1', 'gridRow': '3', 'height': '100%', 'borderRadius': '10px'}),
        dcc.Graph(id='grafica-esperanza-vida', style={'gridColumn': '2', 'gridRow': '3', 'height': '100%', 'borderRadius': '10px'}),
        dcc.Interval(id='intervalo-burbujas', interval=300, n_intervals=0, disabled=True),
        dcc.Interval(id='intervalo-poblacion', interval=3000, n_intervals=0, disabled=True),
        dcc.Interval(id='intervalo-esperanza', interval=3000, n_intervals=0, disabled=True)
    ]
)

@app.callback(
    [dd.Output('map', 'srcDoc'),
     dd.Output('intervalo-burbujas', 'disabled'),
     dd.Output('intervalo-poblacion', 'disabled'),
     dd.Output('intervalo-esperanza', 'disabled')],
    [dd.Input('boton-marcar', 'n_clicks')]
)
def actualizar_mapa_y_animaciones(n_clicks):
    if n_clicks and n_clicks > 0:
        mapa_con_contornos = crear_mapa_base()
        agregar_contornos_mexico(mapa_con_contornos)
        mapa_con_contornos.save('mapa_con_contornos.html')
        return open('mapa_con_contornos.html', 'r').read(), False, False, False
    return open('mapa_base.html', 'r').read(), True, True, True

@app.callback(
    dd.Output('grafica-burbujas', 'figure'),
    [dd.Input('intervalo-burbujas', 'n_intervals')]
)
def animar_burbujas(n_intervals):
    rango_index = min(n_intervals, len(df_clean))
    data_actualizada = df_clean.iloc[:rango_index]
    fig = px.scatter(
        data_actualizada,
        x='Pobreza',
        y='Yhat_Plb',
        size='Pobtot',
        color='Cluster',
        hover_name='Nom_Ent',
        labels={'Pobreza': 'Porcentaje de Pobreza', 'Yhat_Plb': 'Predicción de Pobreza'},
        title='Agrupamiento de Estados de México según Indicadores de Pobreza',
        size_max=50
    )
    return fig

@app.callback(
    dd.Output('grafica-poblacion', 'figure'),
    [dd.Input('intervalo-poblacion', 'n_intervals')]
)
def animar_poblacion(n_intervals):
    end_year = 1960 + min(n_intervals * 5, 2023 - 1960)
    data_actualizada = data_scaled[data_scaled.index <= end_year]
    fig = go.Figure()
    for country in data_actualizada.columns:
        fig.add_trace(go.Scatter(
            x=data_actualizada.index,
            y=data_actualizada[country],
            mode='lines+markers',
            name=country
        ))
    fig.update_layout(
        title="Crecimiento Acumulativo de la Población",
        xaxis_title="Año",
        yaxis_title="Población (millones)",
        xaxis=dict(tickmode='linear', dtick=5),
        template="plotly_dark"
    )
    return fig

@app.callback(
    dd.Output('grafica-esperanza-vida', 'figure'),
    [dd.Input('intervalo-esperanza', 'n_intervals')]
)
def animar_esperanza_vida(n_intervals):
    end_year = 1950 + min(n_intervals * 5, 2070 - 1950)
    datos_hombres = df_hombres[df_hombres['AÑO'] <= end_year]
    datos_mujeres = df_mujeres[df_mujeres['AÑO'] <= end_year]
    pred_hombres = df_pred_hombres[df_pred_hombres['AÑO'] <= end_year]
    pred_mujeres = df_pred_mujeres[df_pred_mujeres['AÑO'] <= end_year]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=datos_hombres['AÑO'],
        y=datos_hombres['EV'],
        mode='lines+markers',
        name='Hombres (Histórico)',
        line=dict(color='blue')
    ))
    fig.add_trace(go.Scatter(
        x=datos_mujeres['AÑO'],
        y=datos_mujeres['EV'],
        mode='lines+markers',
        name='Mujeres (Histórico)',
        line=dict(color='purple')
    ))
    fig.add_trace(go.Scatter(
        x=pred_hombres['AÑO'],
        y=pred_hombres['EV'],
        mode='lines+markers',
        name='Hombres (Predicción)',
        line=dict(color='red', dash='dash')
    ))
    fig.add_trace(go.Scatter(
        x=pred_mujeres['AÑO'],
        y=pred_mujeres['EV'],
        mode='lines+markers',
        name='Mujeres (Predicción)',
        line=dict(color='orange', dash='dash')
    ))
    fig.update_layout(
        title="Predicción de la Esperanza de Vida al Nacer en México",
        xaxis_title="Año",
        yaxis_title="Esperanza de Vida (Años)",
        xaxis=dict(tickmode='linear', dtick=10),
        template="plotly_dark"
    )
    return fig

@app.callback(
    dd.Output('fecha-actual', 'children'),
    [dd.Input('fecha-actual', 'n_clicks')]
)
def mostrar_fecha_actual(n_clicks):
    if n_clicks and n_clicks > 0:
        return f"Fecha Actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    return "Fecha Actual"

# Ejecutar el servidor
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
