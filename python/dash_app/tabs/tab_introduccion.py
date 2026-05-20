"""
tab_introduccion.py
-------------------
Pestaña de Introducción del dashboard PlayStation Gaming Analytics.
Pregunta de investigación: ¿Existe asociación entre el género de un juego y su precio en PS Store?
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

 # Título
 dbc.Row(dbc.Col([
 html.H4("Introducción", className="fw-bold mt-3 mb-1", style={"color": PS_DARK}),
 html.P(
 "Análisis exploratorio de precios en el catálogo PlayStation Store (snapshot 2025)",
 className="text-muted-custom lead mb-3"
 ),
 html.Hr(),
 ])),

 # Contexto + Pregunta
 dbc.Row([
 dbc.Col(dbc.Card([
 dbc.CardHeader(html.H6("Contexto", className="mb-0 fw-semibold"), style=HEADER_STYLE),
 dbc.CardBody([
 html.P(
 "El mercado digital de videojuegos en consola ha crecido de forma acelerada. "
 "PlayStation Store concentra decenas de miles de títulos distribuidos en múltiples "
 "géneros y plataformas (PS3, PS4, PS5), con precios que varían considerablemente "
 "entre categorías.",
 className="mb-2", style={"color": "#6B7A9A"}
 ),
 html.P(
 "Este trabajo utiliza el dataset público Gaming Profiles 2025 (Kaggle, CC0) "
 "para explorar si existe una relación entre el género declarado de un juego "
 "y su precio listado en el snapshot de febrero 2025.",
 className="mb-0", style={"color": "#6B7A9A"}
 ),
 ])
 ], style=CARD_STYLE), md=6, className="mb-4"),

 dbc.Col(dbc.Card([
 dbc.CardHeader(html.H6("Pregunta de investigación", className="mb-0 fw-semibold"), style=HEADER_STYLE),
 dbc.CardBody([
 dbc.Alert(
 "¿Existe una asociación entre el género declarado de un juego y el precio "
 "listado en PlayStation Store (snapshot 2025)?",
 color="primary", className="fw-semibold mb-3"
 ),
 html.P("Subpreguntas:", className="fw-semibold mb-2", style={"color": PS_DARK}),
 html.Ol([
 html.Li("¿Qué géneros muestran medianas de precio más altas o más bajas?", className="mb-1"),
 html.Li("¿Cómo se relaciona el volumen de títulos por género con la mediana de precio?", className="mb-1"),
 html.Li("¿Se observan diferencias entre PS4 y PS5 dentro del mismo género?"),
 ], style={"color": "#6B7A9A", "paddingLeft": "20px"}),
 ])
 ], style=CARD_STYLE), md=6, className="mb-4"),
 ]),

 # Datos usados
 dbc.Card([
 dbc.CardHeader(html.H6("Dataset: Gaming Profiles 2025 — PlayStation", className="mb-0 fw-semibold"), style=HEADER_STYLE),
 dbc.CardBody([
 html.P([
 "Fuente: Kruglov, A. (2025). ",
 html.Em("Gaming Profiles 2025 (Steam, PlayStation, Xbox)"),
 ". Kaggle — licencia CC0 (dominio público)."
 ], className="mb-3", style={"color": "#6B7A9A"}),
 dbc.Row([
 dbc.Col(_data_card("games.csv", "23 152 juegos", "title, platform, genres, release_date", "#e8f0fe"), md=4, className="mb-3"),
 dbc.Col(_data_card("players.csv", "356 600 jugadores", "playerid, nickname, country", "#e8f0fe"), md=4, className="mb-3"),
 dbc.Col(_data_card("prices.csv", "62 816 precios", "gameid, usd, eur, gbp, jpy, rub, date_acquired", "#e8f0fe"), md=4, className="mb-3"),
 ]),
 ])
 ], style=CARD_STYLE, className="mb-4"),

 # Flujo del proyecto
 dbc.Card([
 dbc.CardHeader(html.H6("Flujo del proyecto", className="mb-0 fw-semibold"), style=HEADER_STYLE),
 dbc.CardBody([
 dbc.Row([
 dbc.Col(_step(1, "Datos", "Carga de games, players y prices desde CSV (Kaggle CC0)", "#003087"), md=2, className="mb-3"),
 dbc.Col(_step(2, "ETL", "Limpieza de géneros, filtro de precios, expansión por género", "#0055b3"), md=2, className="mb-3"),
 dbc.Col(_step(3, "EDA", "Distribuciones, outliers, comparaciones PS4 vs PS5", "#0070CC"), md=2, className="mb-3"),
 dbc.Col(_step(4, "Visualización R", "ggplot2 estático + Shiny interactivo", "#4D9AC2"), md=2, className="mb-3"),
 dbc.Col(_step(5, "Visualización Python", "Plotly + Dash multipágina", "#A8DADC"), md=2, className="mb-3"),
 dbc.Col(_step(6, "Conclusiones", "Hallazgos sobre géneros y precios en PS Store", "#F4A261"), md=2, className="mb-3"),
 ], className="g-3")
 ])
 ], style=CARD_STYLE, className="mb-5"),

 ], fluid=True)


def _data_card(archivo, registros, columnas, bg):
 return dbc.Card([
 dbc.CardBody([
 html.H6(archivo, className="fw-bold mb-1", style={"color": PS_DARK}),
 html.P(registros, className="fw-semibold mb-1", style={"color": PS_BLUE}),
 html.P(columnas, className="small mb-0", style={"color": "#64748b"}),
 ])
 ], style={
 "border": "none", "borderRadius": "14px",
 "backgroundColor": bg,
 "boxShadow": "0 4px 12px rgba(0,26,82,0.07)"
 })


def _step(num, title, desc, color):
 return dbc.Card([
 dbc.CardBody([
 html.Div(str(num), className="fw-bold text-center mb-1",
 style={"fontSize": "2rem", "color": color}),
 html.H6(title, className="text-center fw-semibold", style={"color": PS_DARK}),
 html.P(desc, className="small text-center mb-0", style={"color": "#64748b"}),
 ])
 ], style={
 "border": "none", "borderRadius": "14px",
 "backgroundColor": "#f8fafc",
 "boxShadow": "0 4px 12px rgba(0,26,82,0.06)",
 "borderTop": f"4px solid {color}"
 }, className="h-100")
