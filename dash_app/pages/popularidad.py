"""popularidad.py — Objetivo 6: juegos más comprados y relación con el precio."""
import plotly.express as px
from dash import Input, Output, html

from components import (AMBER, BLUE, PLATFORM_COLORS, empty, graph_card, grid, interp_children, pad_x,
                        section_header, style)
from data import S, filter_games, player_library

FILTERS = [Input("f-plat", "value"), Input("f-year", "value"), Input("f-genre", "value")]
N_LIB = len(player_library)


def library_fig():
    lib = player_library[player_library["library_size"] <= 1000]
    fig = px.histogram(lib, x="library_size", nbins=50, color_discrete_sequence=[AMBER],
                       labels={"library_size": "Juegos en la biblioteca"})
    med = player_library["library_size"].median()
    fig.add_vline(x=med, line_dash="dash", line_color="#F0F4FF",
                  annotation_text=f"Mediana: {med:.0f}", annotation_font_color="#F0F4FF")
    fig.update_yaxes(title_text="Jugadores")
    return style(fig, 340, legend=False)


LIBRARY = library_fig()
INTERP_LIBRARY = (f"La distribución está sesgada a la derecha: la mitad de los jugadores tiene {S['median_library']} "
                  f"juegos o menos y el 90% tiene {S['p90_library']} o menos, pero unos pocos coleccionistas llegan a "
                  f"{S['max_library']}. Por eso se usa la mediana y no el promedio para describir al jugador típico.")


def layout():
    return html.Div([
        section_header("Popularidad", "Qué juegos compran realmente los jugadores de la muestra", "fire",
                       ["Objetivo 6"]),
        grid([
            graph_card("trophy", "Top 15 juegos con más compradores", "pop-top", height=420, dynamic=True,
                       note=f"Compradores = jugadores de la muestra ({S['n_players_library']} bibliotecas públicas) "
                            "que tienen el juego."),
            graph_card("crosshair", "Precio vs. compradores", "pop-scatter", height=420, dynamic=True,
                       note="Cada punto es un juego. Eje vertical en escala logarítmica."),
        ]),
        grid([
            graph_card("tags", "Compradores medianos por género (12 más comunes)", "pop-genre", dynamic=True),
            graph_card("collection", "Tamaño de las bibliotecas", "pop-library", figure=LIBRARY, interp=INTERP_LIBRARY,
                       note="No usa filtros. Se cortan bibliotecas de más de 1.000 juegos para ver mejor la forma."),
        ]),
    ])


def interp_top(df, top):
    best = top.iloc[-1]
    n_plat = top["platform"].value_counts()
    m_top = top["price_usd"].median()
    m_all = df["price_usd"].median()
    plat_txt = (f"Los {len(top)} son de {n_plat.index[0]}." if n_plat.iloc[0] == len(top)
                else f"{n_plat.iloc[0]} de los {len(top)} son de {n_plat.index[0]}.")
    txt = (f"{best['title']} lidera con {int(best['n_owners']):,} compradores ({best['n_owners'] / N_LIB * 100:.1f}% "
           f"de las bibliotecas). {plat_txt}")
    if m_top == m_top and m_all == m_all:
        txt += f" Su precio mediano actual es ${m_top:.2f}, frente a ${m_all:.2f} de todos los juegos filtrados"
        txt += (": los más comprados cuestan más que el juego típico, no son los más baratos." if m_top > m_all else ".")
    return txt


def interp_scatter(sc):
    if len(sc) < 10:
        return "Hay muy pocos juegos para medir la relación con estos filtros."
    rho = sc["price_usd"].rank().corr(sc["n_owners"].rank())
    fuerza = "prácticamente nula" if abs(rho) < 0.1 else "débil" if abs(rho) < 0.3 else "moderada" if abs(rho) < 0.6 else "fuerte"
    signo = "positiva" if rho > 0 else "negativa"
    txt = f"La correlación de Spearman entre precio y compradores es {rho:.2f} ({fuerza}, {signo})."
    if abs(rho) < 0.3:
        txt += (" Hay juegos de menos de $5 con miles de compradores y juegos de $60 con muy pocos: el precio casi "
                "no explica la popularidad; pesan más la marca, el género o la publicidad.")
    return txt


def interp_genre(df, gm):
    hi, lo = gm.iloc[-1], gm.iloc[0]
    if len(gm) == 1:
        return f"Con un solo género no hay comparación: cada juego de {hi['genre_main']} tiene en mediana {hi['n_owners']:,.0f} compradores."
    biggest = df.loc[df["genre_main"] != "Sin género", "genre_main"].value_counts().index[0]
    med_big = gm.set_index("genre_main")["n_owners"].get(biggest)
    txt = (f"{hi['genre_main']} tiene la mediana más alta ({hi['n_owners']:,.0f} compradores por juego) y "
           f"{lo['genre_main']} la más baja ({lo['n_owners']:,.0f}).")
    if med_big is not None:
        txt += (f" Que un género tenga muchos juegos no significa que cada uno se compre más: {biggest} es el género "
                f"con más juegos y su mediana es {med_big:,.0f}.")
    return txt


def register(app):
    @app.callback(Output("pop-top", "figure"), Output("pop-scatter", "figure"), Output("pop-genre", "figure"),
                  Output("pop-top-interp", "children"), Output("pop-scatter-interp", "children"),
                  Output("pop-genre-interp", "children"), *FILTERS)
    def update(plat, years, genre):
        df = filter_games(plat, years, genre)
        df = df[df["n_owners"] > 0]
        if df.empty:
            return empty(height=420), empty(height=420), empty(), "", "", ""

        top = df.nlargest(15, "n_owners").sort_values("n_owners")
        top = top.assign(label=top["title"].str.slice(0, 38) + " (" + top["platform"] + ")")
        f1 = px.bar(top, x="n_owners", y="label", orientation="h", color="platform",
                    color_discrete_map=PLATFORM_COLORS, text="n_owners",
                    labels={"n_owners": "Compradores", "label": "", "platform": "Plataforma"})
        f1.update_traces(texttemplate="%{text:,}", textposition="outside", cliponaxis=False)
        f1.update_layout(yaxis={"categoryorder": "total ascending"})
        pad_x(f1, top["n_owners"].max())

        sc = df.dropna(subset=["price_usd"])
        f2 = px.scatter(sc, x="price_usd", y="n_owners", color="platform", color_discrete_map=PLATFORM_COLORS,
                        hover_name="title", log_y=True, opacity=0.55,
                        labels={"price_usd": "Precio (USD)", "n_owners": "Compradores", "platform": "Plataforma"})
        f2.update_traces(marker=dict(size=6))
        f2.update_xaxes(tickprefix="$")
        f2.update_yaxes(dtick=1)

        top_g = df.loc[df["genre_main"] != "Sin género", "genre_main"].value_counts().head(12).index
        gm = df[df["genre_main"].isin(top_g)].groupby("genre_main")["n_owners"].median().sort_values().reset_index()
        f3 = px.bar(gm, x="n_owners", y="genre_main", orientation="h", color_discrete_sequence=[BLUE],
                    text="n_owners", labels={"n_owners": "Compradores (mediana)", "genre_main": ""})
        f3.update_traces(texttemplate="%{text:,.0f}", textposition="outside", cliponaxis=False)
        if len(gm):
            pad_x(f3, gm["n_owners"].max())

        return (style(f1, 420), style(f2, 420), style(f3, legend=False),
                interp_children(interp_top(df, top)), interp_children(interp_scatter(sc)),
                interp_children(interp_genre(df, gm)) if len(gm) else "")
