"""
tab_objetivos.py
----------------
Pestaña de Objetivos del dashboard PlayStation Gaming Analytics.
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
 html.H4("Objetivos", className="fw-bold mt-3 mb-1", style={"color": PS_DARK}),
 html.P("Metas del análisis de precios en el catálogo PlayStation", className="text-muted-custom lead mb-3"),
 html.Hr(),
 ])),

 # Objetivo general
 dbc.Card([
 dbc.CardHeader(html.H6("Objetivo general", className="mb-0 fw-semibold"), style=HEADER_STYLE),
 dbc.CardBody([
 html.P(
 "Describir la distribución de precios del catálogo PlayStation Store (2025) "
 "y comparar patrones entre géneros y plataformas mediante gráficos reproducibles "
 "en R (ggplot2 / Shiny) y Python (Plotly / Dash).",
 className="mb-0 fs-6", style={"color": "#2d3748"}
 )
 ])
 ], style=CARD_STYLE, className="mb-4"),

 # Objetivos específicos
 dbc.Card([
 dbc.CardHeader(html.H6("Objetivos específicos", className="mb-0 fw-semibold"), style=HEADER_STYLE),
 dbc.CardBody([
 dbc.Row([
 dbc.Col(_obj_card(
 "1", "ETL reproducible",
 "Aplicar un flujo de limpieza transparente: normalización de géneros en formato lista Python, "
 "filtro de precios válidos (USD > 0 y < 150) y expansión por género para análisis comparativo.",
 "#e8f0fe"
 ), md=6, className="mb-3"),
 dbc.Col(_obj_card(
 "2", "Visualizaciones estáticas",
 "Producir gráficos con ggplot2 (R) y Plotly (Python) que muestren distribuciones, "
 "medianas por género, comparaciones PS4 vs PS5 y detección de outliers.",
 "#e8f0fe"
 ), md=6, className="mb-3"),
 dbc.Col(_obj_card(
 "3", "Dashboards interactivos",
 "Construir una app Shiny (R) y un dashboard Dash (Python) con filtros por plataforma "
 "y año, que permitan explorar el catálogo y visualizar la distribución de precios.",
 "#e8f0fe"
 ), md=6, className="mb-3"),
 dbc.Col(_obj_card(
 "4", "Simulador y modelos predictivos",
 "Implementar un simulador descriptivo (Q1–Q3 por género) y modelos de ML "
 "(Lasso, Random Forest, XGBoost) para predecir el precio de un juego según sus características.",
 "#e8f0fe"
 ), md=6, className="mb-3"),
 ])
 ])
 ], style=CARD_STYLE, className="mb-4"),

 # Justificación
 dbc.Card([
 dbc.CardHeader(html.H6("Justificación", className="mb-0 fw-semibold"), style=HEADER_STYLE),
 dbc.CardBody([
 dbc.Row([
 dbc.Col(_just_card(
 "¿Por qué videojuegos?",
 "El mercado de juegos digitales genera miles de millones anuales. "
 "Comprender cómo se distribuyen los precios por género tiene valor práctico "
 "para desarrolladores y consumidores.",
 ), md=4, className="mb-3"),
 dbc.Col(_just_card(
 "¿Por qué PlayStation?",
 "PS Store es una de las tiendas digitales más grandes del mundo. "
 "El dataset de Kaggle ofrece un snapshot real de precios en 5 monedas, "
 "ideal para un análisis exploratorio del curso.",
 ), md=4, className="mb-3"),
 dbc.Col(_just_card(
 "Alcance del trabajo",
 "El análisis combina técnicas descriptivas y modelos predictivos (Lasso, "
 "Random Forest, XGBoost), alineados con los módulos del curso de Visualización "
 "de Datos en R y Python.",
 ), md=4, className="mb-3"),
 ])
 ])
 ], style=CARD_STYLE, className="mb-5"),

 ], fluid=True)


def _obj_card(num, title, desc, bg):
 return dbc.Card([
 dbc.CardBody([
 dbc.Row([
 dbc.Col(
 html.Div(num, className="fw-bold text-center",
 style={"fontSize": "2rem", "color": PS_BLUE}),
 width=2
 ),
 dbc.Col([
 html.H6(title, className="fw-bold mb-1", style={"color": PS_DARK}),
 html.P(desc, className="small mb-0", style={"color": "#64748b"}),
 ], width=10),
 ], align="center")
 ])
 ], style={
 "border": "none", "borderRadius": "14px",
 "backgroundColor": bg,
 "boxShadow": "0 4px 12px rgba(0,26,82,0.07)"
 })


def _just_card(title, desc):
 return dbc.Card([
 dbc.CardBody([
 html.H6(title, className="fw-bold mb-2", style={"color": PS_DARK}),
 html.P(desc, className="small mb-0", style={"color": "#64748b"}),
 ])
 ], style={
 "border": "none", "borderRadius": "14px",
 "backgroundColor": "#f8fafc",
 "boxShadow": "0 4px 12px rgba(0,26,82,0.07)"
 }, className="h-100")
