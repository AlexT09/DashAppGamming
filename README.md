# PS Gaming Analytics 2025 · Dashboard en Dash

Dashboard interactivo en **Python (Dash + Plotly)** sobre el catálogo, los precios, los jugadores, la popularidad y los trofeos de **PlayStation Store**, con el dataset público [Gaming Profiles 2025](https://www.kaggle.com/datasets/artyomkruglov/gaming-profiles-2025-steam-playstation-xbox) (Kaggle, CC0).

La misma aplicación existe en **R / Shiny**, junto con el informe en bookdown, en el repositorio [ShinyAppGamming](https://github.com/AlexT09/ShinyAppGamming). Las dos versiones leen los mismos datos procesados, tienen las mismas páginas y muestran las mismas cifras.

## Pregunta de investigación

> ¿Qué patrones de catálogo, precio, audiencia, popularidad y dificultad caracterizan a PlayStation Store según los datos de Gaming Profiles 2025?

| # | Objetivo | Página del dashboard |
|---|---|---|
| 1 | Composición del catálogo por plataforma, género y publisher | Catálogo |
| 2 | Distribución de precios por género y plataforma | Precios |
| 3 | Comparación de precios entre USD, EUR, GBP, JPY y RUB | Precios |
| 4 | Crecimiento del catálogo por año y género | Catálogo |
| 5 | Distribución geográfica de los jugadores | Jugadores |
| 6 | Juegos más comprados y su relación con el precio | Popularidad |
| 7 | Actividad de los jugadores en el tiempo (2008–2024) | Jugadores |
| 8 | Dificultad de los juegos según sus trofeos | Logros |
| 9 | Cambios de precio entre capturas de febrero de 2025 | Precios |

Cada gráfico tiene debajo una **interpretación** que se recalcula con los filtros globales (plataforma, género y año).

## Hallazgos principales

- El catálogo tiene **23,151 productos** (11,153 títulos únicos); PS4 concentra el 61.2% y los lanzamientos crecieron un 838% entre 2015 y 2024.
- El precio mediano es **$7.99** y el 62.1% de los juegos cuesta menos de $10.
- El mismo juego cuesta en mediana un **5% más en euros** y un **19% menos en rublos** que en dólares.
- La popularidad casi no depende del precio (Spearman 0.02): *Grand Theft Auto V* está en el 66% de las bibliotecas.
- El Platinum lo consigue en mediana solo el **19.5%** de los jugadores de un juego.

## Estructura

```text
DashAppGamming/
├── etl/
│   ├── etl_playstation.py   # ETL de las 6 tablas crudas (lee history.csv por partes)
│   └── build_summary.py     # cifras clave que usan los textos (summary.csv)
├── data/processed/          # 13 tablas limpias (~10 MB) que lee el dashboard
├── dash_app/
│   ├── app.py               # menú lateral, filtros globales y rutas
│   ├── data.py              # carga de data/processed/
│   ├── components.py        # colores, estilo de gráficos y bloques de interfaz
│   ├── pages/               # una página por sección (catalogo.py, precios.py, ...)
│   └── assets/ps-theme.css  # tema compartido con la app Shiny
├── Dockerfile, docker-compose.yml
├── requirements.txt
├── Contexto.md              # descripción original del dataset en Kaggle
└── INSTRUCCIONES.md         # cómo ejecutar todo paso a paso
```

## Ejecución rápida

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
python dash_app/app.py            # http://127.0.0.1:8050
```

Los datos procesados ya vienen en el repositorio. El ETL solo hace falta para regenerarlos; ver [INSTRUCCIONES.md](INSTRUCCIONES.md).

## Autor

**Alex Terán** · Curso de Visualización de Datos.
