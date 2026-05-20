# PlayStation Gaming Analytics — Dashboard Shiny (R)

## Descripción

Aplicación web interactiva en **R** con **Shiny** y **Plotly** para análisis exploratorio (EDA) del catálogo PlayStation 2025. Implementa técnicas de visualización dinámica del curso: gráficos reactivos, filtros globales, y diseño profesional con shinydashboard.

**Características:**
- **7 pestañas temáticas**: Resumen, Catálogo, Jugadores, Precios, Simulador, Calidad Datos, Explorador
- **KPIs dinámicos**: Actualizados en tiempo real con filtros
- **Gráficos Plotly**: Interactividad (zoom, hover, leyendas dinámicas)
- **Tabla explorador**: DataTable con búsqueda y paginación
- **Análisis geográfico**: Jugadores por país, burbujas, proporciones
- **Análisis de precios**: Distribuciones, monedas, correlaciones
- **Filtros globales**: Plataforma y año se aplican a todo el dashboard

---

## Instalación

### Requisitos
- **R** >= 4.0
- **Librería Shiny** + dependencias

### Setup

```r
# Instalar paquetes (si no los tienes)
install.packages(c(
 "shiny",
 "shinydashboard",
 "tidyverse",
 "plotly",
 "DT",
 "scales",
 "lubridate",
 "caret",
 "randomForest",
 "glmnet",
 "xgboost"
))
```

### Ejecutar

```r
# Opción 1: Desde RStudio
setwd(".../shiny_app")
shiny::runApp()

# Opción 2: Desde línea de comandos R
R -e "shiny::runApp('shiny_app')"
```

**Abrir navegador:** http://127.0.0.1:3838 (por defecto)

---

## Estructura

```
shiny_app/
 app.R # Aplicación Shiny única (UI + Server)
 README.md
 data/
 games.csv # ~23.000 juegos PlayStation
 players.csv # ~1.500 perfiles de jugadores
 prices.csv # ~20.000 precios en múltiples monedas
```

---

## Pestañas (Tabs)

| Pestaña | Contenido |
|---------|-----------|
| ** Resumen** | KPIs globales, gráficos resumen, insights clave |
| ** Catálogo** | Top géneros, publishers, precio promedio, tabla completa |
| ** Jugadores** | Distribución por país, burbujas, pie chart (top 6) |
| ** Precios** | Histograma, rangos, boxplots monedas, correlaciones |
| ** Simulador** | Benchmark (mediana + Q1–Q3) por género/plataforma |
| ** Calidad Datos** | % de valores faltantes por dataset (CSV crudo) |
| ** Explorador** | Tabla interactiva con búsqueda, filtro, paginación |

---

## Diseño Visual

- **Paleta PlayStation**: Azul (#003087), Rojo (#E63946), Oro (#F4A261), Gris oscuro (#001A52)
- **Tema shinydashboard**: Skin "blue" personalizado con CSS
- **Tipografía**: Segoe UI, Arial (sin serif para legibilidad)
- **Layout responsivo**: Funciona en desktop, tablet y móvil (media queries)

---

## Técnicas Aplicadas

| Aspecto | Técnica | Detalles |
|--------|---------|----------|
| **Transformación datos** | Tidyverse (dplyr, tidyr) | `separate_rows()` para expandir géneros |
| **Visualización** | Plotly (ggplotly) | Gráficos interactivos con hover |
| **Reactividad** | `reactive()` + `observeEvent()` | Filtros globales actualizan todos los gráficos |
| **Tablas** | DataTable (DT) | Búsqueda nativa, paginación |
| **Escalas** | scales R | Formateo moneda, porcentajes |
| **Fechas** | lubridate | Análisis temporal de lanzamientos |

---

## Decisiones de Diseño

1. **Archivo único (app.R)**: Simplicidad operacional; fácil de desplegar
2. **Filtros globales**: Plataforma y año se aplican transversalmente
3. **Sin ML**: Enfoque **descriptivo** (mediana, cuartiles, proporciones)
4. **Tablas con DT**: Interactividad nativa sin callbacks Shiny complejos
5. **Paleta PS auténtica**: Colores del logo oficial PlayStation
6. **Insights visibles**: Cada pestaña incluye hallazgos clave

---

## Gráficos Destacados

### Resumen
- Juegos por plataforma (barras)
- Lanzamientos por año (línea + área)
- Mapa de jugadores (top 10 países)
- Insights narrativos en boxes

### Catálogo
- Top géneros (barras con slider dinámico para n)
- Top publishers (barras)
- Precio promedio por género (coloreado)
- Tabla completa con búsqueda

### Jugadores
- Barras: Top países
- Burbujas: Concentración geográfica (size = cantidad)
- Pie: Proporción top 6

### Precios
- Histograma USD (con línea mediana)
- Rangos de precio (categorías)
- Boxplot: Comparativa monedas (USD, EUR, GBP, JPY, RUB)
- Heatmap: Correlación entre monedas

---

## Notas Técnicas

- **Carga de datos**: `read_csv()` con `show_col_types = FALSE` para evitar mensajes
- **Limpieza de géneros**: Usa `str_remove_all()` para quitar corchetes y comillas
- **Filtros reactivos**: `filter(platform == input$f_plat)` se ejecuta al cambiar selector
- **Reutilización**: Dataframes como `sim_base` se construyen una sola vez (mejor performance)
- **Mensaje de ayuda**: Helptext() educa al usuario sobre qué hace cada filtro

---

## Optimizaciones Posibles

- Migrar a **Shiny Modules** si crece (tablas reutilizables)
- Conectar a **base de datos** en lugar de CSV
- Implementar **autenticación** para datos sensibles
- Agregar **exportación a PDF** de reportes

---

## Referencias

- [Shiny RStudio](https://shiny.posit.co/)
- [Plotly R](https://plotly.com/r/)
- [Tidyverse](https://www.tidyverse.org/)
- [DataTable (DT)](https://rstudio.github.io/DT/)
- Curso: Visualización de Datos (módulos R/ggplot2)

---

## Instalación

Asegúrate de tener R instalado. Instala los paquetes necesarios:

```r
install.packages(c("shiny", "shinydashboard", "tidyverse", "plotly", "DT", "scales", "lubridate"))
```

---

## Ejecución

```r
cd shiny_app
shiny::runApp()
```

O abre `app.R` en RStudio y ejecuta la aplicación.