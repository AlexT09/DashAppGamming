# PS Gaming Analytics 2025 · Dashboard en Dash

Dashboard interactivo en **Python (Dash + Plotly)** sobre el catálogo, los precios, los jugadores, la popularidad y los trofeos de **PlayStation Store**.

La misma aplicación existe en **R / Shiny**, junto con el informe en bookdown, en el repositorio [ShinyAppGamming](https://github.com/AlexT09/ShinyAppGamming). Las dos versiones leen los mismos datos procesados, tienen las mismas páginas y muestran las mismas cifras.

## Dataset

[Gaming Profiles 2025](https://www.kaggle.com/datasets/artyomkruglov/gaming-profiles-2025-steam-playstation-xbox) (Kruglov, Kaggle, licencia CC0): datos reales de Steam, PlayStation y Xbox (~60 GB en total). Este proyecto usa las 6 tablas del esquema **PlayStation**:

| Tabla | Contenido |
|---|---|
| `games` | Ficha de cada juego: título, plataforma, géneros, publisher y fecha |
| `prices` | Precio en USD, EUR, GBP, JPY y RUB, capturado cada 2 días desde el 22-02-2025 |
| `players` | 356 mil jugadores y su país |
| `purchased_games` | Biblioteca de juegos comprados por cada jugador |
| `achievements` | Trofeos de cada juego y su rareza |
| `history` | Trofeos ganados por cada jugador entre 2008 y 2024 (46 mil jugadores) |

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

El dashboard tiene además las páginas Resumen, Introducción, Objetivos, ETL, Explorador y Conclusiones. Cada gráfico tiene debajo una **interpretación** que se recalcula con los filtros globales (plataforma, género y año).

## Hallazgos principales

- El catálogo tiene **23,151 productos** (11,153 títulos únicos); PS4 concentra el 61.2% y los lanzamientos crecieron un 838% entre 2015 y 2024.
- El precio mediano es **$7.99** y el 62.1% de los juegos cuesta menos de $10.
- El mismo juego cuesta en mediana un **5% más en euros** y un **19% menos en rublos** que en dólares.
- La popularidad casi no depende del precio (Spearman 0.02): *Grand Theft Auto V* está en el 66% de las bibliotecas.
- El Platinum lo consigue en mediana solo el **19.5%** de los jugadores de un juego.

## Ejecutar el dashboard

Requiere Python 3.10 o superior.

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
python dash_app/app.py            # http://127.0.0.1:8050
```

Con Docker: `docker compose up --build` y abrir http://localhost:8050.

## Regenerar los datos (ETL)

Los datos procesados ya vienen en `data/processed/`. El ETL solo hace falta si cambias el código o descargas otra versión del dataset:

1. Descarga el dataset de Kaggle y descomprímelo en la carpeta `dataset/` del repo (debe quedar `dataset/playstation/`) o en `data/raw/`. Esas carpetas están en `.gitignore`.
2. Ejecuta `python etl/etl_playstation.py` (o `--raw "ruta/a/playstation"`). Tarda unos 3 minutos y usa menos de 1 GB de RAM porque lee `history.csv` (800 MB) por partes.
3. Si solo cambias los textos de resumen, basta con `python etl/build_summary.py`.

Si regeneras los datos, cópialos también a `data/processed/` del repo de Shiny.

## Estructura

```text
DashAppGamming/
├── etl/
│   ├── etl_playstation.py   # ETL de las 6 tablas crudas
│   └── build_summary.py     # cifras clave que usan los textos (summary.csv)
├── data/processed/          # 13 tablas limpias (~8 MB) que lee el dashboard
├── dash_app/
│   ├── app.py               # menú lateral, filtros globales y rutas
│   ├── data.py              # carga de data/processed/
│   ├── components.py        # colores, estilo de gráficos y bloques de interfaz
│   ├── pages/               # una página por sección (catalogo.py, precios.py, ...)
│   └── assets/ps-theme.css  # tema compartido con la app Shiny
├── Dockerfile, docker-compose.yml
└── requirements.txt
```

## Autor

**Alex Terán** · Curso de Visualización de Datos.
