import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import requests

app = dash.Dash(__name__)
app.title = "Dashboard de Monitoreo de Sensores"

API_URL = "http://127.0.0.1:5000/sensors/"

# Estilos CSS personalizados para un diseño profesional
COLORS = {
    'background': '#f8f9fa',
    'card_bg': '#ffffff',
    'text': '#212529',
    'primary': '#0d6efd',
    'secondary': '#6c757d',
    'border': '#dee2e6'
}

app.layout = html.Div(style={
    'backgroundColor': COLORS['background'],
    'fontFamily': 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif',
    'minHeight': '100vh',
    'padding': '30px'
}, children=[
    
    # Componente de actualización automática cada 2 segundos
    dcc.Interval(
        id='interval-component',
        interval=2000,
        n_intervals=0
    ),
    
    # Encabezado principal
    html.Div([
        html.H1("📊 Dashboard de Monitoreo de Sensores", style={
            'textAlign': 'center', 
            'color': COLORS['text'],
            'fontWeight': '600',
            'marginBottom': '5px'
        }),
        html.P("Sistema en tiempo real integrado con API Flask y Dash", style={
            'textAlign': 'center',
            'color': COLORS['secondary'],
            'fontSize': '15px',
            'marginBottom': '30px'
        })
    ]),
    
    # Controles de filtrado (Fila superior)
    html.Div([
        html.Div([
            html.Label("Tipo de Sensor:", style={'fontWeight': '600', 'color': COLORS['text'], 'marginBottom': '8px', 'display': 'block'}),
            dcc.Dropdown(
                id='dropdown-type',
                options=[
                    {'label': '🌡️ Temperatura', 'value': 'temperatura'},
                    {'label': '🔵 Presión', 'value': 'presión'},
                    {'label': '⚡ Velocidad', 'value': 'velocidad'}
                ],
                value='temperatura',
                clearable=False,
                style={'borderRadius': '8px'}
            )
        ], style={'width': '45%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        
        html.Div([
            html.Label("ID del Sensor:", style={'fontWeight': '600', 'color': COLORS['text'], 'marginBottom': '8px', 'display': 'block'}),
            dcc.Dropdown(
                id='dropdown-sensor-id',
                clearable=False,
                style={'borderRadius': '8px'}
            )
        ], style={'width': '45%', 'display': 'inline-block', 'verticalAlign': 'top', 'float': 'right'}),
    ], style={
        'backgroundColor': COLORS['card_bg'],
        'padding': '20px',
        'borderRadius': '12px',
        'boxShadow': '0 4px 6px rgba(0,0,0,0.05)',
        'marginBottom': '25px',
        'maxWidth': '900px',
        'marginLeft': 'auto',
        'marginRight': 'auto'
    }),
    
    # Tarjetas de Indicadores (KPIs)

    html.Div([
        html.Div([
            html.H5("Promedio", style={'color': COLORS['secondary'], 'fontSize': '14px', 'textTransform': 'uppercase', 'letterSpacing': '1px'}),
            html.P(id='indicator-avg', style={'fontSize': '26px', 'fontWeight': 'bold', 'color': COLORS['primary'], 'margin': '5px 0 0 0'})
        ], style={
            'flex': '1', 'backgroundColor': COLORS['card_bg'], 
            'padding': '20px', 'borderRadius': '12px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.05)', 
            'textAlign': 'center', 'margin': '0 10px'
        }),
        
        html.Div([
            html.H5("Mínimo", style={'color': COLORS['secondary'], 'fontSize': '14px', 'textTransform': 'uppercase', 'letterSpacing': '1px'}),
            html.P(id='indicator-min', style={'fontSize': '26px', 'fontWeight': 'bold', 'color': '#198754', 'margin': '5px 0 0 0'})
        ], style={
            'flex': '1', 'backgroundColor': COLORS['card_bg'], 
            'padding': '20px', 'borderRadius': '12px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.05)', 
            'textAlign': 'center', 'margin': '0 10px'
        }),
        
        html.Div([
            html.H5("Máximo", style={'color': COLORS['secondary'], 'fontSize': '14px', 'textTransform': 'uppercase', 'letterSpacing': '1px'}),
            html.P(id='indicator-max', style={'fontSize': '26px', 'fontWeight': 'bold', 'color': '#dc3545', 'margin': '5px 0 0 0'})
        ], style={
            'flex': '1', 'backgroundColor': COLORS['card_bg'], 
            'padding': '20px', 'borderRadius': '12px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.05)', 
            'textAlign': 'center', 'margin': '0 10px'
        }),
    ], style={
        'display': 'flex', 
        'justifyContent': 'space-between', 
        'marginBottom': '25px', 
        'maxWidth': '900px', 
        'marginLeft': 'auto', 
        'marginRight': 'auto'
    }),

    # Contenedor del Gráfico Interactivo
    html.Div([
        dcc.Graph(id='live-update-graph')
    ], style={
        'backgroundColor': COLORS['card_bg'],
        'padding': '20px',
        'borderRadius': '12px',
        'boxShadow': '0 4px 6px rgba(0,0,0,0.05)',
        'maxWidth': '900px',
        'marginLeft': 'auto',
        'marginRight': 'auto'
    })
])

# Callback para actualizar las opciones del ID de sensor según el tipo
@app.callback(
    Output('dropdown-sensor-id', 'options'),
    Output('dropdown-sensor-id', 'value'),
    Input('dropdown-type', 'value'),
    Input('interval-component', 'n_intervals')
)
def update_sensor_dropdown(selected_type, n):
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            if df.empty:
                return [], None
            
            df_filtered = df[df['type'] == selected_type]
            sensor_ids = df_filtered['sensor_id'].unique()
            
            options = [{'label': f'Sensor ID: {sid}', 'value': sid} for sid in sensor_ids]
            default_value = sensor_ids[0] if len(sensor_ids) > 0 else None
            return options, default_value
    except Exception as e:
        print(f"Error conectando con la API: {e}")
    return [], None

# Callback principal para actualizar gráfico e indicadores con diseño Plotly mejorado
@app.callback(
    Output('live-update-graph', 'figure'),
    Output('indicator-avg', 'children'),
    Output('indicator-min', 'children'),
    Output('indicator-max', 'children'),
    Input('dropdown-type', 'value'),
    Input('dropdown-sensor-id', 'value'),
    Input('interval-component', 'n_intervals')
)
def update_dashboard(selected_type, selected_sensor_id, n):
    fig = px.line(title="Sin datos disponibles")
    avg_val, min_val, max_val = "N/A", "N/A", "N/A"
    
    if not selected_sensor_id:
        return fig, avg_val, min_val, max_val
        
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            if not df.empty:
                df_filtered = df[(df['type'] == selected_type) & (df['sensor_id'] == selected_sensor_id)]
                
                if not df_filtered.empty:
                    df_filtered['timestamp'] = pd.to_datetime(df_filtered['timestamp'])
                    df_filtered = df_filtered.sort_values('timestamp')
                    
                    avg_val = f"{df_filtered['value'].mean():.2f}"
                    min_val = f"{df_filtered['value'].min():.2f}"
                    max_val = f"{df_filtered['value'].max():.2f}"
                    
                    # Gráfico estilizado con Plotly
                    fig = px.line(
                        df_filtered, 
                        x='timestamp', 
                        y='value', 
                        markers=True,
                        title=f'Comportamiento Histórico - {selected_type.capitalize()} (Sensor #{selected_sensor_id})',
                        labels={'timestamp': 'Fecha y Hora', 'value': f'Valor Medido ({selected_type})'}
                    )
                    
                    # Mejoras estéticas de la gráfica (template limpio y colores)
                    fig.update_traces(
                        line=dict(color='#0d6efd', width=3),
                        marker=dict(size=8, color='#0dcaf0')
                    )
                    fig.update_layout(
                        plot_bgcolor='#ffffff',
                        paper_bgcolor='#ffffff',
                        title_font=dict(size=18, color='#212529', family='Segoe UI'),
                        font=dict(family='Segoe UI', color='#495057'),
                        xaxis=dict(showgrid=True, gridcolor='#f1f3f5'),
                        yaxis=dict(showgrid=True, gridcolor='#f1f3f5'),
                        margin=dict(t=50, l=50, r=30, b=50)
                    )
    except Exception as e:
        print(f"Error actualizando dashboard: {e}")
        
    return fig, avg_val, min_val, max_val

if __name__ == '__main__':
    app.run(debug=True, port=8050)