"""
components.py — Colores, estilo de gráficos y bloques de interfaz.

Los mismos colores y clases CSS se usan en la app Shiny (ShinyAppGamming),
para que los dos dashboards se vean iguales.
"""
from __future__ import annotations

import plotly.graph_objects as go
from dash import dcc, html

# ── Paleta ────────────────────────────────────────────────────────────────────
BLUE, ACCENT, GREEN, AMBER, RED, PURPLE = "#0070D1", "#00AAFF", "#22C55E", "#F59E0B", "#EF4444", "#A78BFA"
TEXT, MUTED, BORDER, CARD = "#F0F4FF", "#8B9BB4", "#1E2D4A", "#111827"

PLATFORM_COLORS = {"PS3": "#8B9BB4", "PS4": BLUE, "PS5": "#7FD3F7", "PS Vita": PURPLE}
RARITY_COLORS = {"Bronze": "#CD7F32", "Silver": "#C0C7D1", "Gold": "#F5B700", "Platinum": "#7FD3F7"}
CURRENCY_COLORS = {"USD": BLUE, "EUR": GREEN, "GBP": PURPLE, "JPY": AMBER, "RUB": RED}
CAT_COLORS = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A", "#19D3F3"]  # géneros (mismo orden en Shiny)
SEQ_SCALE =[[0, "#13294B"], [0.5, BLUE], [1, ACCENT]]


def style(fig: go.Figure, height: int = 340, legend: bool = True) -> go.Figure:
    """Estilo oscuro común a todos los gráficos."""
    fig.update_layout(
        height=height,
        font=dict(family="Inter, Segoe UI, Arial, sans-serif", size=12, color=MUTED),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=16, t=16, b=10),
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0,
                    bgcolor="rgba(0,0,0,0)", font=dict(color=MUTED), title_text=""),
        hoverlabel=dict(bgcolor=CARD, bordercolor=BORDER, font=dict(color=TEXT)),
        coloraxis_colorbar=dict(tickfont=dict(color=MUTED), title=dict(font=dict(color=MUTED))),
    )
    fig.update_xaxes(gridcolor=BORDER, linecolor=BORDER, zerolinecolor=BORDER, title_font=dict(color=MUTED))
    fig.update_yaxes(gridcolor=BORDER, linecolor=BORDER, zerolinecolor=BORDER, title_font=dict(color=MUTED))
    return fig


def pad_x(fig: go.Figure, max_value: float, factor: float = 1.18) -> go.Figure:
    """Deja espacio a la derecha para que no se corten las etiquetas de barras horizontales."""
    fig.update_xaxes(range=[0, max_value * factor])
    return fig


def empty(msg: str = "Sin datos para los filtros elegidos", height: int = 340) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=msg, showarrow=False, font=dict(color=MUTED, size=13))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return style(fig, height, legend=False)


# ── Bloques de interfaz ───────────────────────────────────────────────────────
def section_header(title: str, subtitle: str, icon: str, tags: list[str] | None = None):
    return html.Div([
        html.I(className=f"bi bi-{icon}"),
        html.Div([html.H4(title), html.P(subtitle)]),
        html.Div([html.Span(t, className="tag") for t in (tags or [])], className="objective-tags"),
    ], className="section-header")


def interp_children(text: str):
    """Contenido del bloque 'Interpretación' que va debajo de cada gráfico."""
    return [html.Strong("Interpretación: "), text]


def card(icon: str, title: str, body, note: str | None = None, interp: str | None = None,
         interp_id: str | None = None):
    children = [body] if not isinstance(body, list) else body
    if note:
        children = children + [html.P(note, className="card-note")]
    if interp_id:
        children = children + [html.Div(id=interp_id, className="interp")]
    elif interp:
        children = children + [html.Div(interp_children(interp), className="interp")]
    return html.Div([
        html.Div([html.I(className=f"bi bi-{icon}"), html.Span(title)], className="ps-card-header"),
        html.Div(children, className="ps-card-body"),
    ], className="ps-card")


def graph_card(icon: str, title: str, graph_id: str, note: str | None = None, height: int = 340,
               figure: go.Figure | None = None, interp: str | None = None, dynamic: bool = False):
    """Tarjeta con gráfico. dynamic=True crea el bloque '<graph_id>-interp' que llena un callback."""
    extra = {"figure": figure} if figure is not None else {}
    graph = dcc.Graph(id=graph_id, config={"displayModeBar": False, "responsive": True},
                      style={"height": f"{height}px"}, **extra)
    return card(icon, title, dcc.Loading(graph, color=ACCENT, type="dot"), note, interp,
                f"{graph_id}-interp" if dynamic else None)


def kpi(label: str, value: str, sub: str = "", color: str = BLUE):
    return html.Div([
        html.Div(label, className="kpi-label"),
        html.Div(value, className="kpi-value"),
        html.Div(sub, className="kpi-sub"),
    ], className="kpi-box", style={"--kpi-color": color})


def grid(children, cols: str = "grid-2"):
    return html.Div(children, className=f"grid {cols}")


def insight(title: str, text: str, warn: bool = False):
    return html.Div([html.Strong(f"{title} "), text], className="insight-box warn" if warn else "insight-box")


def step(num, title: str, desc: str, color: str = BLUE):
    return html.Div([
        html.Div(str(num), className="step-num"),
        html.Div(title, className="step-title"),
        html.P(desc, className="step-desc"),
    ], className="step", style={"--step-color": color})


def fmt_int(n) -> str:
    return f"{int(n):,}"


def fmt_usd(x) -> str:
    return f"${x:,.2f}"
