"""
textos.py — Páginas de contexto: Introducción, Objetivos y Conclusiones.
Las cifras salen de summary.csv (las mismas que usa la app Shiny).
"""
from dash import dcc, html

from components import (ACCENT, AMBER, BLUE, GREEN, PURPLE, RED, card, grid, insight,
                        section_header, step)
from data import S, etl_quality

OBJETIVOS = [
    ("1", "Composición del catálogo", "Describir el catálogo por plataforma, género y publisher.", "/catalogo"),
    ("2", "Distribución de precios", "Analizar los precios por género y por plataforma.", "/precios"),
    ("3", "Precios entre monedas", "Comparar el precio en USD, EUR, GBP, JPY y RUB para ver en qué región sale más caro.", "/precios"),
    ("4", "Crecimiento del catálogo", "Describir cómo creció el número de lanzamientos por año y género.", "/catalogo"),
    ("5", "Distribución geográfica", "Mostrar desde qué países juegan los usuarios de la muestra.", "/jugadores"),
    ("6", "Juegos más populares", "Identificar los juegos con más compradores y su relación con el precio.", "/popularidad"),
    ("7", "Actividad en el tiempo", "Analizar la actividad de los jugadores (trofeos ganados) entre 2008 y 2024.", "/jugadores"),
    ("8", "Dificultad según trofeos", "Medir la dificultad de los juegos con la cantidad y la rareza de sus trofeos.", "/logros"),
    ("9", "Cambios de precio", "Revisar si los precios cambiaron entre las capturas de febrero de 2025.", "/precios"),
]


def introduccion():
    raw = etl_quality.groupby("tabla", sort=False)["filas_antes"].first()
    tablas = [
        ("games", "Ficha de cada juego: título, plataforma, géneros, publisher y fecha"),
        ("prices", "Precio en 5 monedas, capturado varias veces en febrero de 2025"),
        ("players", "Jugadores de la muestra y su país"),
        ("purchased_games", "Biblioteca de juegos comprados por cada jugador"),
        ("achievements", "Trofeos de cada juego y su rareza (Bronze a Platinum)"),
        ("history", "Cada trofeo ganado por cada jugador, con fecha y hora"),
    ]
    filas = [html.Tr([html.Td(html.Code(f"{t}.csv")), html.Td(f"{int(raw.get(t, 0)):,}", className="num"),
                      html.Td(d)]) for t, d in tablas]
    return html.Div([
        section_header("Introducción", "Contexto del mercado y pregunta de investigación", "book"),
        grid([
            card("info-circle", "Contexto", html.Div([
                html.P("PlayStation Store reúne decenas de miles de juegos digitales para PS3, PS4, PS5 y PS Vita, "
                       "desde producciones AAA de más de $60 hasta juegos indie de menos de $1. Como copiar un "
                       "juego digital casi no cuesta nada, el precio depende del género, del publisher y de la competencia."),
                html.P(["Este trabajo usa el dataset público ", html.Strong("Gaming Profiles 2025"),
                        " (Kruglov, Kaggle, licencia CC0), que reúne datos reales de Steam, PlayStation y Xbox. "
                        "Aquí se usan las 6 tablas del esquema ", html.Strong("PlayStation"), "."]),
                html.P(f"El catálogo tiene {S['n_games']} productos ({S['n_titles']} títulos distintos) y la muestra de "
                       f"jugadores reúne {S['n_players']} perfiles de {S['n_countries']} países."),
            ], className="text-card")),
            card("question-circle", "Pregunta de investigación", html.Div([
                html.Div("¿Qué patrones de catálogo, precio, audiencia, popularidad y dificultad caracterizan a "
                         "PlayStation Store según los datos de Gaming Profiles 2025?", className="question"),
                html.P("Subpreguntas:"),
                html.Ol([
                    html.Li("¿Qué plataformas, géneros y publishers dominan el catálogo y cómo creció?"),
                    html.Li("¿Cómo se distribuyen los precios y en qué moneda sale más caro un juego?"),
                    html.Li("¿Desde dónde y cuándo juegan los usuarios?"),
                    html.Li("¿Qué juegos son los más comprados y tiene relación con su precio?"),
                    html.Li("¿Qué tan difíciles son los juegos según sus trofeos?"),
                ]),
            ], className="text-card")),
        ]),
        card("database", "Tablas del dataset (esquema PlayStation)", html.Table([
            html.Thead(html.Tr([html.Th("Archivo"), html.Th("Filas crudas", className="num"), html.Th("Contenido")])),
            html.Tbody(filas),
        ], className="ps-table"), note="Fuente: kaggle.com/datasets/artyomkruglov/gaming-profiles-2025-steam-playstation-xbox"),
        html.Div(style={"height": "14px"}),
        card("diagram-3", "Flujo del proyecto", html.Div([
            step(1, "Extracción", "Lectura de las 6 tablas crudas (3,8 GB con las otras plataformas).", BLUE),
            step(2, "ETL", "Limpieza, precio vigente por juego, países a ISO-3 y agregados.", ACCENT),
            step(3, "EDA", "Distribuciones, comparaciones y tendencias por objetivo.", GREEN),
            step(4, "Dashboards", "La misma app en Dash (Python) y en Shiny (R).", PURPLE),
            step(5, "Conclusiones", "Hallazgos por objetivo y limitaciones de los datos.", AMBER),
        ], className="step-grid")),
    ])


def objetivos():
    tarjetas = [
        dcc.Link(html.Div([
            html.Div(num, className="step-num"),
            html.Div(t, className="step-title"),
            html.P(d, className="step-desc"),
        ], className="step", style={"--step-color": c, "height": "100%"}), href=href, style={"textDecoration": "none"})
        for (num, t, d, href), c in zip(OBJETIVOS, [BLUE, ACCENT, GREEN, BLUE, PURPLE, AMBER, PURPLE, RED, ACCENT])
    ]
    return html.Div([
        section_header("Objetivos", "Qué busca responder el dashboard", "bullseye"),
        card("flag", "Objetivo general", html.Div(html.P(
            "Construir un dashboard interactivo que permita explorar el catálogo, los precios y el comportamiento de "
            "los jugadores de PlayStation Store, para identificar patrones del mercado y apoyar decisiones de "
            "desarrolladores, publishers y jugadores."), className="text-card")),
        html.Div(style={"height": "14px"}),
        card("list-check", "Objetivos específicos (clic para ir a la página)",
             html.Div(tarjetas, className="step-grid")),
        html.Div(style={"height": "14px"}),
        card("signpost-split", "Cómo se organiza el dashboard", html.Div([
            insight("Catálogo:", "objetivos 1 y 4."),
            insight("Precios:", "objetivos 2, 3 y 9."),
            insight("Jugadores:", "objetivos 5 y 7."),
            insight("Popularidad:", "objetivo 6."),
            insight("Logros:", "objetivo 8."),
        ])),
    ])


def conclusiones():
    return html.Div([
        section_header("Conclusiones", "Hallazgos por objetivo y limitaciones", "check2-circle"),
        grid([
            card("lightbulb", "Hallazgos", html.Div([
                insight("1. Catálogo:", f"{S['top_platform']} concentra el {S['top_platform_pct']} del catálogo; "
                        f"{S['top_genre']} es el género principal más común ({S['top_genre_pct']}) y "
                        f"{S['top_publisher']} es el publisher con más productos ({S['top_publisher_n']})."),
                insight("2. Precios:", f"La mediana es {S['median_price']} y el {S['pct_under_10']} de los juegos cuesta "
                        f"menos de $10. {S['priciest_genre']} es el género más caro (mediana {S['priciest_genre_median']}) "
                        f"y {S['cheapest_genre']} el más barato ({S['cheapest_genre_median']})."),
                insight("3. Monedas:", f"Convertido a dólares, un juego cuesta en mediana {S['priciest_currency_diff']} "
                        f"más en {S['priciest_currency']} y {S['cheapest_currency_diff']} en {S['cheapest_currency']} "
                        "frente a su precio en USD."),
                insight("4. Crecimiento:", f"Los lanzamientos pasaron de {S['launches_2015']} en 2015 a "
                        f"{S['launches_2024']} en 2024 ({S['growth_2015_2024']}); el pico fue {S['peak_year']}."),
                insight("5. Geografía:", f"{S['top_country']} aporta el {S['top_country_pct']} de los jugadores y los "
                        f"5 primeros países suman el {S['top5_countries_pct']}."),
                insight("6. Popularidad:", f"{S['top_owned_game']} está en el {S['top_owned_pct']} de las bibliotecas. "
                        f"La correlación de Spearman entre precio y compradores es {S['spearman_price_owners']}: "
                        "el precio casi no explica la popularidad."),
                insight("7. Actividad:", f"El mes con más trofeos fue {S['peak_month']}; la hora con más actividad es "
                        f"las {S['peak_hour']} (probablemente UTC) y el día, {S['peak_weekday']}."),
                insight("8. Dificultad:", f"Un juego tiene en mediana {S['median_trophies']} trofeos. El Platinum lo "
                        f"consigue en mediana el {S['earn_platinum']} de sus jugadores, frente al {S['earn_bronze']} de un Bronze."),
                insight("9. Cambios de precio:", f"Solo {S['n_price_changed']} de {S['n_multi_snapshot']} juegos "
                        f"({S['pct_price_changed']}) cambiaron de precio entre capturas: los precios fueron estables."),
            ])),
            card("exclamation-triangle", "Limitaciones", html.Div([
                insight("Precios de 2025:", "las capturas son de 4 días de febrero de 2025. No hay historial de precios, "
                        "así que no se puede medir la evolución de precios a lo largo de los años.", warn=True),
                insight("Muestra de jugadores:", f"los datos de jugadores no son un censo de PlayStation. Solo "
                        f"{S['n_players_library']} perfiles tienen biblioteca pública.", warn=True),
                insight("Compras ≠ ventas:", "la popularidad cuenta cuántos jugadores de la muestra tienen el juego, no "
                        "las unidades vendidas.", warn=True),
                insight("Ediciones regionales:", f"un mismo título puede aparecer varias veces ({S['n_games']} productos, "
                        f"{S['n_titles']} títulos). Se analizan como productos distintos de la tienda.", warn=True),
                insight("Tasas de cambio:", "la comparación de monedas usa tasas aproximadas del 24-feb-2025.", warn=True),
                insight("Último mes:", f"la actividad de {S['last_month']} está incompleta y no se usa para el pico.", warn=True),
            ])),
        ]),
    ])
