# Instrucciones de ejecución

## Requisitos

| Software | Versión |
|---|---|
| Python | 3.10 o superior |
| Git | cualquiera |
| Docker (opcional) | cualquiera |

## 1. Dashboard (Dash)

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
python dash_app/app.py
```

Abrir **http://127.0.0.1:8050**.

| Ruta | Página |
|---|---|
| `/` | Resumen (KPIs e insights) |
| `/introduccion` | Contexto, pregunta de investigación y tablas del dataset |
| `/objetivos` | Objetivo general y los 9 objetivos específicos |
| `/etl` | Pasos del ETL, registro de calidad y valores faltantes |
| `/catalogo` | Objetivos 1 y 4 |
| `/precios` | Objetivos 2, 3 y 9 |
| `/jugadores` | Objetivos 5 y 7 |
| `/popularidad` | Objetivo 6 |
| `/logros` | Objetivo 8 |
| `/explorador` | Tabla filtrable del catálogo limpio |
| `/conclusiones` | Hallazgos y limitaciones |

## 2. Con Docker

```bash
docker compose up --build
```

Abrir **http://localhost:8050**. La imagen usa `gunicorn` y solo copia `dash_app/` y `data/processed/`.

## 3. Regenerar los datos (ETL)

Solo hace falta si cambias el ETL o descargas una versión nueva del dataset.

1. Descarga el dataset de [Kaggle](https://www.kaggle.com/datasets/artyomkruglov/gaming-profiles-2025-steam-playstation-xbox) (~1 GB comprimido, 3,8 GB descomprimido).
2. Descomprímelo dentro del repositorio (por ejemplo en `archive (19)/`) o en `data/raw/`. Esas carpetas están en `.gitignore`, así que no se suben.
3. Ejecuta:

```bash
python etl/etl_playstation.py                          # busca la carpeta playstation/ sola
python etl/etl_playstation.py --raw "ruta/a/playstation"   # o indícala
```

Tarda unos 3 minutos y usa menos de 1 GB de RAM. Al final escribe las 13 tablas en `data/processed/` y `summary.csv` con las cifras clave. Si solo cambias los textos de resumen, basta con `python etl/build_summary.py`.

## 4. Versión en R (Shiny + bookdown)

Está en el repositorio [ShinyAppGamming](https://github.com/AlexT09/ShinyAppGamming), con sus propias instrucciones. Usa los mismos archivos de `data/processed/`; si regeneras los datos aquí, cópialos también allá.

## Checklist

- [ ] `pip install -r requirements.txt` sin errores
- [ ] `python dash_app/app.py` abre en el puerto 8050
- [ ] Las 11 páginas cargan y los filtros cambian gráficos e interpretaciones
- [ ] (Opcional) `python etl/etl_playstation.py` termina con "Listo"
