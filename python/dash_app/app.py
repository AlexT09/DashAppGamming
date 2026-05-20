"""
app.py — PlayStation Gaming Analytics 2025
Dashboard Dash + Plotly · Diseño dark pro enterprise

Ejecutar: python app.py → http://127.0.0.1:8050
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dash import Input, Output, dash_table, dcc, html, callback
import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from tabs import tab_introduccion, tab_objetivos, tab_metodologia, tab_modelos, tab_prediccion
from data import (
 MED_PRICE, MISSINGNESS_DF, N_COUNTRIES, N_GAMES, N_PLAYERS,
 PLATFORMS, YEARS, filter_games, format_benchmark_md, games,
 GENRES_LIST, players, precio_genero_for_subset,
 precio_gen_plat_for_subset, pricing_benchmark, prices,
 price_daily_for_games, price_dispersion_for_subset,
)

# 
# PALETA & TEMA
# 
PS_BLUE = "#0070D1"
PS_DARK = "#00265F"
PS_DARKER = "#0A0F1E"
PS_ACCENT = "#00AAFF"
PS_SIDEBAR= "#0D1426"
PS_CARD = "#111827"
PS_BORDER = "#1E2D4A"
PS_MUTED = "#8B9BB4"
PS_TEXT = "#F0F4FF"
PS_GREEN = "#22C55E"
PS_AMBER = "#F59E0B"
PS_RED = "#EF4444"

PLOTLY_TEMPLATE = dict(
 layout=dict(
 font = dict(family="Inter, Segoe UI, Arial, sans-serif", size=12, color=PS_MUTED),
 paper_bgcolor = "rgba(0,0,0,0)",
 plot_bgcolor = "rgba(0,0,0,0)",
 title = dict(font=dict(color=PS_TEXT, size=14), x=0.01),
 xaxis = dict(gridcolor=PS_BORDER, linecolor=PS_BORDER,
 tickfont=dict(color=PS_MUTED), showgrid=True),
 yaxis = dict(gridcolor=PS_BORDER, linecolor=PS_BORDER,
 tickfont=dict(color=PS_MUTED), showgrid=True),
 colorway = [PS_BLUE, PS_ACCENT, PS_GREEN, PS_AMBER, PS_RED,
 "#A78BFA", "#34D399", "#F472B6"],
 legend = dict(font=dict(color=PS_MUTED), bgcolor="rgba(0,0,0,0)"),
 margin = dict(l=10, r=10, t=40, b=30),
 )
)

# 
# APP
# 
app = dash.Dash(
 __name__,
 external_stylesheets=[
 dbc.themes.BOOTSTRAP,
 "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
 "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css",
 ],
 title = "PS Gaming Analytics 2025",
 suppress_callback_exceptions = True,
 meta_tags = [{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server

_SIM_PLAT = "PS5" if "PS5" in PLATFORMS else (PLATFORMS[1] if len(PLATFORMS) > 1 else "Todas")


# 
# HELPERS UI
# 
def ps_card(header_icon, header_title, body_content, header_color=PS_BLUE):
 return html.Div([
 html.Div([
 html.I(className=f"bi bi-{header_icon}",
 style={"color": header_color, "fontSize": "15px"}),
 html.Span(header_title, style={"fontSize": "13px", "fontWeight": "600",
 "color": PS_TEXT})
 ], className="ps-card-header"),
 html.Div(body_content, className="ps-card-body"),
 ], className="ps-card")


def kpi_box(label, value, sub=None, icon="bar-chart", color=PS_BLUE):
 return html.Div([
 html.Div(label, className="kpi-label"),
 html.Div(value, className="kpi-value"),
 html.Div(sub, className="kpi-sub") if sub else None,
 html.I(className="kpi-icon",
 style={"position": "absolute", "right": "14px", "top": "50%",
 "transform": "translateY(-50%)", "fontSize": "28px",
 "opacity": ".12", "color": color}),
 ], className="kpi-box", style={"--kpi-color": color})


def section_header(title, subtitle=None, icon=None):
 return html.Div([
 html.I(className=f"bi bi-{icon}", style={"fontSize": "20px", "color": PS_BLUE})
 if icon else None,
 html.Div([
 html.H4(title, style={"fontSize": "18px", "fontWeight": "700",
 "color": PS_TEXT, "margin": "0"}),
 html.P(subtitle, style={"fontSize": "13px", "color": PS_MUTED,
 "margin": "2px 0 0"}) if subtitle else None,
 ])
 ], className="section-header")


def graph_card(icon, title, graph_id, height="320px", color=PS_BLUE):
 return ps_card(icon, title,
 dcc.Graph(id=graph_id, style={"height": height},
 config={"displayModeBar": False}),
 header_color=color
 )


# 
# KPIs
# 
KPI_ROW = html.Div([
 kpi_box("Juegos en catálogo", f"{N_GAMES:,}", "PS4 + PS5", "controller", PS_BLUE),
 kpi_box("Jugadores", f"{N_PLAYERS:,}", "registrados", "people-fill", "#22C55E"),
 kpi_box("Países", f"{N_COUNTRIES}", "globales", "globe2", "#A78BFA"),
 kpi_box("Precio mediano", f"${MED_PRICE:.2f}", "USD feb 2025","currency-dollar", PS_AMBER),
], className="kpi-grid")

# 
# SIDEBAR
# 
SIDEBAR = html.Div([
 # Logo
 html.Div([
 html.Div([
 html.Img(
 src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Playstation_logo_colour.svg/60px-Playstation_logo_colour.svg.png",
 style={"height": "22px"}
 ),
 html.Div([
 html.Div("PS Analytics", style={"fontSize": "13px", "fontWeight": "700",
 "color": PS_TEXT}),
 html.Div("2025 · Grupo 13", style={"fontSize": "11px", "color": PS_MUTED}),
 ], style={"marginLeft": "8px"})
 ], style={"display": "flex", "alignItems": "center", "padding": "18px 16px 14px"}),
 html.Hr(style={"borderColor": PS_BORDER, "margin": "0"}),
 ]),

 # Nav contexto
 html.Div("Contexto", className="sidebar-section"),
 dbc.Nav([
 dbc.NavLink([html.I(className="bi bi-book me-2"), "Introducción"],
 href="/introduccion", active="exact"),
 dbc.NavLink([html.I(className="bi bi-bullseye me-2"), "Objetivos"],
 href="/objetivos", active="exact"),
 dbc.NavLink([html.I(className="bi bi-diagram-3 me-2"), "Metodología"],
 href="/metodologia", active="exact"),
 ], vertical=True, pills=True, style={"padding": "0 8px"}),

 html.Hr(style={"borderColor": PS_BORDER, "margin": "8px 0"}),

 # Nav análisis
 html.Div("Análisis", className="sidebar-section"),
 dbc.Nav([
 dbc.NavLink([html.I(className="bi bi-speedometer2 me-2"), "Resumen"],
 href="/", active="exact"),
 dbc.NavLink([html.I(className="bi bi-bar-chart-line me-2"), "EDA / Precios"],
 href="/eda", active="exact"),
 dbc.NavLink([html.I(className="bi bi-sliders me-2"), "Simulador"],
 href="/simulador", active="exact"),
 dbc.NavLink([html.I(className="bi bi-search me-2"), "Explorador"],
 href="/explorador", active="exact"),
 ], vertical=True, pills=True, style={"padding": "0 8px"}),

 html.Hr(style={"borderColor": PS_BORDER, "margin": "8px 0"}),

 # Nav modelos
 html.Div("Modelos ML", className="sidebar-section"),
 dbc.Nav([
 dbc.NavLink([html.I(className="bi bi-cpu me-2"), "Métricas"],
 href="/modelos", active="exact"),
 dbc.NavLink([html.I(className="bi bi-lightning-charge me-2"), "Predictor"],
 href="/prediccion", active="exact"),
 ], vertical=True, pills=True, style={"padding": "0 8px"}),

 html.Hr(style={"borderColor": PS_BORDER, "margin": "8px 0"}),

 # Filtros
 html.Div("Filtros globales", className="sidebar-section"),
 html.Div([
 html.Label("Plataforma", style={"fontSize": "12px", "color": PS_MUTED,
 "marginBottom": "4px"}),
 dcc.Dropdown(
 id="f_plat",
 options=[{"label": p, "value": p} for p in PLATFORMS],
 value="Todas",
 style={"background": PS_SIDEBAR, "color": PS_TEXT,
 "border": f"1px solid {PS_BORDER}", "borderRadius": "8px",
 "fontSize": "12px"},
 ),
 html.Label("Año de lanzamiento",
 style={"fontSize": "12px", "color": PS_MUTED,
 "marginTop": "12px", "marginBottom": "4px"}),
 dcc.RangeSlider(
 id="f_year",
 min=max(2010, min(YEARS) if YEARS else 2010),
 max=min(2024, max(YEARS) if YEARS else 2024),
 value=[2015, 2024],
 marks={y: {"label": str(y), "style": {"color": PS_MUTED, "fontSize": "10px"}}
 for y in range(2010, 2025, 4)},
 ),
 ], style={"padding": "4px 14px 16px"}),

 # Footer
 html.Div([
 html.Hr(style={"borderColor": PS_BORDER}),
 html.P("Ciencia de Datos · Grupo 13",
 style={"fontSize": "11px", "color": PS_MUTED, "margin": "0",
 "textAlign": "center"}),
 html.P("Gaming Profiles 2025 · Kaggle CC0",
 style={"fontSize": "10px", "color": "#4B5A72", "margin": "2px 0 0",
 "textAlign": "center"}),
 ], style={"padding": "0 14px 16px"}),
], id="sidebar", style={"width": "220px", "minWidth": "220px", "flexShrink": "0"})

# 
# PÁGINAS
# 
def PAGE_RESUMEN():
 return html.Div([
 section_header("Resumen ejecutivo",
 "Vista general del catálogo PlayStation Store 2025",
 "speedometer2"),
 KPI_ROW,
 dbc.Row([
 dbc.Col(graph_card("pie-chart-fill", "Juegos por plataforma",
 "g-plataforma", "280px"), md=5),
 dbc.Col(graph_card("graph-up", "Lanzamientos por año",
 "g-anios", "280px", PS_GREEN), md=7),
 ]),
 dbc.Row([
 dbc.Col(graph_card("geo-alt-fill", "Top 10 países — jugadores",
 "g-paises", "280px", "#A78BFA"), md=6),
 dbc.Col(
 ps_card("lightbulb-fill", "Insights clave", html.Div([
 html.Div([html.Strong("PS4 domina: "), "61% del catálogo (14,163 juegos)."],
 className="insight-box"),
 html.Div([html.Strong("Crecimiento: "), "+1,570% lanzamientos (2013→2024)."],
 className="insight-box"),
 html.Div([html.Strong("Accesible: "), "86% de juegos < $20 · mediana $7.99."],
 className="insight-box"),
 html.Div([html.Strong("EE.UU. + Europa: "), "59% de jugadores globales."],
 className="insight-box"),
 html.Div([html.Strong("Motor indie: "), "eastasiasoft, Ratalaika, ThiGames."],
 className="insight-box"),
 ]), header_color=PS_AMBER),
 md=6,
 ),
 ]),
 dbc.Row([
 dbc.Col(graph_card("tags-fill", "Géneros: caros vs baratos",
 "g-generos-kpi", "340px"), md=12),
 ]),
 dbc.Row([
 dbc.Col(graph_card("clipboard-data", "Calidad de datos — % NA en CSVs crudos",
 "g-missingness", "320px", PS_AMBER), md=12),
 ]),
 ])


def PAGE_EDA():
 return html.Div([
 section_header("EDA — Catálogo y precios",
 "Análisis exploratorio completo", "bar-chart-line"),
 dbc.Row([
 dbc.Col(graph_card("cash-stack", "Precio mediano por género (top 25)",
 "g-precio-genero", "420px"), md=7),
 dbc.Col(graph_card("scatter-chart", "Volumen vs precio mediano",
 "g-volumen-precio", "420px", PS_AMBER), md=5),
 ]),
 dbc.Row([
 dbc.Col(graph_card("controller", "PS4 vs PS5 por género",
 "g-ps4-ps5", "360px", PS_GREEN), md=12),
 ]),
 dbc.Row([
 dbc.Col(graph_card("bar-chart", "Distribución de precios (USD)",
 "g-hist-precios", "360px"), md=7),
 dbc.Col(graph_card("distribute-vertical", "Violin — precio por plataforma",
 "g-violin-plat", "360px", "#A78BFA"), md=5),
 ]),
 dbc.Row([
 dbc.Col(graph_card("percent", "Dispersión de precios por género (CV)",
 "g-dispersión-genero", "340px", PS_RED), md=12),
 ]),
 dbc.Row([
 dbc.Col(graph_card("box", "Boxplot por plataforma",
 "g-boxplot-plat", "280px"), md=6),
 dbc.Col(graph_card("grid-3x3", "Correlación entre monedas",
 "g-corr-monedas", "280px", PS_AMBER), md=6),
 ]),
 dbc.Row([
 dbc.Col(graph_card("activity", "Serie temporal — precio medio catálogo",
 "g-precio-temporal", "300px"), md=12),
 ]),
 ])


def PAGE_SIMULADOR():
 return html.Div([
 section_header("Simulador de precio de referencia",
 "Benchmark descriptivo por género · sin ML", "sliders"),
 dbc.Row([
 dbc.Col(
 ps_card("sliders", "Entradas", html.Div([
 html.Label("Género declarado",
 style={"fontSize": "12px", "color": PS_MUTED,
 "marginBottom": "4px"}),
 dcc.Dropdown(
 id="sim-genre",
 options=[{"label": g, "value": g} for g in GENRES_LIST],
 value=GENRES_LIST[0] if GENRES_LIST else None,
 style={"background": PS_SIDEBAR, "fontSize": "13px"},
 ),
 html.Label("Plataforma objetivo",
 style={"fontSize": "12px", "color": PS_MUTED,
 "marginTop": "12px", "marginBottom": "4px"}),
 dcc.Dropdown(
 id="sim-platform",
 options=[{"label": p, "value": p} for p in PLATFORMS],
 value=_SIM_PLAT,
 style={"background": PS_SIDEBAR, "fontSize": "13px"},
 ),
 html.P("'Todas' agrega todas las plataformas. Estadísticos descriptivos del catálogo (feb. 2025), sin ML.",
 style={"fontSize": "11px", "color": "#4B5A72",
 "marginTop": "12px"}),
 ]), PS_AMBER),
 md=4,
 ),
 dbc.Col(
 ps_card("graph-up-arrow", "Benchmark de mercado",
 html.Div(id="sim-output")),
 md=8,
 ),
 ]),
 ])


def PAGE_EXPLORADOR():
 return html.Div([
 section_header("Explorador de datos",
 "Filtrado interactivo del catálogo completo", "search"),
 ps_card("funnel", "Filtros de búsqueda", dbc.Row([
 dbc.Col([
 html.Label("Precio USD", style={"fontSize": "12px", "color": PS_MUTED}),
 dcc.RangeSlider(id="exp-precio", min=0, max=70, value=[0, 70],
 marks={0: "$0", 20: "$20", 40: "$40", 70: "$70"},
 tooltip={"placement": "bottom"}),
 ], md=4),
 dbc.Col([
 html.Label("Plataforma", style={"fontSize": "12px", "color": PS_MUTED}),
 dcc.Dropdown(id="exp-plat",
 options=[{"label": p, "value": p} for p in PLATFORMS],
 value="Todas", style={"background": PS_SIDEBAR}),
 ], md=3),
 dbc.Col([
 html.Label("Género", style={"fontSize": "12px", "color": PS_MUTED}),
 dcc.Dropdown(
 id="exp-genero",
 options=[{"label": "Todos", "value": "Todos"}] +
 [{"label": g, "value": g} for g in GENRES_LIST],
 value="Todos", style={"background": PS_SIDEBAR}),
 ], md=4),
 dbc.Col([
 dbc.Button([html.I(className="bi bi-arrow-counterclockwise me-1"), "Reset"],
 id="btn-reset", size="sm",
 style={"background": PS_BORDER, "border": "none",
 "color": PS_TEXT, "marginTop": "20px",
 "borderRadius": "8px"}),
 ], md=1),
 ])),
 html.Div(id="exp-count",
 style={"fontSize": "12px", "color": PS_MUTED, "margin": "8px 0 4px"}),
 ps_card("table", "Resultados filtrados",
 dash_table.DataTable(
 id="tabla-explorador",
 columns=[
 {"name": "Título", "id": "title"},
 {"name": "Plataforma", "id": "platform"},
 {"name": "Géneros", "id": "genres_clean"},
 {"name": "USD", "id": "usd", "type": "numeric",
 "format": {"specifier": "$.2f"}},
 ],
 page_size=12,
 filter_action="native",
 style_cell={"fontSize": "12px", "padding": "8px 12px",
 "background": PS_CARD, "color": PS_TEXT,
 "border": f"1px solid {PS_BORDER}"},
 style_header={"background": "#0D1426", "color": PS_MUTED,
 "fontWeight": "600", "fontSize": "11px",
 "textTransform": "uppercase", "letterSpacing": ".06em"},
 style_data_conditional=[
 {"if": {"state": "selected"},
 "background": PS_BORDER, "color": PS_TEXT},
 ],
 )
 ),
 ])


# 
# LAYOUT PRINCIPAL
# 
app.layout = html.Div([
 dcc.Location(id="url"),
 html.Div([
 SIDEBAR,
 html.Div(id="content", style={"flex": "1", "minWidth": "0"}),
 ], style={"display": "flex", "minHeight": "100vh"}),
])

# 
# ROUTING
# 
def _route(path):
 routes = {
 "/introduccion": tab_introduccion.layout(),
 "/objetivos": tab_objetivos.layout(),
 "/metodologia": tab_metodologia.layout(),
 "/modelos": tab_modelos.create_layout(),
 "/prediccion": tab_prediccion.create_layout(),
 "/eda": PAGE_EDA(),
 "/simulador": PAGE_SIMULADOR(),
 "/explorador": PAGE_EXPLORADOR(),
 "/": PAGE_RESUMEN(),
 }
 return routes.get(path or "/", PAGE_RESUMEN())


@app.callback(Output("content", "children"), Input("url", "pathname"))
def render_page(path):
 return _route(path)

# 
# HELPERS PLOTLY
# 
def apply_template(fig, title=None):
 fig.update_layout(
 **PLOTLY_TEMPLATE["layout"],
 title_text=title or "",
 )
 return fig

# 
# CALLBACKS — RESUMEN
# 
@app.callback(Output("g-plataforma", "figure"),
 Input("f_plat", "value"), Input("f_year", "value"))
def cb_plat(plat, years):
 df = filter_games(plat, years).groupby("platform").size().reset_index(name="n").sort_values("n")
 fig = px.bar(df, x="n", y="platform", orientation="h",
 color_discrete_sequence=[PS_BLUE], text="n")
 fig.update_traces(textfont_color=PS_TEXT, textposition="outside")
 return apply_template(fig, "Juegos por plataforma")


@app.callback(Output("g-anios", "figure"),
 Input("f_plat", "value"), Input("f_year", "value"))
def cb_anios(plat, years):
 df = filter_games(plat, years).dropna(subset=["year"]).groupby("year").size().reset_index(name="n")
 fig = go.Figure(go.Scatter(
 x=df["year"], y=df["n"],
 fill="tozeroy",
 line=dict(color=PS_GREEN, width=2),
 fillcolor="rgba(34,197,94,0.13)",
 mode="lines+markers",
 marker=dict(color=PS_GREEN, size=4),
 ))
 return apply_template(fig, "Lanzamientos por año")


@app.callback(Output("g-generos-kpi", "figure"),
 Input("f_plat", "value"), Input("f_year", "value"))
def cb_gen_kpi(p, y):
 pg = precio_genero_for_subset(filter_games(p, y))
 if pg.empty or len(pg) < 2:
 return go.Figure().update_layout(**PLOTLY_TEMPLATE["layout"])
 n = min(8, len(pg))
 top_c = pg.nlargest(n, "precio_mediana").assign(t="Precio alto")
 top_b = pg.nsmallest(n, "precio_mediana").assign(t="Precio bajo")
 df = pd.concat([top_c, top_b])
 fig = px.bar(df, x="precio_mediana", y="genre", color="t",
 orientation="h", barmode="group",
 color_discrete_map={"Precio alto": PS_BLUE, "Precio bajo": "#A78BFA"})
 return apply_template(fig, "Géneros caros vs baratos")


@app.callback(Output("g-paises", "figure"), Input("f_year", "value"))
def cb_paises(_):
 df = players["country"].value_counts().head(15).reset_index()
 df.columns = ["country", "n"]
 fig = px.bar(df, x="n", y="country", orientation="h",
 color_discrete_sequence=["#A78BFA"], text="n")
 fig.update_traces(textfont_color=PS_TEXT, textposition="outside")
 return apply_template(fig, "Top 15 países — jugadores")


@app.callback(Output("g-missingness", "figure"), Input("url", "pathname"))
def cb_miss(_):
 df = MISSINGNESS_DF.copy()
 df["lab"] = df["dataset"] + ": " + df["column"]
 colors = {"games": PS_BLUE, "players": PS_GREEN, "prices": PS_AMBER}
 fig = px.bar(df, x="missing_pct", y="lab", color="dataset", orientation="h",
 color_discrete_map=colors)
 return apply_template(fig, "% NA en CSVs crudos (calidad de datos)")


# 
# CALLBACKS — EDA
# 
@app.callback(Output("g-precio-genero", "figure"),
 Input("f_plat", "value"), Input("f_year", "value"))
def cb_pg(p, y):
 pg = precio_genero_for_subset(filter_games(p, y))
 if pg.empty:
 return go.Figure().update_layout(**PLOTLY_TEMPLATE["layout"])
 df = pg.nlargest(min(25, len(pg)), "precio_mediana")
 fig = px.bar(df, x="precio_mediana", y="genre", orientation="h",
 color="precio_mediana",
 color_continuous_scale=[[0, "#1E2D4A"], [0.5, PS_BLUE], [1, PS_ACCENT]],
 text=df["precio_mediana"].apply(lambda v: f"${v:.2f}"))
 fig.update_traces(textfont_color=PS_TEXT, textposition="outside")
 fig.update_layout(coloraxis_showscale=False, showlegend=False)
 return apply_template(fig, "Precio mediano por género (top 25)")


@app.callback(Output("g-volumen-precio", "figure"),
 Input("f_plat", "value"), Input("f_year", "value"))
def cb_vol(p, y):
 df = precio_genero_for_subset(filter_games(p, y))
 if df.empty or len(df) < 3:
 return go.Figure().update_layout(**PLOTLY_TEMPLATE["layout"])
 fig = px.scatter(df, x="n", y="precio_mediana", text="genre", log_x=True,
 color="precio_mediana",
 size=df["precio_sd"].fillna(1).clip(0.5, 50),
 color_continuous_scale=[[0, "#1E2D4A"], [1, PS_ACCENT]])
 try:
 fig.add_traces(
 px.scatter(df, x="n", y="precio_mediana", trendline="ols", log_x=True).data[1]
 )
 except Exception:
 pass
 fig.update_layout(coloraxis_showscale=False, showlegend=False)
 return apply_template(fig, "Volumen vs precio mediano")


@app.callback(Output("g-ps4-ps5", "figure"),
 Input("f_plat", "value"), Input("f_year", "value"))
def cb_ps(p, y):
 gf = filter_games(p, y)
 pg = precio_genero_for_subset(gf)
 gp = precio_gen_plat_for_subset(gf)
 if pg.empty or gp.empty:
 return go.Figure().update_layout(**PLOTLY_TEMPLATE["layout"])
 top_genres = set(pg.nlargest(15, "precio_mediana")["genre"])
 df = gp[gp["genre"].isin(top_genres)]
 if df.empty:
 return go.Figure().update_layout(**PLOTLY_TEMPLATE["layout"])
 fig = px.bar(df, x="mediana", y="genre", color="platform", orientation="h",
 barmode="group",
 color_discrete_map={"PS4": PS_BLUE, "PS5": PS_ACCENT})
 return apply_template(fig, "PS4 vs PS5 — precio mediano por género")


@app.callback(Output("g-hist-precios", "figure"),
 Input("f_plat", "value"), Input("f_year", "value"))
def cb_hist(plat, years):
 gf = filter_games(plat, years)
 pr = prices[prices["gameid"].isin(gf["gameid"]) & (prices["usd"] <= 75)]
 fig = go.Figure(go.Histogram(x=pr["usd"], nbinsx=28,
 marker_color=PS_BLUE, opacity=0.85))
 med = pr["usd"].median()
 avg = pr["usd"].mean()
 fig.add_vline(x=med, line_dash="dash", line_color=PS_RED,
 annotation_text=f"Mediana ${med:.2f}",
 annotation_font_color=PS_RED)
 fig.add_vline(x=avg, line_dash="dot", line_color=PS_AMBER,
 annotation_text=f"Media ${avg:.2f}",
 annotation_font_color=PS_AMBER,
 annotation_position="top left")
 fig.update_layout(showlegend=False)
 return apply_template(fig, "Distribución de precios (USD)")


@app.callback(Output("g-violin-plat", "figure"),
 Input("f_plat", "value"), Input("f_year", "value"))
def cb_violin(plat, years):
 gf = filter_games(plat, years)
 df = gf.merge(prices[["gameid", "usd"]], on="gameid")
 df = df[df["platform"].isin(["PS3","PS4","PS5"]) & (df["usd"] <= 70)]
 if df.empty:
 return go.Figure().update_layout(**PLOTLY_TEMPLATE["layout"])
 fig = px.violin(df, x="platform", y="usd", color="platform", box=True, points=False,
 color_discrete_map={"PS3": "#4B5A72", "PS4": PS_BLUE, "PS5": PS_ACCENT})
 fig.update_layout(showlegend=False)
 return apply_template(fig, "Distribución de precios por plataforma (violin)")


@app.callback(Output("g-dispersión-genero", "figure"),
 Input("f_plat", "value"), Input("f_year", "value"))
def cb_disp(p, y):
 df = price_dispersion_for_subset(filter_games(p, y)).head(20)
 if df.empty:
 return go.Figure().update_layout(**PLOTLY_TEMPLATE["layout"])
 df["cv"] = (df["std"] / df["media"]).replace(0, np.nan).fillna(0)
 fig = px.bar(df, x="cv", y="genre", orientation="h",
 color="cv",
 color_continuous_scale=[[0, "#1E2D4A"], [0.5, PS_BLUE], [1, PS_RED]])
 fig.update_layout(coloraxis_showscale=False, showlegend=False)
 return apply_template(fig, "Variabilidad de precios por género (Coef. Variación)")


@app.callback(Output("g-boxplot-plat", "figure"),
 Input("f_plat", "value"), Input("f_year", "value"))
def cb_box(plat, years):
 gf = filter_games(plat, years)
 df = gf.merge(prices[["gameid", "usd"]], on="gameid")
 df = df[df["platform"].isin(["PS3","PS4","PS5"]) & (df["usd"] <= 70)]
 if df.empty:
 return go.Figure().update_layout(**PLOTLY_TEMPLATE["layout"])
 fig = px.box(df, x="platform", y="usd", color="platform",
 color_discrete_map={"PS3": "#4B5A72", "PS4": PS_BLUE, "PS5": PS_ACCENT})
 fig.update_layout(showlegend=False)
 return apply_template(fig, "Boxplot de precios por plataforma")


@app.callback(Output("g-corr-monedas", "figure"), Input("f_year", "value"))
def cb_corr(_):
 df = prices[["usd","eur","gbp","jpy","rub"]].dropna()
 z = df.corr().values.tolist()
 fig = go.Figure(go.Heatmap(
 z=z, x=list(df.columns), y=list(df.columns),
 colorscale=[[0, "#1E2D4A"], [0.5, PS_DARK], [1, PS_ACCENT]],
 zmin=-1, zmax=1,
 text=[[f"{v:.2f}" for v in row] for row in z],
 texttemplate="%{text}",
 ))
 return apply_template(fig, "Correlación entre monedas")


@app.callback(Output("g-precio-temporal", "figure"),
 Input("f_plat", "value"), Input("f_year", "value"))
def cb_ts(plat, years):
 gf = filter_games(plat, years)
 d = price_daily_for_games(set(gf["gameid"].tolist()))
 if d.empty:
 return go.Figure().update_layout(**PLOTLY_TEMPLATE["layout"])
 fig = go.Figure([
 go.Scatter(x=d["date_acquired"], y=d["usd"],
 name="Media diaria", line=dict(color=PS_BORDER, width=1)),
 go.Scatter(x=d["date_acquired"], y=d["roll14"],
 name="Media móvil 14d", line=dict(color=PS_BLUE, width=2.5)),
 ])
 return apply_template(fig, "Serie temporal — precio medio del catálogo")


# 
# CALLBACKS — SIMULADOR
# 
@app.callback(Output("sim-output", "children"),
 Input("sim-genre", "value"), Input("sim-platform", "value"))
def cb_sim(g, plat):
 if not g:
 return ""
 d = pricing_benchmark(g, plat or "Todas")
 if "error" in d:
 return html.Div([
 html.I(className="bi bi-exclamation-triangle",
 style={"color": PS_AMBER, "marginRight": "6px"}),
 d["error"]
 ], style={"color": PS_AMBER, "fontSize": "13px"})

 return html.Div([
 html.Div([
 html.Div([
 html.Div("Q1", style={"fontSize":"11px","color":PS_MUTED,
 "textTransform":"uppercase","marginBottom":"6px"}),
 html.Div(f"${d['q1']:.2f}",
 style={"fontSize":"24px","fontWeight":"700","color":PS_GREEN}),
 ], style={"background":"#0D1F3C","borderRadius":"10px","padding":"16px",
 "textAlign":"center","flex":"1"}),
 html.Div([
 html.Div("Mediana", style={"fontSize":"11px","color":PS_MUTED,
 "textTransform":"uppercase","marginBottom":"6px"}),
 html.Div(f"${d['median']:.2f}",
 style={"fontSize":"32px","fontWeight":"800","color":PS_ACCENT}),
 ], style={"background":"#0D1F3C","border":f"1px solid {PS_BLUE}",
 "borderRadius":"10px","padding":"16px","textAlign":"center","flex":"1"}),
 html.Div([
 html.Div("Q3", style={"fontSize":"11px","color":PS_MUTED,
 "textTransform":"uppercase","marginBottom":"6px"}),
 html.Div(f"${d['q3']:.2f}",
 style={"fontSize":"24px","fontWeight":"700","color":PS_AMBER}),
 ], style={"background":"#0D1F3C","borderRadius":"10px","padding":"16px",
 "textAlign":"center","flex":"1"}),
 ], style={"display":"flex","gap":"12px","marginBottom":"12px"}),
 html.P([
 html.I(className="bi bi-people", style={"marginRight":"4px","color":PS_MUTED}),
 f"{d['n']:,} observaciones · ",
 html.I(className="bi bi-info-circle",
 style={"marginRight":"4px","marginLeft":"4px","color":PS_MUTED}),
 "Estadísticos descriptivos del catálogo feb. 2025."
 ], style={"fontSize":"12px","color":PS_MUTED}),
 ])


# 
# CALLBACKS — EXPLORADOR
# 
@app.callback(
 Output("tabla-explorador", "data"), Output("exp-count", "children"),
 Input("exp-genero", "value"), Input("exp-plat", "value"),
 Input("exp-precio", "value"), Input("btn-reset", "n_clicks"),
)
def cb_exp(genre, plat, rng, _):
 df = games.merge(prices[["gameid", "usd"]], on="gameid")
 if genre and genre != "Todos":
 df = df[df["genres_clean"].str.contains(genre, na=False)]
 if plat and plat != "Todas":
 df = df[df["platform"] == plat]
 df = df[(df["usd"] >= rng[0]) & (df["usd"] <= rng[1])]
 df = df[["title","platform","genres_clean","usd"]].sort_values("title")
 return df.to_dict("records"), f"{len(df):,} juegos encontrados"


@app.callback(
 Output("exp-genero", "value"), Output("exp-plat", "value"),
 Output("exp-precio", "value"),
 Input("btn-reset", "n_clicks"),
 prevent_initial_call=True,
)
def cb_rst(_):
 return "Todos", "Todas", [0, 70]


if __name__ == "__main__":
 print("PS Gaming Dashboard — http://127.0.0.1:8050")
 app.run(debug=True, port=8050)