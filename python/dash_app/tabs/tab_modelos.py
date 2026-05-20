"""
tab_modelos.py — Pestaña de métricas de modelos predictivos
PlayStation Gaming Analytics 2025
"""

import sys
import os as _os

sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

PS_BLUE = "#003087"
PS_RED = "#E63946"
PS_GOLD = "#F4A261"
PS_DARK = "#001A52"

# Métricas reales calculadas con train/test split 80/20 (random_state=42)
METRICS = {
    "Lasso Regression": {"r2": 0.0244, "rmse": 11.74, "mae": 8.74},
    "Random Forest": {"r2": 0.2406, "rmse": 10.36, "mae": 7.22},
    "XGBoost": {"r2": 0.2913, "rmse": 10.01, "mae": 7.01},
}

BEST_MODEL = "XGBoost"


def _metrics_table():
    rows = []
    for nombre, m in METRICS.items():
        rows.append({
            "Modelo": nombre,
            "R²": f"{m['r2']:.4f}",
            "RMSE ($)": f"${m['rmse']:.2f}",
            "MAE ($)": f"${m['mae']:.2f}",
        })
    return dash_table.DataTable(
        data=rows,
        columns=[{"name": c, "id": c} for c in ["Modelo", "R²", "RMSE ($)", "MAE ($)"]],
        style_cell={
            "textAlign": "center",
            "fontFamily": "Inter, Segoe UI, Arial",
            "fontSize": "0.9rem",
            "backgroundColor": "#111827",
            "color": "#F0F4FF",
            "border": "1px solid #1E2D4A",
            "padding": "8px 12px",
        },
        style_header={
            "backgroundColor": "#0D1426",
            "color": "#8B9BB4",
            "fontWeight": "600",
            "fontSize": "11px",
            "textTransform": "uppercase",
            "letterSpacing": ".06em",
        },
        style_data_conditional=[
            {
                "if": {"filter_query": "{Modelo} = 'XGBoost'"},
                "backgroundColor": "#0D1F3C",
                "color": "#00AAFF",
                "fontWeight": "bold",
            }
        ],
        style_table={"overflowX": "auto"},
    )


def _metrics_chart():
    """Tres paneles con escalas propias: R² (0–1) no debe compartir eje con RMSE/MAE en USD."""
    modelos = list(METRICS.keys())
    r2s = [METRICS[m]["r2"] for m in modelos]
    rmses = [METRICS[m]["rmse"] for m in modelos]
    maes = [METRICS[m]["mae"] for m in modelos]

    fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=(
            "R² (mayor es mejor)",
            "RMSE USD (menor es mejor)",
            "MAE USD (menor es mejor)",
        ),
        horizontal_spacing=0.06,
    )
    fig.add_trace(
        go.Bar(
            x=modelos,
            y=r2s,
            marker_color=PS_BLUE,
            showlegend=False,
            text=[f"{v:.3f}" for v in r2s],
            textposition="outside",
        ),
        1,
        1,
    )
    fig.add_trace(
        go.Bar(
            x=modelos,
            y=rmses,
            marker_color=PS_RED,
            showlegend=False,
            text=[f"${v:.2f}" for v in rmses],
            textposition="outside",
        ),
        1,
        2,
    )
    fig.add_trace(
        go.Bar(
            x=modelos,
            y=maes,
            marker_color=PS_GOLD,
            showlegend=False,
            text=[f"${v:.2f}" for v in maes],
            textposition="outside",
        ),
        1,
        3,
    )
    fig.update_xaxes(tickangle=-15)
    fig.update_yaxes(gridcolor="#e0e8ff")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI, Arial", size=12),
        title=dict(
            text="Comparación de métricas por modelo (escalas separadas)",
            font=dict(color=PS_BLUE),
        ),
        margin=dict(t=80, b=80),
        height=400,
    )
    return fig


def create_layout():
    _dark_card = {"background": "#111827", "border": "1px solid #1E2D4A", "borderRadius": "12px"}

    return html.Div([
        html.H4(
            " Métricas de Modelos Predictivos",
            style={"color": "#F0F4FF", "fontWeight": "bold"},
        ),
        html.P(
            "Comparación de Lasso Regression, Random Forest y XGBoost para predecir precios en PS Store.",
            style={"color": "#8B9BB4"},
        ),
        html.Hr(style={"borderColor": "#1E2D4A"}),
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(
                        html.B(" Mejor Modelo"),
                        style={
                            "background": "#0A2818",
                            "borderBottom": "1px solid #1E2D4A",
                            "color": "#F0F4FF",
                        },
                    ),
                    dbc.CardBody([
                        html.H3(BEST_MODEL, style={"color": "#00AAFF", "textAlign": "center"}),
                        html.Div([
                            html.P(
                                [html.B("R² = "), f"{METRICS[BEST_MODEL]['r2']:.4f}"],
                                style={"color": "#0070D1", "fontSize": "1.1rem", "textAlign": "center"},
                            ),
                            html.P(
                                [html.B("RMSE = "), f"${METRICS[BEST_MODEL]['rmse']:.2f}"],
                                style={"color": "#EF4444", "textAlign": "center"},
                            ),
                            html.P(
                                [html.B("MAE = "), f"${METRICS[BEST_MODEL]['mae']:.2f}"],
                                style={"color": "#F59E0B", "textAlign": "center"},
                            ),
                        ], style={"backgroundColor": "#0D1F3C", "borderRadius": "8px", "padding": "12px"}),
                    ]),
                ], style=_dark_card),
                md=4,
            ),
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(
                        html.B(" Tabla Comparativa"),
                        style={
                            "background": "#001A52",
                            "borderBottom": "1px solid #1E2D4A",
                            "color": "#F0F4FF",
                        },
                    ),
                    dbc.CardBody(_metrics_table()),
                ], style=_dark_card),
                md=8,
            ),
        ], className="mb-4"),
        dbc.Card([
            dbc.CardHeader(
                html.B(" Comparación Visual"),
                style={
                    "background": "#001A52",
                    "borderBottom": "1px solid #1E2D4A",
                    "color": "#F0F4FF",
                },
            ),
            dbc.CardBody(dcc.Graph(figure=_metrics_chart(), config={"displayModeBar": False})),
        ], style=_dark_card, className="mb-4"),
        dbc.Card([
            dbc.CardHeader(
                html.B(" ¿Por qué XGBoost es el mejor modelo?"),
                style={
                    "background": "#0A1E2E",
                    "borderBottom": "1px solid #1E2D4A",
                    "color": "#F0F4FF",
                },
            ),
            dbc.CardBody([
                html.Ul([
                    html.Li(
                        [
                            html.B("Precisión superior: "),
                            "R² de 0.2913 vs 0.2406 (Random Forest) y 0.0244 (Lasso).",
                        ],
                        style={"color": "#B8C9E4", "marginBottom": "6px"},
                    ),
                    html.Li(
                        [
                            html.B("Captura no-linealidades: "),
                            "Detecta interacciones entre género, plataforma y año que Lasso no puede modelar.",
                        ],
                        style={"color": "#B8C9E4", "marginBottom": "6px"},
                    ),
                    html.Li(
                        [
                            html.B("Regularización integrada: "),
                            "XGBoost incorpora L1 y L2 automáticamente, previniendo sobreajuste.",
                        ],
                        style={"color": "#B8C9E4", "marginBottom": "6px"},
                    ),
                    html.Li(
                        [
                            html.B("Menor error de predicción: "),
                            "MAE de $7.01 — el error promedio por predicción es el más bajo de los tres modelos.",
                        ],
                        style={"color": "#B8C9E4", "marginBottom": "6px"},
                    ),
                    html.Li(
                        [
                            html.B("Balance sesgo-varianza: "),
                            "El boosting secuencial corrige iterativamente los errores residuales.",
                        ],
                        style={"color": "#B8C9E4", "marginBottom": "6px"},
                    ),
                    html.Li(
                        [
                            html.B("Nota sobre R²: "),
                            "El R² de 0.29 indica que el precio depende también de variables no disponibles "
                            "(publisher, franquicia, historial de descuentos). XGBoost sigue siendo el mejor "
                            "con las variables disponibles.",
                        ],
                        style={"color": "#B8C9E4", "marginBottom": "6px"},
                    ),
                ]),
                html.Hr(style={"borderColor": "#1E2D4A"}),
                html.P(
                    "Modelos entrenados con 80% de los datos y evaluados en 20% de prueba (random_state=42).",
                    style={"color": "#8B9BB4", "fontSize": "0.85rem"},
                ),
            ]),
        ], style=_dark_card),
    ], style={"padding": "10px"})
