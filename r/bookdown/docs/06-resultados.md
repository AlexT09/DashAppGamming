# Resultados y Discusión {#resultados}

Este capítulo integra la **verificación de hipótesis** del EDA con los **resultados del modelado predictivo**, respondiendo directamente a las subpreguntas de investigación planteadas en el capítulo 1.

---

## Verificación de hipótesis

| Hipótesis | Estado | Evidencia |
|---|---|---|
| **H1** — Géneros de nicho tienen precios medianos más altos | **CONFIRMADA** | Simulation Racing (66 títulos, $39.99), Open World (193, $24.99) vs. Action (2.999, $2.99). Correlación negativa volumen-precio significativa. |
| **H2** — Géneros masivos tienen mayor variabilidad de precios | **CONFIRMADA PARCIALMENTE** | Action y Adventure presentan alta dispersión ($0.19–$59.99), pero Role Playing también es variable por coexistencia de indie y grandes RPGs. La variabilidad depende del grado de penetración indie en cada género, no solo del volumen. |
| **H3** — El precio mediano cayó entre 2015 y 2024 | **CONFIRMADA** | El precio mediano descendió de ~$12 (2015) a ~$4 (2022), recuperándose levemente en 2023–24. El volumen de lanzamientos pasó de 543 títulos en 2015 a 5.091 en 2024 — el crecimiento de oferta es la causa principal de la deflación. |

---

## Respuesta a las subpreguntas

**Subpregunta 1 — ¿Cómo evolucionó el precio entre 2015 y 2024?**

La deflación fue sostenida y acelerada: el precio mediano cayó un ~67% en siete años. El inflexión ocurre alrededor de 2019–2020, que coincide con la explosión de publishers de alto volumen y la entrada de PS5 al mercado. La leve recuperación en 2023–24 puede interpretarse como una corrección del mercado: los jugadores comienzan a ignorar catálogos de títulos ultra-baratos y los precios de los juegos que sí logran atención empiezan a normalizarse.

**Subpregunta 2 — ¿Qué géneros tienen precios consistentemente altos o bajos?**

Los géneros caros (Simulation Racing, Open World, Role Playing, Action-RPG) comparten la promesa de experiencias largas. Los géneros baratos (Bowling, Pinball, Educational, Puzzle) son de sesión corta y tienen alta penetración indie. Este patrón es estable a lo largo del tiempo y es capturado de forma consistente por los tres modelos.

**Subpregunta 3 — ¿Tiene `year` un efecto independiente del género?**

Sí. En Random Forest y XGBoost, la variable `year` aparece con importancia significativa incluso después de controlar por género. Además, la serie de tiempo por género (capítulo 4) muestra que la deflación afecta a todos los géneros, aunque con distinta velocidad. Esto confirma que año y género tienen efectos parcialmente independientes, y que su interacción (géneros se deflacionan a ritmos distintos) es capturada por los modelos no lineales.

---

## Resultados del modelado predictivo

### Rendimiento comparativo

Random Forest obtuvo el mejor desempeño en todas las métricas (R²=0.3244, RMSE=$9.85, MAE=$6.66), seguido por XGBoost y Lasso. Su superioridad sobre Lasso confirma que la relación precio-predictores no es lineal. La baja desviación estándar en la CV de 5 pliegues confirma buena generalización.

### El género como predictor dominante

En RF y XGBoost, las variables de género tienen mayor Gain e %IncMSE que el año. Géneros como Simulation Racing, Open World y Role Playing aportan la mayor reducción de error. La variable `year` contribuye de forma consistente capturando la tendencia deflacionaria documentada en la serie de tiempo.

### Sobre el R² moderado

Un R² de ~0.32 no es un fracaso del modelo — es un resultado **honesto y esperado** con solo dos variables. La varianza no explicada (68%) proviene principalmente de:

1. **Heterogeneidad indie vs. AAA:** dentro del género *Action* hay juegos indie a $0.99 y producciones AAA a $59.99. Sin saber cuál es cuál, ningún modelo puede distinguirlos.
2. **Variables ausentes:** Metacritic, duración, ESRB, reputación del desarrollador son predictores relevantes no disponibles en este dataset.
3. **Snapshot estático:** descuentos temporales y ajustes de precio post-lanzamiento no están capturados.

---

## Hallazgos principales

**1. El género predice el precio mejor que cualquier otra variable disponible.**
La diferencia entre géneros llega al 4.000% ($0.99–$39.99). Un desarrollador debe analizar su género antes que cualquier otra decisión de posicionamiento.

**2. La saturación indie comprime el piso de precios por género.**
En géneros con alta presencia de publishers de alto volumen, el percentil 25 cae por debajo de $2, actuando como ancla psicológica que dificulta justificar precios superiores aun con mayor calidad.

**3. La deflación temporal es real y cuantificable.**
El año de lanzamiento tiene poder predictivo independiente: lanzar en 2024 predice un precio más bajo que lanzar el mismo género en 2018, ceteris paribus. Cada año adicional de saturación del mercado reduce el precio esperado en promedio.

---

## Limitaciones del análisis

1. **Variables limitadas:** faltan duración estimada, Metacritic, ESRB/PEGI, reputación del desarrollador.
2. **Snapshot único (febrero 2025):** no captura descuentos estacionales ni dinámicas temporales de precios individuales.
3. **Género único como proxy:** usar solo el género principal pierde información en títulos multi-género.
4. **Sesgo hacia segmento indie:** baja precisión en el segmento AAA (>$40) por escasez de ejemplos.
5. **Sin datos de ventas:** el precio alto no implica mayores ingresos si el volumen vendido es bajo.

<!--chapter:end:06-resultados.Rmd-->
