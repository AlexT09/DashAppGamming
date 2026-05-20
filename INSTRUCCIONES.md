# Instrucciones de Ejecución — PS Gaming Analytics 2025

Guía paso a paso para ejecutar cada componente del proyecto.

---

## Requisitos Previos

| Software | Versión mínima |
|----------|---------------|
| Python | 3.10+ |
| R | 4.2+ |
| Git | cualquiera |

---

## 1⃣ Dashboard Python (Dash)

### Opción A: Ejecución Local

```bash
cd python/dash_app
python3 -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
# Abrir: http://127.0.0.1:8050
```

### Opción B: Con Docker

```bash
cd python/dash_app
docker compose up --build
# Abrir: http://localhost:8050
```

### Rutas disponibles

| URL | Sección |
|-----|---------|
| `http://127.0.0.1:8050/` | Resumen |
| `http://127.0.0.1:8050/introduccion` | Introducción |
| `http://127.0.0.1:8050/objetivos` | Objetivos |
| `http://127.0.0.1:8050/metodologia` | Metodología |
| `http://127.0.0.1:8050/eda` | EDA Completo |
| `http://127.0.0.1:8050/simulador` | Simulador |
| `http://127.0.0.1:8050/modelos` | Métricas Modelos |
| `http://127.0.0.1:8050/prediccion` | Predictor XGBoost |
| `http://127.0.0.1:8050/explorador` | Explorador |

---

## 2⃣ Jupyter Notebook (Python)

```bash
cd python
pip install pandas numpy matplotlib scikit-learn xgboost jupyter
jupyter notebook notebook_ps_gaming.ipynb
```

También puedes abrirlo en Google Colab:
1. Ir a [colab.research.google.com](https://colab.research.google.com)
2. Subir `notebook_ps_gaming.ipynb` y los 3 CSV de `data/`
3. Ejecutar todo

---

## 3⃣ Dashboard Shiny (R)

### Desde RStudio

```r
setwd("r/shiny_app")

install.packages(c(
 "shiny", "shinydashboard", "tidyverse", "plotly",
 "DT", "scales", "lubridate", "caret", "randomForest", "xgboost"
))

shiny::runApp()
# Abre en navegador puerto 3838
```

### Desde línea de comandos

```bash
R -e "shiny::runApp('r/shiny_app')"
```

### Pestañas disponibles

| Pestaña | Descripción |
|---------|-------------|
| Introducción | Contexto y pregunta de investigación |
| Objetivos | Metas del análisis |
| Metodología | Flujo ETL |
| Resumen | KPIs generales |
| Catálogo | Géneros, publishers, tabla completa |
| Jugadores | Distribución geográfica |
| Precios | Histogramas, monedas, correlaciones |
| Simulador | Benchmarks descriptivos |
| Calidad | % valores faltantes |
| Explorador | Tabla interactiva |
| Modelos ML | Métricas Lasso / RF / XGBoost |
| Predictor | Predicción con mejor modelo |

---

## 4⃣ Reporte Bookdown (R Markdown)

### Desde RStudio

```r
setwd("r/bookdown")

install.packages(c("bookdown", "tidyverse", "knitr", "kableExtra",
 "corrplot", "ggrepel", "glmnet", "randomForest", "xgboost"))

bookdown::render_book("index.Rmd", "bookdown::gitbook")
# Resultado: r/bookdown/docs/index.html
```

### Publicar en GitHub Pages

```bash
git add r/bookdown/docs
git commit -m "actualizar libro"
git push
# En GitHub: Settings → Pages → Branch: main → Folder: /docs
```

---

## Checklist de Ejecución

- [ ] Python >= 3.10 instalado
- [ ] R >= 4.2 instalado
- [ ] Dash ejecutándose en puerto 8050
- [ ] Shiny ejecutándose en puerto 3838
- [ ] Bookdown compilado en `r/bookdown/docs/index.html`
- [ ] Notebook ejecutado sin errores
- [ ] Los 3 componentes cargan datos sin errores

---

**Última actualización:** Mayo 2025 
**Curso:** Visualización de Datos 
**Grupo:** 13
