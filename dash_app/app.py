"""
app.py — PS Gaming Analytics 2025 · Dashboard Dash + Plotly.

Visualización del catálogo, precios, jugadores, popularidad y trofeos de
PlayStation Store (dataset Gaming Profiles 2025, Kaggle CC0).

Ejecutar:  python dash_app/app.py   →   http://127.0.0.1:8050
Requiere haber corrido antes el ETL (etl/etl_playstation.py), que deja los
datos limpios en data/processed/.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import dash  # noqa: E402
from dash import Input, Output, dcc, html  # noqa: E402

from data import GENRES, PLATFORMS, YEAR_MAX, YEAR_MIN  # noqa: E402
from pages import (catalogo, etl, explorador, jugadores, logros, popularidad, precios,  # noqa: E402
                   resumen, textos)

app = dash.Dash(
    __name__,
    title="PS Gaming Analytics 2025",
    suppress_callback_exceptions=True,
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap",
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css",
    ],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server

# (ruta, etiqueta, icono, función que arma la página)
MENU = [
    ("Contexto", [
        ("/", "Resumen", "speedometer2", resumen.layout),
        ("/introduccion", "Introducción", "book", textos.introduccion),
        ("/objetivos", "Objetivos", "bullseye", textos.objetivos),
        ("/etl", "ETL", "database-gear", etl.layout),
    ]),
    ("Análisis (EDA)", [
        ("/catalogo", "Catálogo", "grid-3x3-gap", catalogo.layout),
        ("/precios", "Precios", "currency-dollar", precios.layout),
        ("/jugadores", "Jugadores", "people", jugadores.layout),
        ("/popularidad", "Popularidad", "fire", popularidad.layout),
        ("/logros", "Logros", "award", logros.layout),
    ]),
    ("Cierre", [
        ("/explorador", "Explorador", "search", explorador.layout),
        ("/conclusiones", "Conclusiones", "check2-circle", textos.conclusiones),
    ]),
]
ROUTES = {path: fn for _, items in MENU for path, _, _, fn in items}


def sidebar():
    nav = []
    for group, items in MENU:
        nav.append(html.Div(group, className="nav-group-title"))
        nav += [dcc.Link([html.I(className=f"bi bi-{icon}"), label], href=path, id=f"nav-{path.strip('/') or 'inicio'}",
                         className="nav-item") for path, label, icon, _ in items]
    year_marks = {y: {"label": str(y)} for y in range(YEAR_MIN, YEAR_MAX + 1, 4)}
    return html.Div([
        html.Div([
            html.Div(html.I(className="bi bi-playstation"), className="brand-logo"),
            html.Div([html.Div("PS Gaming Analytics", className="brand-title"),
                      html.Div("2025 · Dash", className="brand-sub")]),
        ], className="brand"),
        *nav,
        html.Div("Filtros globales", className="nav-group-title"),
        html.Div([
            html.Label("Plataforma", className="filter-label"),
            dcc.Dropdown(id="f-plat", options=PLATFORMS, value="Todas", clearable=False),
            html.Label("Género principal", className="filter-label"),
            dcc.Dropdown(id="f-genre", options=GENRES, value="Todos", clearable=False),
            html.Label("Año de lanzamiento", className="filter-label"),
            dcc.RangeSlider(id="f-year", min=YEAR_MIN, max=YEAR_MAX, step=1, value=[YEAR_MIN, YEAR_MAX],
                            marks=year_marks, tooltip={"placement": "bottom"}),
            html.P("Aplican a Resumen, Catálogo, Precios, Popularidad, Logros y Explorador.", className="filter-note"),
        ], className="filters"),
        html.Div(["Gaming Profiles 2025 · Kaggle CC0", html.Br(), "Curso de Visualización de Datos"],
                 className="sidebar-footer"),
    ], className="sidebar")


app.layout = html.Div([
    dcc.Location(id="url"),
    html.Div([sidebar(), html.Main(id="page", className="content")], className="app-shell"),
])

NAV_IDS = [f"nav-{p.strip('/') or 'inicio'}" for p in ROUTES]


@app.callback(Output("page", "children"), *[Output(i, "className") for i in NAV_IDS], Input("url", "pathname"))
def route(path):
    path = path if path in ROUTES else "/"
    return (ROUTES[path](), *["nav-item active" if i == f"nav-{path.strip('/') or 'inicio'}" else "nav-item"
                              for i in NAV_IDS])


for page in (resumen, catalogo, precios, popularidad, logros, explorador):
    page.register(app)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    debug = os.environ.get("DASH_DEBUG", "1") == "1"
    print(f"PS Gaming Analytics: http://127.0.0.1:{port}")
    app.run(host="0.0.0.0" if not debug else "127.0.0.1", port=port, debug=debug)
