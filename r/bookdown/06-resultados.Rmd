# Resultados y Discusión {#resultados}

Este capítulo integra la **verificación de hipótesis** del EDA y los **resultados del modelado predictivo**.

---

## Verificación de hipótesis

| Hipótesis | Estado | Evidencia |
|---|---|---|
| **H1** — Géneros de nicho tienen precios más altos | **CONFIRMADA** | Simulation Racing (66 títulos, $39.99), Open World (193, $24.99) vs. Action (2.999, $2.99), Puzzle (2.065, $4.99). Correlación negativa volumen-precio significativa. |
| **H2** — Géneros masivos tienen mayor variabilidad | **CONFIRMADA PARCIALMENTE** | Action y Adventure presentan alta dispersión ($0.19–$59.99), pero Role Playing también es variable ($0.99–$69.99) por coexistencia de indie y grandes RPGs. La variabilidad depende del nivel de penetración indie en cada género. |
| **H3** — PS5 tiene precios más altos en el mismo género | **CONFIRMADA** | PS5 supera o iguala a PS4 en el 71% de géneros analizados. Diferencia más marcada en Role Playing, Open World y Action-RPG. |

---

## Resultados del modelado predictivo

### Rendimiento comparativo

Random Forest obtuvo el mejor desempeño en todas las métricas (R²=0.3244, RMSE=$9.85, MAE=$6.66), seguido por XGBoost y Lasso. Su superioridad sobre Lasso confirma que la relación precio-predictores **no es lineal**. La baja desviación estándar en la CV de 5 pliegues confirma buena generalización.

### El género como predictor dominante

En ambos modelos de árboles (RF y XGBoost), las variables de género tienen mayor *Gain* e *%IncMSE* que plataforma o año. Géneros como Simulation Racing, Open World y Role Playing aportan la mayor reducción de error. La variable `year` contribuye de forma consistente capturando tendencias temporales (incluyendo deflación post-pandemia).

---

## Hallazgos principales

**1. Género predice precio mejor que plataforma.**
La diferencia entre géneros llega al 4.000% ($0.99–$39.99), mientras PS4 vs PS5 muestra solo 10–20% dentro del mismo género. Implicación: un desarrollador debe analizar su género antes que su plataforma para definir el precio de referencia.

**2. Saturación indie comprime el piso de precios por género.**
En géneros con alta presencia de publishers de alto volumen (eastasiasoft, Ratalaika, ThiGames), el percentil 25 de precios cae por debajo de $2 (Action: p25 = $1.49, Puzzle: p25 = $1.99). Esto actúa como ancla psicológica y dificulta justificar precios superiores aun con mayor calidad.

**3. Géneros de experiencia larga mantienen precios diferenciados.**
Simulation Racing, Open World, Role Playing y Action-RPG comparten la promesa de experiencias largas. El consumidor acepta pagar más porque el **costo por hora de entretenimiento** es comparable o inferior al de géneros baratos y cortos.

---

## Limitaciones del análisis

1. **Variables limitadas:** faltan duración estimada, Metacritic, ESRB/PEGI, reputación del desarrollador.
2. **Snapshot único (febrero 2025):** no captura descuentos estacionales ni dinámicas temporales.
3. **Múltiples géneros por juego:** usar solo el género principal pierde información en títulos multi-género.
4. **Sesgo hacia segmento indie:** baja precisión en el segmento AAA (>$40) por escasez de ejemplos.
5. **Sin datos de ventas:** el precio alto no implica mayores ingresos si el volumen vendido es bajo.

<!--chapter:end:06-resultados.Rmd-->
