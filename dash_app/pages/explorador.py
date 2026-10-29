"""explorador.py — Tabla interactiva del catálogo limpio."""
from dash import Input, Output, dash_table, html

from components import BORDER, CARD, MUTED, TEXT, card, section_header
from data import filter_games

FILTERS = [Input("f-plat", "value"), Input("f-year", "value"), Input("f-genre", "value")]
COLUMNS = [
    {"name": "Título", "id": "title"},
    {"name": "Plataforma", "id": "platform"},
    {"name": "Género", "id": "genre_main"},
    {"name": "Publisher", "id": "publisher"},
    {"name": "Año", "id": "year", "type": "numeric"},
    {"name": "Precio USD", "id": "price_usd", "type": "numeric", "format": {"specifier": "$.2f"}},
    {"name": "Compradores", "id": "n_owners", "type": "numeric", "format": {"specifier": ","}},
    {"name": "Trofeos", "id": "n_trophies", "type": "numeric"},
]


def layout():
    return html.Div([
        section_header("Explorador", "Busca y ordena cualquier juego del catálogo limpio", "search"),
        html.Div(id="exp-count", className="card-note", style={"marginBottom": "8px"}),
        card("table", "Catálogo (usa los filtros del menú; escribe en la fila gris para buscar)", dash_table.DataTable(
            id="exp-table", columns=COLUMNS, page_size=15, sort_action="native", filter_action="native",
            style_table={"overflowX": "auto"},
            style_cell={"backgroundColor": CARD, "color": TEXT, "border": f"1px solid {BORDER}", "fontSize": "12.5px",
                        "fontFamily": "Inter, Segoe UI, Arial", "padding": "7px 10px", "textAlign": "left",
                        "maxWidth": "280px", "overflow": "hidden", "textOverflow": "ellipsis"},
            style_header={"backgroundColor": "#0D1426", "color": MUTED, "fontWeight": "600", "fontSize": "11px",
                          "textTransform": "uppercase"},
            style_filter={"backgroundColor": "#1A2236", "color": TEXT},
            style_cell_conditional=[{"if": {"column_type": "numeric"}, "textAlign": "right"}],
        )),
    ])


def register(app):
    @app.callback(Output("exp-table", "data"), Output("exp-count", "children"), *FILTERS)
    def update(plat, years, genre):
        df = filter_games(plat, years, genre)[[c["id"] for c in COLUMNS]].sort_values("n_owners", ascending=False)
        return df.to_dict("records"), f"{len(df):,} productos con los filtros actuales (ordenados por compradores)."
