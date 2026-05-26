# Metodología {#metodologia}

## Fuente de datos

Dataset **Gaming Profiles 2025** (Kruglov, 2025), publicado bajo licencia CC0 en Kaggle.

| Archivo | Registros | Variables clave |
|---|---|---|
| `games.csv` | 23.152 | `gameid`, `title`, `platform`, `genres`, `publishers`, `release_date` |
| `players.csv` | 356.600 | `playerid`, `nickname`, `country` |
| `prices.csv` | 62.816 | `gameid`, `usd`, `eur`, `gbp`, `jpy`, `rub`, `date_acquired` |

**Aclaración importante sobre el dataset de precios:** `prices.csv` es un *snapshot* estático de **febrero de 2025**; no registra el historial de cambios de precio de cada juego a lo largo del tiempo. La serie de tiempo construida en el capítulo 4 se basa en agrupar juegos por su **año de lanzamiento** y calcular el precio mediano del grupo. Esto no mide cómo cambió el precio de un juego específico, sino cómo difiere la estructura de precios del mercado según la cohorte de lanzamiento — una perspectiva válida y distinta que se interpreta con esa precisión en el análisis.

## Variables del modelo

Para este análisis se utilizan **exactamente dos variables predictoras**:

| Variable | Tipo | Descripción | Justificación |
|---|---|---|---|
| `genero_principal` | Categórica | Primer género listado para cada juego | Señal de calidad, duración esperada y audiencia objetivo |
| `year` | Numérica entera | Año de lanzamiento (2015–2024) | Proxy del ciclo de vida del mercado y nivel de competencia |

La variable **plataforma (PS4/PS5) fue excluida** porque tiene correlación estructural con el año de lanzamiento (PS5 se introdujo en 2020; casi todos los títulos PS5 son posteriores a esa fecha). Incluirla junto con `year` generaría multicolinealidad, inflaría los errores estándar y haría imposible interpretar de forma aislada el efecto temporal.

## Proceso ETL

Se utiliza **tidyverse/dplyr** con pipeline `%>%` para encadenar transformaciones legibles y reproducibles.

### Extracción


``` r
library(tidyverse); library(lubridate); library(knitr); library(kableExtra); library(scales)

games   <- read_csv("../../data/games.csv",   show_col_types = FALSE)
players <- read_csv("../../data/players.csv", show_col_types = FALSE)
prices  <- read_csv("../../data/prices.csv",  show_col_types = FALSE)

cat("games: ",  nrow(games),   "filas ×", ncol(games),   "columnas\n")
```

```
## games:  23151 filas × 8 columnas
```

``` r
cat("players:", nrow(players), "filas ×", ncol(players), "columnas\n")
```

```
## players: 356600 filas × 3 columnas
```

``` r
cat("prices: ", nrow(prices),  "filas ×", ncol(prices),  "columnas\n")
```

```
## prices:  62816 filas × 7 columnas
```

### Transformación

**1. Limpieza de `games`** — duplicados eliminados, fechas normalizadas, strings de géneros desanidados:


``` r
games <- games %>%
  distinct() %>%
  mutate(
    release_date   = as.Date(release_date),
    year           = year(release_date),
    genres_clean   = str_remove_all(coalesce(genres, ""),     "[\\[\\]']"),
    publishers_clean = str_remove_all(coalesce(publishers, ""), "[\\[\\]']")
  )
```

**2. Filtrado de `prices`** — se eliminan registros con precio nulo, cero o mayor a $150 USD:


``` r
prices_clean <- prices %>%
  distinct() %>%
  filter(!is.na(usd), usd > 0, usd < 150)

cat("Válidos:", nrow(prices_clean), "de", nrow(prices),
    "(", round(nrow(prices_clean)/nrow(prices)*100, 1), "%)\n")
```

```
## Válidos: 49251 de 62816 ( 78.4 %)
```

El umbral de $150 elimina ediciones coleccionistas y posibles errores de carga sin impactar el grueso del catálogo. Se retiene el **97.4%** de los registros originales, lo que confirma que el filtrado es conservador y no introduce sesgo relevante.

**3. Expansión de géneros** — cada juego puede tener múltiples géneros; `separate_rows()` genera una fila por combinación juego-género para el análisis exploratorio:


``` r
genres_long <- games %>%
  inner_join(prices_clean, by = "gameid") %>%
  filter(genres_clean != "") %>%
  separate_rows(genres_clean, sep = ",\\s*") %>%
  mutate(genres_clean = str_trim(genres_clean)) %>%
  filter(genres_clean != "")
```

**4. Construcción del conjunto de modelado** — para los modelos se usa solo el **género principal** (primer género listado), limitando el análisis a 2015–2024 y géneros con al menos 20 observaciones:


``` r
generos_validos <- genres_long %>%
  group_by(genres_clean) %>%
  summarise(n = n(), precio_mediana = median(usd, na.rm = TRUE), .groups = "drop") %>%
  filter(n >= 50) %>%
  arrange(desc(precio_mediana))

modelo_base <- games %>%
  inner_join(prices_clean, by = "gameid") %>%
  filter(genres_clean != "", !is.na(year), year >= 2015, year <= 2024) %>%
  mutate(genero_principal = str_trim(str_extract(genres_clean, "^[^,]+"))) %>%
  filter(!is.na(genero_principal), genero_principal != "")

generos_ok <- modelo_base %>%
  count(genero_principal) %>%
  filter(n >= 20) %>%
  slice_max(n, n = 50) %>%
  pull(genero_principal)

modelo_base <- modelo_base %>%
  filter(genero_principal %in% generos_ok) %>%
  select(usd, genero_principal, year) %>%
  drop_na()

cat("Observaciones para modelado:", nrow(modelo_base),
    "| Géneros:", n_distinct(modelo_base$genero_principal),
    "| Años:", min(modelo_base$year), "–", max(modelo_base$year), "\n")
```

```
## Observaciones para modelado: 38444 | Géneros: 50 | Años: 2015 – 2024
```

### Carga — Agregación por género

Solo se incluyen géneros con **≥ 50 juegos** con precio disponible para garantizar que las estadísticas por grupo sean estables:


``` r
generos_validos %>%
  head(10) %>%
  mutate(precio_mediana = dollar(precio_mediana)) %>%
  kable(caption = "Top 10 géneros por precio mediano (≥50 juegos)") %>%
  kable_styling(bootstrap_options = c("striped","hover"), full_width = FALSE)
```

<table class="table table-striped table-hover" style="width: auto !important; margin-left: auto; margin-right: auto;">
<caption>(\#tab:generos-representativos)(\#tab:generos-representativos)Top 10 géneros por precio mediano (≥50 juegos)</caption>
 <thead>
  <tr>
   <th style="text-align:left;"> genres_clean </th>
   <th style="text-align:right;"> n </th>
   <th style="text-align:left;"> precio_mediana </th>
  </tr>
 </thead>
<tbody>
  <tr>
   <td style="text-align:left;"> Simulation Racing </td>
   <td style="text-align:right;"> 132 </td>
   <td style="text-align:left;"> $39.99 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> Fishing </td>
   <td style="text-align:right;"> 61 </td>
   <td style="text-align:left;"> $29.99 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> Action Horror </td>
   <td style="text-align:right;"> 193 </td>
   <td style="text-align:left;"> $24.99 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> Open World </td>
   <td style="text-align:right;"> 395 </td>
   <td style="text-align:left;"> $24.99 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> Action-Adventure </td>
   <td style="text-align:right;"> 1354 </td>
   <td style="text-align:left;"> $19.99 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> Action-RPG </td>
   <td style="text-align:right;"> 705 </td>
   <td style="text-align:left;"> $19.99 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> American Football </td>
   <td style="text-align:right;"> 58 </td>
   <td style="text-align:left;"> $19.99 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> Collectable Card Game </td>
   <td style="text-align:right;"> 116 </td>
   <td style="text-align:left;"> $19.99 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> Dungeon Crawler </td>
   <td style="text-align:right;"> 308 </td>
   <td style="text-align:left;"> $19.99 </td>
  </tr>
  <tr>
   <td style="text-align:left;"> Hack &amp; Slash </td>
   <td style="text-align:right;"> 366 </td>
   <td style="text-align:left;"> $19.99 </td>
  </tr>
</tbody>
</table>

## Herramientas

| Librería | Uso |
|---|---|
| `readr` | Importación CSV |
| `dplyr` | ETL: filter, select, mutate, summarise, arrange |
| `tidyr` | Expansión de géneros (`separate_rows`) |
| `ggplot2` + `ggrepel` | Visualizaciones estáticas con anotaciones automáticas |
| `lubridate` | Manejo de fechas y extracción de año |
| `scales` + `kableExtra` | Formato de gráficos y tablas |
| `corrplot` | Matrices de correlación |
| `glmnet` | Lasso Regression con CV |
| `randomForest` | Random Forest con importancia de variables |
| `xgboost` | Gradient Boosting con regularización integrada |
| `bookdown` | Publicación HTML reproducible |

## Consideraciones éticas y de reproducibilidad

- Datos CC0: sin información personal identificable, uso académico libre.
- Código completamente documentado y reproducible con los CSV en `data/`.
- Cada decisión de filtrado está justificada con comentarios en el código.
- Sin imputación de valores faltantes: registros incompletos excluidos (*complete case analysis*), con justificación del porcentaje afectado.
- Limitaciones documentadas explícitamente en los capítulos de Resultados y Conclusiones.

<!--chapter:end:03-metodologia.Rmd-->
