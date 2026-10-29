"""resumen.py — Vista general con KPIs filtrables e insights clave."""
import plotly.express as px
from dash import Input, Output, html

from components import (ACCENT, AMBER, BLUE, GREEN, PLATFORM_COLORS, PURPLE, card, empty, fmt_int,
                        fmt_usd, graph_card, grid, insight, interp_children, kpi, section_header, style)
from data import S, filter_games

FILTERS = [Input("f-plat", "value"), Input("f-year", "value"), Input("f-genre", "value")]


def layout():
    return html.Div([
        section_header("Resumen", "Vista general del catálogo y de la audiencia de PlayStation Store", "speedometer2"),
        html.Div(id="res-kpis", className="kpi-grid"),
        grid([
            graph_card("bar-chart-steps", "Lanzamientos por año y plataforma", "res-year", dynamic=True,
                       note="Productos de la tienda según su año de lanzamiento. 2025 solo incluye enero."),
            card("lightbulb", "Insights clave (todo el dataset)", html.Div([
                insight("Catálogo:", f"{S['top_platform']} tiene el {S['top_platform_pct']} de los productos."),
                insight("Precio:", f"mediana de {S['median_price']}; el {S['pct_under_10']} cuesta menos de $10."),
                insight("Audiencia:", f"{S['top_country']} reúne el {S['top_country_pct']} de los jugadores."),
                insight("Popularidad:", f"{S['top_owned_game']} está en el {S['top_owned_pct']} de las bibliotecas."),
                insight("Dificultad:", f"solo el {S['earn_platinum']} (mediana) de los jugadores de un juego consigue su Platinum."),
                insight("Precios estables:", f"solo {S['n_price_changed']} juegos cambiaron de precio en feb. 2025.", warn=True),
            ])),
        ], "grid-60-40"),
    ])


def interp_year(df):
    by_year = df["year"].value_counts()
    peak, n = int(by_year.idxmax()), int(by_year.max())
    recent = (df["year"] >= 2020).mean() * 100
    plat = df["platform"].value_counts(normalize=True) * 100
    return (f"El año con más lanzamientos es {peak} ({n:,} productos). El {recent:.1f}% de los productos filtrados "
            f"salió desde 2020: el catálogo es reciente y creció muy rápido en los últimos años. "
            f"{plat.index[0]} es la plataforma con más productos ({plat.iloc[0]:.1f}%).")


def register(app):
    @app.callback(Output("res-kpis", "children"), Output("res-year", "figure"), Output("res-year-interp", "children"),
                  *FILTERS)
    def update(plat, years, genre):
        df = filter_games(plat, years, genre)
        priced = df["price_usd"].dropna()
        kpis = [
            kpi("Productos", fmt_int(len(df)), f"{fmt_int(df['title'].nunique())} títulos únicos", BLUE),
            kpi("Precio mediano", fmt_usd(priced.median()) if len(priced) else "—", "USD, feb. 2025", AMBER),
            kpi("Menos de $10", f"{(priced < 10).mean() * 100:.1f}%" if len(priced) else "—", "de los juegos con precio", GREEN),
            kpi("Trofeos por juego", fmt_int(df.loc[df['n_trophies'] > 0, 'n_trophies'].median())
                if (df['n_trophies'] > 0).any() else "—", "mediana", PURPLE),
            kpi("Jugadores", S["n_players"], f"{S['n_countries']} países · sin filtro", ACCENT),
        ]
        if df.empty:
            return kpis, empty(), ""
        by = df.groupby(["year", "platform"]).size().reset_index(name="juegos")
        fig = px.bar(by, x="year", y="juegos", color="platform", color_discrete_map=PLATFORM_COLORS,
                     labels={"year": "Año de lanzamiento", "juegos": "Productos", "platform": "Plataforma"})
        fig.update_layout(bargap=0.15)
        return kpis, style(fig, 360), interp_children(interp_year(df))
