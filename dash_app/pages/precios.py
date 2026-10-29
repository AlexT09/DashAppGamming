"""precios.py — Objetivos 2, 3 y 9: distribución, monedas y cambios de precio."""
import pandas as pd
import plotly.express as px
from dash import Input, Output, html

from components import (CURRENCY_COLORS, PLATFORM_COLORS, card, empty, graph_card, grid, interp_children,
                        section_header, style)
from data import CURRENCIES, filter_games, snapshots

FILTERS = [Input("f-plat", "value"), Input("f-year", "value"), Input("f-genre", "value")]
TIERS = ["< $5", "$5–10", "$10–20", "$20–40", "> $40"]
TIER_COLORS = ["#13294B", "#1D4E89", "#0070D1", "#00AAFF", "#7FD3F7"]


def layout():
    return html.Div([
        section_header("Precios", "Cuánto cuestan los juegos, en qué moneda salen más caros y si cambian",
                       "currency-dollar", ["Objetivo 2", "Objetivo 3", "Objetivo 9"]),
        grid([
            graph_card("box", "Precio por género principal (12 más comunes)", "pre-box", height=400, dynamic=True,
                       note="Ordenado por mediana. La caja va del 25% al 75% de los precios; eje recortado en $80."),
            graph_card("bar-chart", "Rango de precio por plataforma", "pre-tier", height=400, dynamic=True,
                       note="Porcentaje de juegos de cada plataforma en cada rango (USD)."),
        ], "grid-60-40"),
        grid([
            graph_card("currency-exchange", "¿En qué moneda sale más caro?", "pre-currency", dynamic=True,
                       note="Diferencia mediana del precio local convertido a USD frente al precio en USD del mismo "
                            "juego. Tasas aprox. del 24-feb-2025."),
            graph_card("graph-down", "Precio mediano según año de lanzamiento", "pre-year", dynamic=True,
                       note="Precio de feb. 2025 de los juegos lanzados cada año (no es el precio histórico). "
                            "Solo años con 20+ juegos; 2025 se excluye porque solo tiene enero."),
        ]),
        card("arrow-left-right", "Juegos que cambiaron de precio entre capturas (22 al 25 de febrero de 2025)",
             html.Div(id="pre-changes"), interp_id="pre-changes-interp"),
    ])


def currency_diffs(p):
    rows = []
    for c in CURRENCIES[1:]:
        both = p.dropna(subset=[f"price_{c}_in_usd"])
        if len(both):
            rows.append({"moneda": c.upper(),
                         "dif": ((both[f"price_{c}_in_usd"] / both["price_usd"]).median() - 1) * 100,
                         "n": len(both)})
    return pd.DataFrame(rows).sort_values("dif", ascending=False)


def interp_box(b):
    st = b.groupby("genre_main")["price_usd"].describe()
    st["iqr"] = st["75%"] - st["25%"]
    if len(st) == 1:
        g = st.index[0]
        return (f"Con un solo género no hay comparación: la mitad de los juegos de {g} cuesta entre "
                f"${st.loc[g, '25%']:.2f} y ${st.loc[g, '75%']:.2f} (mediana ${st.loc[g, '50%']:.2f}).")
    hi, lo, nar = st["50%"].idxmax(), st["50%"].idxmin(), st["iqr"].idxmin()
    return (f"{hi} tiene el precio mediano más alto (${st.loc[hi, '50%']:.2f}) y {lo} el más bajo "
            f"(${st.loc[lo, '50%']:.2f}). {nar} tiene la caja más estrecha (la mitad de sus juegos cuesta entre "
            f"${st.loc[nar, '25%']:.2f} y ${st.loc[nar, '75%']:.2f}): sus precios son muy parecidos. Los bigotes "
            "largos muestran que en casi todos los géneros conviven juegos baratos y juegos caros.")


def interp_tier(p, t):
    cheap = t[t["price_tier"] == "< $5"].set_index("platform")["pct"]
    over40 = (p["price_usd"] >= 40).mean() * 100
    txt = ""
    if p["platform"].nunique() == 1 and len(cheap):
        txt = f"El {cheap.max():.1f}% de los juegos de {cheap.idxmax()} cuesta menos de $5. "
    elif len(cheap):
        txt = f"{cheap.idxmax()} tiene la mayor proporción de juegos de menos de $5 ({cheap.max():.1f}%). "
    return txt + (f"En total solo el {over40:.1f}% de los juegos cuesta $40 o más: el catálogo es sobre todo de "
                  "bajo precio y los juegos AAA son una minoría.")


def interp_currency(cur):
    if cur.empty:
        return "No hay juegos con precio en otras monedas para estos filtros."
    top, low = cur.iloc[0], cur.iloc[-1]
    cheaper = cur[cur["dif"] < 0]["moneda"].tolist()
    txt = (f"El mismo juego cuesta en mediana {top['dif']:+.1f}% en {top['moneda']} y {low['dif']:+.1f}% en "
           f"{low['moneda']} frente a su precio en USD. Sony fija precios distintos por región")
    lista = " y ".join([", ".join(cheaper[:-1]), cheaper[-1]]) if len(cheaper) > 1 else "".join(cheaper)
    return txt + (f": comprar en {lista} sale más barato que en dólares." if cheaper else ".")


def interp_year(y):
    parts = []
    trend = []
    for plat, d in y.groupby("platform"):
        d = d.sort_values("year")
        if len(d) >= 2:
            a, b = d.iloc[0], d.iloc[-1]
            parts.append(f"en {plat} pasa de ${a['median']:.2f} (juegos de {int(a['year'])}) a "
                         f"${b['median']:.2f} (juegos de {int(b['year'])})")
            trend.append(b["median"] < a["median"])
    if not parts:
        return "Hay pocos juegos por año para comparar con estos filtros."
    txt = "La mediana " + " y ".join(parts) + "."
    if all(trend):
        txt += (" Los juegos más recientes son más baratos porque cada año llegan más juegos indie de bajo precio; "
                "no significa que los precios bajen con el tiempo (todos son precios de 2025).")
    return txt


def _changes(df):
    s = snapshots[snapshots["gameid"].isin(df["gameid"])].dropna(subset=["usd"]).sort_values("date")
    fl = s.groupby("gameid")["usd"].agg(["first", "last", "size"])
    multi = int((fl["size"] >= 2).sum())
    ch = fl[fl["first"] != fl["last"]].join(df.set_index("gameid")[["title", "platform"]])
    ch["pct"] = (ch["last"] / ch["first"] - 1) * 100
    ch = ch.sort_values("pct")
    resumen = html.P(f"{len(ch)} de {multi:,} juegos con 2 o más capturas cambiaron de precio "
                     f"({len(ch) / multi * 100 if multi else 0:.2f}%).",
                     className="card-note", style={"marginBottom": "8px"})
    down, up = int((ch["pct"] < 0).sum()), int((ch["pct"] > 0).sum())
    if ch.empty:
        txt = "Ningún juego de esta selección cambió de precio entre las capturas."
    else:
        txt = f"En 4 días casi ningún precio cambió: {down} juegos bajaron y {up} subieron."
    txt += (" No se ven rebajas masivas en este periodo, así que los precios del análisis son estables y "
            "representativos. Para estudiar descuentos haría falta un historial de varios meses.")
    if ch.empty:
        return [resumen], interp_children(txt)
    rows = [html.Tr([html.Td(r.title), html.Td(r.platform), html.Td(f"${r.first:.2f}", className="num"),
                     html.Td(f"${r.last:.2f}", className="num"),
                     html.Td(f"{r.pct:+.1f}%", className="num",
                             style={"color": "#22C55E" if r.pct < 0 else "#EF4444"})]) for r in ch.itertuples()]
    table = html.Table([html.Thead(html.Tr([html.Th("Juego"), html.Th("Plataforma"), html.Th("Antes", className="num"),
                                            html.Th("Después", className="num"), html.Th("Cambio", className="num")])),
                        html.Tbody(rows)], className="ps-table")
    return [resumen, html.Div(table, style={"maxHeight": "320px", "overflowY": "auto"})], interp_children(txt)


def register(app):
    @app.callback(Output("pre-box", "figure"), Output("pre-tier", "figure"), Output("pre-currency", "figure"),
                  Output("pre-year", "figure"), Output("pre-changes", "children"),
                  Output("pre-box-interp", "children"), Output("pre-tier-interp", "children"),
                  Output("pre-currency-interp", "children"), Output("pre-year-interp", "children"),
                  Output("pre-changes-interp", "children"), *FILTERS)
    def update(plat, years, genre):
        df = filter_games(plat, years, genre)
        p = df.dropna(subset=["price_usd"])
        changes, changes_txt = _changes(df)
        if p.empty:
            return empty(height=400), empty(height=400), empty(), empty(), changes, "", "", "", "", changes_txt

        top = p.loc[p["genre_main"] != "Sin género", "genre_main"].value_counts().head(12).index
        b = p[p["genre_main"].isin(top)]
        order = b.groupby("genre_main")["price_usd"].median().sort_values(ascending=False).index.tolist()
        f1 = px.box(b, x="genre_main", y="price_usd", category_orders={"genre_main": order},
                    color_discrete_sequence=["#0070D1"], points=False,
                    labels={"genre_main": "", "price_usd": "Precio (USD)"})
        f1.update_yaxes(range=[0, 80], tickprefix="$")
        f1.update_xaxes(tickangle=-35)

        t = p.groupby(["platform", "price_tier"], observed=True).size().reset_index(name="n")
        t["pct"] = t["n"] / t.groupby("platform")["n"].transform("sum") * 100
        f2 = px.bar(t, x="platform", y="pct", color="price_tier", category_orders={"price_tier": TIERS},
                    color_discrete_sequence=TIER_COLORS,
                    labels={"platform": "", "pct": "% de juegos", "price_tier": "Rango"})
        f2.update_yaxes(ticksuffix="%", range=[0, 100])

        cur = currency_diffs(p)
        f3 = px.bar(cur, x="moneda", y="dif", color="moneda", color_discrete_map=CURRENCY_COLORS,
                    text=cur["dif"].map(lambda v: f"{v:+.1f}%"), custom_data=["n"],
                    labels={"moneda": "", "dif": "Diferencia vs USD (%)"})
        f3.update_traces(textposition="outside", cliponaxis=False,
                         hovertemplate="%{x}: %{y:+.1f}% · %{customdata[0]:,} juegos<extra></extra>")
        f3.add_hline(y=0, line_color="#8B9BB4", line_width=1)
        f3.update_yaxes(ticksuffix="%")

        y = p[p["platform"].isin(["PS4", "PS5"]) & (p["year"] <= 2024)].groupby(["year", "platform"])["price_usd"] \
            .agg(["median", "size"]).reset_index()
        y = y[y["size"] >= 20]
        f4 = px.line(y, x="year", y="median", color="platform", markers=True, color_discrete_map=PLATFORM_COLORS,
                     labels={"year": "Año de lanzamiento", "median": "Precio mediano (USD)", "platform": "Plataforma"})
        f4.update_yaxes(tickprefix="$")

        return (style(f1, 400, legend=False), style(f2, 400), style(f3, legend=False), style(f4), changes,
                interp_children(interp_box(b)) if len(b) else "", interp_children(interp_tier(p, t)),
                interp_children(interp_currency(cur)), interp_children(interp_year(y)), changes_txt)
