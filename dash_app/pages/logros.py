"""logros.py — Objetivo 8: dificultad de los juegos según sus trofeos."""
import plotly.express as px
from dash import Input, Output, html

from components import (BLUE, RARITY_COLORS, card, empty, graph_card, grid, interp_children, section_header, style)
from data import RARITY_ORDER, S, filter_games, rarest_trophies, rarity_summary

FILTERS = [Input("f-plat", "value"), Input("f-year", "value"), Input("f-genre", "value")]


def earn_fig():
    df = rarity_summary.set_index("rarity").reindex(RARITY_ORDER).reset_index()
    fig = px.bar(df, x="rarity", y="median_earn_rate", color="rarity", color_discrete_map=RARITY_COLORS,
                 text=df["median_earn_rate"].map(lambda v: f"{v:.1f}%"), custom_data=["n_trophies"],
                 labels={"rarity": "", "median_earn_rate": "% de jugadores que lo consigue (mediana)"})
    fig.update_traces(textposition="outside", cliponaxis=False,
                      hovertemplate="%{x}: %{y:.1f}% · %{customdata[0]:,} trofeos<extra></extra>")
    fig.update_yaxes(ticksuffix="%")
    return style(fig, 340, legend=False)


def rare_table():
    df = rarest_trophies.head(15)
    rows = [html.Tr([html.Td(r.trophy), html.Td(f"{r.game} ({r.platform})"), html.Td(r.rarity),
                     html.Td(f"{r.earners:,} / {r.game_players:,}", className="num"),
                     html.Td(f"{r.earn_rate:.2f}%", className="num")]) for r in df.itertuples()]
    return html.Div(html.Table([
        html.Thead(html.Tr([html.Th("Trofeo"), html.Th("Juego"), html.Th("Rareza"),
                            html.Th("Lo tienen", className="num"), html.Th("%", className="num")])),
        html.Tbody(rows)], className="ps-table"), style={"maxHeight": "340px", "overflowY": "auto"})


EARN = earn_fig()
_plat = float(S["earn_platinum"].rstrip("%"))
INTERP_EARN = (f"Cuanto más alta la rareza, menos jugadores la consiguen: Bronze {S['earn_bronze']}, Silver "
               f"{S['earn_silver']}, Gold {S['earn_gold']} y Platinum {S['earn_platinum']}. La clasificación de Sony "
               f"refleja bien la dificultad real. En el juego típico, 1 de cada {round(100 / _plat)} jugadores llega "
               "al Platinum.")
_top15 = rarest_trophies.head(15)
_e0, _e1 = _top15["earners"].min(), _top15["earners"].max()
_quien = f"{_e0} jugador" if _e0 == _e1 == 1 else (f"{_e0} jugadores" if _e0 == _e1 else f"entre {_e0} y {_e1} jugadores")
INTERP_RARE = (f"Ninguno de estos trofeos supera el {_top15['earn_rate'].max():.2f}%: de cientos de jugadores con "
               f"algún trofeo del juego, solo {_quien} lo consiguió. "
               f"El más raro es {S['rarest_trophy']}. No todos son Platinum: algunos Bronze o Gold son más difíciles "
               "que el Platinum de otros juegos.")


def layout():
    return html.Div([
        section_header("Logros", "Qué tan difíciles son los juegos según sus trofeos", "award", ["Objetivo 8"]),
        grid([
            graph_card("bar-chart", "Trofeos por juego", "log-hist", dynamic=True,
                       note="Juegos con al menos un trofeo; eje cortado en 100 trofeos."),
            graph_card("stack", "Composición de trofeos por género (12 más comunes)", "log-mix", dynamic=True,
                       note="Porcentaje de los trofeos de cada género según su rareza."),
        ]),
        grid([
            graph_card("percent", "¿Cuántos jugadores consiguen cada tipo de trofeo?", "log-earn", figure=EARN,
                       interp=INTERP_EARN,
                       note="Rareza real: jugadores que ganaron el trofeo entre los que ganaron algún trofeo del "
                            "juego (juegos con 200+ jugadores). No usa filtros."),
            card("gem", "Los 15 trofeos más raros", rare_table(), interp=INTERP_RARE, note="No usa filtros."),
        ]),
    ])


def interp_hist(df):
    med = df["n_trophies"].median()
    mode = df["n_trophies"].mode().iloc[0]
    k = int((df["n_trophies"] == mode).sum())
    plat = df["has_platinum"].mean() * 100
    return (f"Un juego tiene en mediana {med:.0f} trofeos. El valor más repetido es {mode} ({k:,} juegos): muchos "
            f"juegos pequeños usan listas cortas y casi iguales. El {plat:.1f}% de los juegos tiene Platinum.")


def interp_mix(df, mix):
    hard = (mix["Gold"] + mix["Platinum"]).sort_values()
    g_hi, g_lo = hard.index[-1], hard.index[0]
    if len(hard) == 1:
        return f"Con un solo género no hay comparación: el {hard.iloc[0]:.1f}% de sus trofeos son Gold o Platinum."
    med = df.groupby("genre_main")["n_trophies"].median()
    txt = (f"{g_hi} tiene la mayor proporción de trofeos Gold + Platinum ({hard.iloc[-1]:.1f}%) y {g_lo} la menor "
           f"({hard.iloc[0]:.1f}%).")
    if med[g_hi] < med[g_lo]:
        txt += (f" Esto no significa que {g_hi} sea más difícil: sus juegos tienen listas más cortas "
                f"({med[g_hi]:.0f} trofeos en mediana frente a {med[g_lo]:.0f}), así que cada trofeo vale más.")
    return txt


def register(app):
    @app.callback(Output("log-hist", "figure"), Output("log-mix", "figure"),
                  Output("log-hist-interp", "children"), Output("log-mix-interp", "children"), *FILTERS)
    def update(plat, years, genre):
        df = filter_games(plat, years, genre)
        df = df[df["n_trophies"] > 0]
        if df.empty:
            return empty(), empty(), "", ""

        f1 = px.histogram(df[df["n_trophies"] <= 100], x="n_trophies", nbins=50, color_discrete_sequence=[BLUE],
                          labels={"n_trophies": "Trofeos del juego"})
        med = df["n_trophies"].median()
        f1.add_vline(x=med, line_dash="dash", line_color="#F0F4FF",
                     annotation_text=f"Mediana: {med:.0f}", annotation_font_color="#F0F4FF")
        f1.update_yaxes(title_text="Juegos")

        top = df.loc[df["genre_main"] != "Sin género", "genre_main"].value_counts().head(12).index
        cols = [f"n_{r.lower()}" for r in RARITY_ORDER]
        mix = df[df["genre_main"].isin(top)].groupby("genre_main")[cols].sum()
        mix = mix.div(mix.sum(axis=1), axis=0) * 100
        mix.columns = RARITY_ORDER
        order = mix.sort_values("Bronze").index.tolist()
        long = mix.reset_index().melt(id_vars="genre_main", var_name="rarity", value_name="pct")
        f2 = px.bar(long, x="pct", y="genre_main", color="rarity", orientation="h",
                    color_discrete_map=RARITY_COLORS,
                    category_orders={"rarity": RARITY_ORDER, "genre_main": order},
                    labels={"pct": "% de los trofeos", "genre_main": "", "rarity": "Rareza"})
        f2.update_xaxes(ticksuffix="%", range=[0, 100])

        return (style(f1, legend=False), style(f2), interp_children(interp_hist(df)),
                interp_children(interp_mix(df, mix)) if len(mix) else "")
