# Introducción {#introduccion}

## Contexto y relevancia

El mercado digital de videojuegos ha transformado radicalmente la distribución y fijación de precios. PlayStation Store ofrece más de 23.000 títulos, desde producciones AAA que superan los $60 hasta juegos indie por menos de $1. A diferencia de los bienes físicos, el costo marginal de distribución digital es prácticamente cero, por lo que los precios no dependen de los costos de producción directos sino de la percepción de valor del consumidor, la estrategia del publisher y las dinámicas competitivas dentro de cada categoría.

Entre 2015 y 2024 el catálogo de PlayStation creció un 1.570% en número de lanzamientos anuales. Esa explosión de oferta no fue homogénea: algunos géneros se inundaron de títulos baratos mientras otros mantuvieron precios elevados. Entender qué factores estructurales explican esa diferencia tiene implicaciones prácticas para desarrolladores (fijar precio de referencia), consumidores (anticipar rangos por preferencia) y publishers (posicionamiento de mercado).

## Pregunta de investigación

> **¿Es posible predecir el precio de un videojuego en PlayStation Store a partir únicamente de su género y su año de lanzamiento?**

Subpreguntas:

1. ¿Cómo evolucionó el precio mediano de los videojuegos entre 2015 y 2024?
2. ¿Qué géneros presentan los precios medianos más altos y más bajos de forma consistente a lo largo del tiempo?
3. ¿El año de lanzamiento tiene un efecto independiente sobre el precio, más allá del género?

## Objetivos

**Objetivo general:** Analizar la relación entre el género y el año de lanzamiento de un videojuego en PlayStation Store con su precio de venta en USD, con el fin de identificar patrones de fijación de precios y construir modelos predictivos comparativos (Lasso, Random Forest, XGBoost).

**Objetivos específicos:**

1. Describir la distribución general de precios del catálogo PlayStation (tendencia central, dispersión, segmentos de mercado).
2. Construir y analizar la serie de tiempo del precio mediano por año de lanzamiento (2015–2024) para identificar tendencias, ciclos e inflexiones del mercado.
3. Comparar los precios medianos entre géneros e identificar los extremos del catálogo.
4. Construir y comparar modelos predictivos usando **únicamente género y año de lanzamiento** como variables predictoras.
5. Evaluar la capacidad predictiva con métricas estándar (R², RMSE, MAE) e interpretar el aporte relativo de cada variable.

## Por qué solo dos variables predictoras

Este proyecto limita deliberadamente las variables a **género** y **año de lanzamiento**. Las razones son:

- **Parsimonia:** un modelo útil debe explicar el precio con el mínimo de variables necesarias.
- **Accionabilidad:** ambas variables son conocidas *antes* de fijar el precio, lo que hace el modelo directamente útil para un desarrollador.
- **Evitar multicolinealidad:** la variable plataforma (PS4/PS5) tiene correlación alta con el año (PS5 se lanzó en 2020); incluirla junto con `year` inflaría artificialmente los coeficientes e impediría interpretar correctamente el efecto temporal.
- **Hipótesis teórica:** la literatura económica sobre mercados digitales señala al género (señal de calidad y duración esperada) y al ciclo de vida del mercado (año) como los predictores más naturales del precio.

## Estructura del documento

| Capítulo | Contenido |
|---|---|
| 2 — Marco Teórico | Economía digital, señales de calidad, estrategias de precio, factor indie |
| 3 — Metodología | Dataset, ETL, justificación de variables, consideraciones éticas |
| 4 — EDA | Distribución de precios, serie de tiempo 2015–2024, análisis por género |
| 5 — Modelos | Lasso, Random Forest, XGBoost con género + año: métricas y validación |
| 6 — Resultados | Verificación de hipótesis e implicaciones del modelado |
| 7 — Conclusiones | Respuestas a preguntas de investigación y trabajo futuro |

<!--chapter:end:01-introduccion.Rmd-->
