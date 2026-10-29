"""etl.py — Página del proceso ETL: pasos, calidad de datos y decisiones."""
import plotly.express as px
from dash import dcc, html

from components import (ACCENT, AMBER, BLUE, GREEN, PURPLE, RED, card, grid, insight, pad_x, section_header,
                        step, style)
from data import S, etl_quality, fx_rates, missing_raw


def missing_fig():
    df = missing_raw[missing_raw["pct_faltante"] > 0].copy()
    df["campo"] = df["tabla"] + " · " + df["columna"]
    df = df.sort_values("pct_faltante")
    fig = px.bar(df, x="pct_faltante", y="campo", orientation="h", color="tabla",
                 text=df["pct_faltante"].map(lambda v: f"{v:.1f}%"),
                 color_discrete_sequence=[BLUE, AMBER, GREEN, PURPLE, RED],
                 labels={"pct_faltante": "% de valores faltantes", "campo": ""})
    fig.update_traces(textposition="outside", cliponaxis=False)
    pad_x(fig, df["pct_faltante"].max())
    return style(fig, 340)


def missing_interp():
    m = missing_raw.set_index(["tabla", "columna"])["pct_faltante"]
    return (f"Los faltantes se concentran en los precios en RUB ({m[('prices', 'rub')]:.1f}%) y JPY "
            f"({m[('prices', 'jpy')]:.1f}%) y en los idiomas ({m[('games', 'supported_languages')]:.1f}%). "
            "No son errores: muchos juegos no se venden en Rusia o Japón y la tienda no siempre publica los idiomas. "
            "Por eso la comparación de monedas usa solo juegos que tienen los dos precios. Las tablas de jugadores, "
            "compras, trofeos y actividad no tienen faltantes.")


def quality_table():
    head = html.Thead(html.Tr([html.Th("Tabla"), html.Th("Paso"), html.Th("Antes", className="num"),
                               html.Th("Después", className="num"), html.Th("Detalle")]))
    body = html.Tbody([html.Tr([html.Td(r.tabla), html.Td(r.paso), html.Td(f"{r.filas_antes:,}", className="num"),
                                html.Td(f"{r.filas_despues:,}", className="num"), html.Td(r.detalle)])
                       for r in etl_quality.itertuples()])
    return html.Div(html.Table([head, body], className="ps-table"), style={"overflowX": "auto"})


def layout():
    fx = ", ".join(f"1 {r.currency} = {r.usd_per_unit:.4g} USD" for r in fx_rates.itertuples() if r.currency != "USD")
    return html.Div([
        section_header("ETL", "Extracción, limpieza y transformación de las 6 tablas", "database-gear"),
        card("diagram-3", "Pasos del proceso (etl/etl_playstation.py)", html.Div([
            step("E", "Extraer", "Lectura de games, prices, players, purchased_games, achievements y history. "
                 "Los archivos grandes se leen por partes (history: 19,5 M de filas).", BLUE),
            step("T1", "Limpiar", "Duplicados, fechas inválidas, precios ≤ 0 como nulos, listas de texto "
                 "(['Action', 'Indie']) convertidas a columnas.", ACCENT),
            step("T2", "Corregir el precio", "prices tiene 2 o 3 capturas por juego. Se usa solo la última "
                 "(precio vigente) para no contar el mismo juego varias veces.", GREEN),
            step("T3", "Enriquecer", "País a código ISO-3 para el mapa, monedas convertidas a USD, "
                 "dueños por juego y trofeos por rareza.", PURPLE),
            step("L", "Cargar", "13 tablas pequeñas en data/processed/ (≈10 MB) que leen Dash y Shiny.", AMBER),
        ], className="step-grid")),
        html.Div(style={"height": "14px"}),
        card("table", "Registro de calidad: filas antes y después de cada paso", quality_table()),
        html.Div(style={"height": "14px"}),
        grid([
            card("clipboard-data", "Valores faltantes en los datos crudos",
                 dcc.Graph(figure=missing_fig(), config={"displayModeBar": False}),
                 note="Solo columnas con algún faltante, en los CSV originales.", interp=missing_interp()),
            card("lightbulb", "Decisiones del ETL", html.Div([
                insight("Precio vigente:", "se toma la última captura de cada juego. El trabajo anterior unía todas "
                        "las capturas y contaba cada juego 2 o 3 veces."),
                insight("Sin precio:", f"{S['n_no_price']} juegos no tienen precio publicado (gratis, retirados o "
                        "solo en bundles). Se excluyen solo de los gráficos de precio."),
                insight("Atípicos:", "los precios altos (> Q3 + 1,5·IQR) se marcan pero no se eliminan: son "
                        "juegos AAA reales, no errores."),
                insight("Ediciones regionales:", f"{S['n_games']} productos y {S['n_titles']} títulos únicos. Se "
                        "conservan porque son fichas distintas de la tienda."),
                insight("Tasas de cambio:", f"aprox. 24-feb-2025: {fx}."),
                insight("Trofeos:", "un trofeo repetido por el mismo jugador se cuenta una vez; solo se usan "
                        "trofeos de juegos que están en el catálogo."),
            ])),
        ], "grid-60-40"),
    ])
