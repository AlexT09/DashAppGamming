"""
tab_metodologia.py
------------------
Pestaña de Metodología del dashboard PlayStation Gaming Analytics.
"""

import sys, os as _os
sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))


from dash import html
import dash_bootstrap_components as dbc

PS_DARK = "#001A52"
PS_BLUE = "#003087"

CARD_STYLE = {
 "border": "none",
 "borderRadius": "16px",
 "boxShadow": "0 6px 20px rgba(0,26,82,0.10)",
 "backgroundColor": "white",
}

HEADER_STYLE = {
 "background": f"linear-gradient(90deg, {PS_DARK} 0%, {PS_BLUE} 100%)",
 "color": "white",
 "borderTopLeftRadius": "16px",
 "borderTopRightRadius": "16px",
 "borderBottom": "none",
 "padding": "10px 16px",
}


def layout():
 return dbc.Container([

 dbc.Row(dbc.Col([
 html.H4("Metodología", className="fw-bold mt-3 mb-1", style={"color": PS_DARK}),
 html.P("Flujo ETL y decisiones de análisis", className="text-muted-custom lead mb-3"),
 html.Hr(),
 ])),

 # Fuente de datos
 dbc.Card([
 dbc.CardHeader(html.H6("Fuente de datos", className="mb-0 fw-semibold"), style=HEADER_STYLE),
 dbc.CardBody([
 html.P([
 "Dataset: ",
 html.Strong("Gaming Profiles 2025"),
 " — Kruglov, A. (2025). Kaggle, licencia CC0. ",
 "Los archivos utilizados son un snapshot de ",
 html.Strong("febrero 2025"),
 ": no representan una serie temporal sino el estado del mercado en ese momento."
 ], className="mb-0", style={"color": "#6B7A9A"}),
 ])
 ], style=CARD_STYLE, className="mb-4"),

 # Flujo ETL
 dbc.Card([
 dbc.CardHeader(html.H6("Proceso ETL", className="mb-0 fw-semibold"), style=HEADER_STYLE),
 dbc.CardBody([
 dbc.Row([
 dbc.Col(_etl_step(
 "1. Extracción",
 "Carga de games.csv, players.csv y prices.csv desde Kaggle.",
 "#edf6ff"
 ), md=4, className="mb-3"),
 dbc.Col(_etl_step(
 "2. Limpieza de géneros",
 "La columna genres viene en formato lista Python (['Action', 'Indie']). "
 "Se eliminan corchetes y comillas. Se extrae el año de release_date.",
 "#edf6ff"
 ), md=4, className="mb-3"),
 dbc.Col(_etl_step(
 "3. Filtro de precios",
 "Se eliminan precios nulos, cero o mayores a $150 USD. "
 "Esto excluye errores y casos excepcionales no representativos.",
 "#edf6ff"
 ), md=4, className="mb-3"),
 dbc.Col(_etl_step(
 "4. Expansión de géneros",
 "Cada juego con múltiples géneros se expande a una fila por género, "
 "lo que permite comparar precios dentro de cada etiqueta de mercado.",
 "#edf6ff"
 ), md=4, className="mb-3"),
 dbc.Col(_etl_step(
 "5. Filtro de representatividad",
 "Solo se analizan géneros con al menos 50 juegos con precio disponible, "
 "para garantizar que los estadísticos sean robustos.",
 "#edf6ff"
 ), md=4, className="mb-3"),
 dbc.Col(_etl_step(
 "6. Variables derivadas",
 "Se calculan mediana, Q1, Q3, media y desviación estándar "
 "por género y por combinación género × plataforma.",
 "#edf6ff"
 ), md=4, className="mb-3"),
 ])
 ])
 ], style=CARD_STYLE, className="mb-4"),

 # Variables
 dbc.Card([
 dbc.CardHeader(html.H6("Variables utilizadas", className="mb-0 fw-semibold"), style=HEADER_STYLE),
 dbc.CardBody([
 dbc.Row([
 dbc.Col(_var_card("usd", "Precio en dólares", "Variable principal. Snapshot febrero 2025."), md=3, className="mb-3"),
 dbc.Col(_var_card("genres", "Género(s) del juego", "Múltiples valores por juego. Se expande a una fila por género."), md=3, className="mb-3"),
 dbc.Col(_var_card("platform", "Plataforma", "PS3, PS4 o PS5. Permite comparaciones entre generaciones."), md=3, className="mb-3"),
 dbc.Col(_var_card("country", "País del jugador", "Contexto geográfico de la audiencia. No entra al análisis de precios."), md=3, className="mb-3"),
 ]),
 dbc.Alert([
 html.Strong("Nota: "),
 "La expansión multi-género implica que un mismo gameid aparece en varias filas. "
 "Los conteos por género son conteos de etiquetas, no de juegos únicos globales."
 ], color="warning", className="mb-0 mt-2"),
 ])
 ], style=CARD_STYLE, className="mb-4"),

 # Herramientas
 dbc.Card([
 dbc.CardHeader(html.H6("Herramientas utilizadas", className="mb-0 fw-semibold"), style=HEADER_STYLE),
 dbc.CardBody([
 dbc.Row([
 dbc.Col(_tool_card("R / ggplot2", "Visualizaciones estáticas y bookdown reproducible"), md=3, className="mb-3"),
 dbc.Col(_tool_card("R Shiny", "Dashboard interactivo con filtros dinámicos"), md=3, className="mb-3"),
 dbc.Col(_tool_card("Python / Plotly", "Gráficos interactivos para el dashboard Dash"), md=3, className="mb-3"),
 dbc.Col(_tool_card("Python Dash", "App web multipágina con callbacks reactivos"), md=3, className="mb-3"),
 ])
 ])
 ], style=CARD_STYLE, className="mb-5"),

 ], fluid=True)


def _etl_step(title, desc, bg):
 return dbc.Card([
 dbc.CardBody([
 html.H6(title, className="fw-semibold mb-2", style={"color": PS_DARK}),
 html.P(desc, className="small mb-0", style={"color": "#64748b"}),
 ])
 ], style={
 "border": "none", "borderRadius": "14px",
 "backgroundColor": bg,
 "boxShadow": "0 4px 12px rgba(0,26,82,0.07)"
 }, className="h-100")


def _var_card(nombre, titulo, desc):
 return dbc.Card([
 dbc.CardBody([
 dbc.Badge(nombre, color="primary", className="mb-2"),
 html.H6(titulo, className="fw-semibold mb-1", style={"color": PS_DARK}),
 html.P(desc, className="small mb-0", style={"color": "#64748b"}),
 ])
 ], style={
 "border": "none", "borderRadius": "14px",
 "backgroundColor": "#f8fafc",
 "boxShadow": "0 4px 12px rgba(0,26,82,0.07)"
 }, className="h-100")


def _tool_card(nombre, desc):
 return dbc.Card([
 dbc.CardBody([
 html.H6(nombre, className="fw-bold mb-1", style={"color": PS_BLUE}),
 html.P(desc, className="small mb-0", style={"color": "#64748b"}),
 ])
 ], style={
 "border": "none", "borderRadius": "14px",
 "backgroundColor": "#e8f0fe",
 "boxShadow": "0 4px 12px rgba(0,26,82,0.07)"
 }, className="h-100")
