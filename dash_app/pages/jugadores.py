"""jugadores.py — Objetivos 5 y 7: dónde y cuándo juegan los usuarios."""
import plotly.express as px
import plotly.graph_objects as go
from dash import html
from plotly.subplots import make_subplots

from components import AMBER, PURPLE, SEQ_SCALE, graph_card, grid, pad_x, section_header, style
from data import S, activity_heatmap, activity_monthly, countries

DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


def map_fig():
    fig = px.choropleth(countries, locations="iso3", color="n_players", hover_name="country",
                        color_continuous_scale=SEQ_SCALE, custom_data=["pct_players"],
                        labels={"n_players": "Jugadores"})
    fig.update_traces(hovertemplate="<b>%{hovertext}</b><br>%{z:,} jugadores (%{customdata[0]:.1f}%)<extra></extra>",
                      marker_line_color="#0A0F1E")
    fig.update_geos(bgcolor="rgba(0,0,0,0)", showframe=False, showcoastlines=False, landcolor="#1A2236",
                    showland=True, showcountries=True, countrycolor="#0A0F1E", projection_type="natural earth",
                    lataxis_range=[-58, 85])
    fig.update_layout(coloraxis_colorbar=dict(title="", thickness=10, len=0.7))
    return style(fig, 400, legend=False)


def top_fig():
    df = countries.head(15).sort_values("n_players")
    fig = px.bar(df, x="n_players", y="country", orientation="h", color_discrete_sequence=[PURPLE],
                 text=df["pct_players"].map(lambda v: f"{v:.1f}%"),
                 labels={"n_players": "Jugadores", "country": ""})
    fig.update_traces(textposition="outside", cliponaxis=False)
    pad_x(fig, df["n_players"].max())
    return style(fig, 400, legend=False)


def monthly_fig():
    m = activity_monthly.iloc[:-1]  # el último mes está incompleto
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=m["month"], y=m["trophies"], name="Trofeos ganados", marker_color="#1D6FD1",
                         marker_line_width=0))
    fig.add_trace(go.Scatter(x=m["month"], y=m["active_players"], name="Jugadores activos",
                             line=dict(color=AMBER, width=2)), secondary_y=True)
    fig.update_yaxes(title_text="Trofeos", secondary_y=False)
    fig.update_yaxes(title_text="Jugadores activos", secondary_y=True, showgrid=False)
    style(fig, 360)
    fig.update_layout(bargap=0)
    return fig


def heat_fig():
    h = activity_heatmap.pivot(index="weekday", columns="hour", values="trophies").reindex(DIAS)
    fig = go.Figure(go.Heatmap(z=h.values, x=[f"{c:02d}" for c in h.columns], y=h.index,
                               colorscale=SEQ_SCALE, hovertemplate="%{y} %{x}:00<br>%{z:,} trofeos<extra></extra>",
                               colorbar=dict(thickness=10)))
    fig.update_xaxes(title_text="Hora registrada en el dataset", tickangle=0, dtick=2)
    fig.update_yaxes(autorange="reversed")
    return style(fig, 360, legend=False)


# Interpretaciones (gráficos fijos: no dependen de los filtros)
c1, c2 = countries.iloc[0], countries.iloc[1]
INTERP_MAP = (f"La audiencia está concentrada en pocos países: {S['top5_countries']} suman el "
              f"{S['top5_countries_pct']} de los jugadores y los otros {len(countries) - 5} países se reparten el "
              "resto. América y Europa occidental dominan la muestra.")
INTERP_TOP = (f"{c1['country']} tiene {c1['n_players'] / c2['n_players']:.1f} veces más jugadores que el segundo "
              f"país ({c2['country']}, {c2['pct_players']:.1f}%). Por eso, cualquier promedio global de la muestra "
              f"refleja sobre todo el comportamiento de los jugadores de {c1['country']}.")
pandemia = " (coincide con la pandemia)" if S["active_peak_year"] in ("2020", "2021") else ""
INTERP_MONTHLY = (f"Los jugadores activos al mes crecieron de {S['active_first_avg']} en {S['active_first_year']} a "
                  f"{S['active_peak_avg']} en {S['active_peak_year']}{pandemia} y bajaron a {S['active_last_avg']} en "
                  f"{S['active_last_year']}. Aun así, quien sigue activo gana más trofeos: "
                  f"{S['trophies_per_active_peak']} al mes por jugador en {S['active_peak_year']} frente a "
                  f"{S['trophies_per_active_last']} en {S['active_last_year']}. Los primeros años tienen menos "
                  "actividad en parte porque muchos de estos jugadores todavía no usaban PlayStation.")
INTERP_HEAT = (f"El fin de semana concentra el {S['weekend_pct']} de los trofeos (si se jugara igual todos los días "
               f"sería 28.6%). La actividad cae al mínimo a las {S['low_hour']} y sube desde la tarde hasta su "
               f"máximo a las {S['peak_hour']} (hora del dataset, probablemente UTC: es la tarde-noche en América).")

MAP, TOP, MONTHLY, HEAT = map_fig(), top_fig(), monthly_fig(), heat_fig()


def layout():
    return html.Div([
        section_header("Jugadores", "Desde dónde y cuándo juegan los usuarios de la muestra", "people",
                       ["Objetivo 5", "Objetivo 7"]),
        html.P("Esta página no usa los filtros del menú: describe a los jugadores, no a los juegos.",
               className="card-note", style={"marginTop": "-8px", "marginBottom": "12px"}),
        grid([
            graph_card("globe2", "Jugadores por país", "jug-map", height=400, figure=MAP, interp=INTERP_MAP),
            graph_card("geo-alt", "Top 15 países", "jug-top", height=400, figure=TOP, interp=INTERP_TOP,
                       note="Etiqueta: porcentaje del total de jugadores."),
        ], "grid-60-40"),
        grid([
            graph_card("activity", "Actividad mensual 2008–2024", "jug-monthly", figure=MONTHLY, interp=INTERP_MONTHLY,
                       note="Trofeos ganados por mes (barras) y jugadores que ganaron al menos uno (línea). "
                            "Se excluye el último mes porque está incompleto."),
            graph_card("calendar-week", "¿Qué día y a qué hora se juega más?", "jug-heat", figure=HEAT,
                       interp=INTERP_HEAT, note="Total de trofeos ganados por día de la semana y hora."),
        ]),
    ])
