"""catalogo.py — Objetivos 1 y 4: composición y crecimiento del catálogo."""
import plotly.express as px
from dash import Input, Output, html

from components import (BLUE, CAT_COLORS, PLATFORM_COLORS, SEQ_SCALE, empty, graph_card, grid, interp_children, pad_x,
                        section_header, style)
from data import filter_games

FILTERS = [Input("f-plat", "value"), Input("f-year", "value"), Input("f-genre", "value")]


def layout():
    return html.Div([
        section_header("Catálogo", "Qué se vende en PlayStation Store y cómo creció la oferta", "grid-3x3-gap",
                       ["Objetivo 1", "Objetivo 4"]),
        grid([
            graph_card("diagram-2", "Plataforma → género principal", "cat-treemap", height=400, dynamic=True,
                       note="El tamaño de cada bloque es el número de productos. Clic para entrar en una plataforma."),
            graph_card("building", "Top 15 publishers por número de productos", "cat-publishers", height=400,
                       dynamic=True),
        ]),
        grid([
            graph_card("graph-up", "Lanzamientos por año — 6 géneros más comunes", "cat-genre-year", dynamic=True),
            graph_card("pie-chart", "Participación de cada plataforma por año", "cat-platform-share", dynamic=True,
                       note="Porcentaje de los lanzamientos de cada año."),
        ]),
    ])


def last_full_year(df):
    years = df.loc[df["year"] <= 2024, "year"]
    return int(years.max()) if len(years) else int(df["year"].max())


def interp_treemap(df):
    plat = df["platform"].value_counts(normalize=True) * 100
    top_p = plat.index[0]
    gen = df.loc[df["platform"] == top_p, "genre_main"].value_counts()
    shares = df["genre_main"].value_counts(normalize=True) * 100
    small = int((shares < 1).sum())
    if len(plat) == 1:
        txt = f"Todos los productos filtrados son de {top_p}"
    else:
        txt = f"{top_p} concentra el {plat.iloc[0]:.1f}% de los productos filtrados"
    if len(shares) == 1:
        return txt + f" y todos son del género {gen.index[0]} ({gen.iloc[0]:,} productos)."
    txt += f" y dentro de ella el género más grande es {gen.index[0]} ({gen.iloc[0]:,} productos)."
    if small:
        txt += (f" {small} de los {len(shares)} géneros tienen menos del 1% del catálogo: hay pocos géneros "
                "grandes y muchos de nicho.")
    return txt


def interp_publishers(df):
    top = df["publisher"].value_counts()
    top15 = top.head(15).index
    share = df["publisher"].isin(top15).mean() * 100
    m_top = df.loc[df["publisher"].isin(top15), "price_usd"].median()
    m_rest = df.loc[~df["publisher"].isin(top15), "price_usd"].median()
    txt = (f"Los 15 publishers con más productos reúnen el {share:.1f}% del catálogo filtrado y {top.index[0]} "
           f"lidera con {top.iloc[0]:,}.")
    if m_top == m_top and m_rest == m_rest:  # ambos no nulos
        txt += (f" El precio mediano de sus juegos es ${m_top:.2f} frente a ${m_rest:.2f} del resto: "
                + ("los que más publican venden juegos más baratos." if m_top < m_rest
                   else "publicar mucho no implica precios más bajos."))
    return txt


def interp_genre_year(df, top):
    yl = last_full_year(df)
    sub = df[df["genre_main"].isin(top)]
    last = sub[sub["year"] == yl]["genre_main"].value_counts()
    before = sub[sub["year"] == yl - 5]["genre_main"].value_counts()
    if last.empty:
        return "No hay lanzamientos en el último año del rango."
    growth = (last - before.reindex(last.index).fillna(0)).sort_values()
    g1, g2 = last.index[0], growth.index[-1]
    txt = f"En {yl}, {g1} fue el género con más lanzamientos ({last.iloc[0]:,})."
    cambio = f"pasó de {int(before.get(g2, 0)):,} lanzamientos en {yl - 5} a {int(last[g2]):,}"
    if g2 == g1:
        return txt + f" También fue el que más creció: {cambio}."
    return txt + f" El que más creció fue {g2}: {cambio}."


def interp_platform_share(df):
    if df["platform"].nunique() == 1:
        return "Con una sola plataforma seleccionada el gráfico siempre muestra 100%; quita el filtro para comparar."
    yl = last_full_year(df)
    s = df[df["year"] == yl]["platform"].value_counts(normalize=True) * 100
    parts = ", ".join(f"{p} el {v:.1f}%" for p, v in s.items())
    old = df[df["platform"].isin(["PS3", "PS Vita"])].groupby("year").size() / df.groupby("year").size() * 100
    old = old.reindex(sorted(df["year"].unique())).fillna(0)
    low = old[old < 5]
    after = [y for y in low.index if (old.loc[y:] < 5).all()]
    txt = f"En {yl} los lanzamientos se repartieron así: {parts}."
    if after and old.max() >= 5:
        txt += f" El cambio de generación es claro: desde {after[0]} PS3 y PS Vita reciben menos del 5% de los juegos."
    return txt


def register(app):
    @app.callback(Output("cat-treemap", "figure"), Output("cat-publishers", "figure"),
                  Output("cat-genre-year", "figure"), Output("cat-platform-share", "figure"),
                  Output("cat-treemap-interp", "children"), Output("cat-publishers-interp", "children"),
                  Output("cat-genre-year-interp", "children"), Output("cat-platform-share-interp", "children"),
                  *FILTERS)
    def update(plat, years, genre):
        df = filter_games(plat, years, genre)
        if df.empty:
            return empty(height=400), empty(height=400), empty(), empty(), "", "", "", ""

        tm = df.groupby(["platform", "genre_main"]).size().reset_index(name="productos")
        f1 = px.treemap(tm, path=[px.Constant("Catálogo"), "platform", "genre_main"], values="productos",
                        color="productos", color_continuous_scale=SEQ_SCALE)
        f1.update_traces(root_color="#0D1426", marker_line_color="#0A0F1E",
                         hovertemplate="<b>%{label}</b><br>%{value:,} productos<extra></extra>")
        f1.update_layout(coloraxis_showscale=False)

        pub = df["publisher"].value_counts().head(15).sort_values().reset_index()
        pub.columns = ["publisher", "productos"]
        f2 = px.bar(pub, x="productos", y="publisher", orientation="h", text="productos",
                    color_discrete_sequence=[BLUE], labels={"publisher": "", "productos": "Productos"})
        f2.update_traces(textposition="outside", cliponaxis=False)
        pad_x(f2, pub["productos"].max())

        top = df.loc[df["genre_main"] != "Sin género", "genre_main"].value_counts().head(6).index
        gy = df[df["genre_main"].isin(top)].groupby(["year", "genre_main"]).size().reset_index(name="productos")
        f3 = px.line(gy, x="year", y="productos", color="genre_main", markers=True,
                     color_discrete_map=dict(zip(top, CAT_COLORS)), category_orders={"genre_main": list(top)},
                     labels={"year": "Año de lanzamiento", "productos": "Productos", "genre_main": "Género"})

        ps = df.groupby(["year", "platform"]).size().reset_index(name="n")
        ps["pct"] = ps["n"] / ps.groupby("year")["n"].transform("sum") * 100
        f4 = px.area(ps, x="year", y="pct", color="platform", color_discrete_map=PLATFORM_COLORS,
                     labels={"year": "Año de lanzamiento", "pct": "% de lanzamientos", "platform": "Plataforma"})
        f4.update_yaxes(range=[0, 100], ticksuffix="%")

        return (style(f1, 400, legend=False), style(f2, 400, legend=False), style(f3), style(f4),
                interp_children(interp_treemap(df)), interp_children(interp_publishers(df)),
                interp_children(interp_genre_year(df, top)), interp_children(interp_platform_share(df)))
