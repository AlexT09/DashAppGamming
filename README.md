# PS Gaming Analytics 2025

<div align="center">

## Advanced Data Science & Machine Learning Project for PlayStation Store Analytics

End-to-end analytics ecosystem developed with **Python, R, Machine Learning, Dash, Shiny and Bookdown** using real-world gaming market data.

<br>

<img src="https://img.shields.io/badge/Python-Data%20Science-blue?style=for-the-badge&logo=python">
<img src="https://img.shields.io/badge/R-Analytics-276DC3?style=for-the-badge&logo=r">
<img src="https://img.shields.io/badge/Machine%20Learning-XGBoost-orange?style=for-the-badge">
<img src="https://img.shields.io/badge/Dash-Interactive%20Dashboard-119DFF?style=for-the-badge">
<img src="https://img.shields.io/badge/Shiny-R%20Dashboard-75AADB?style=for-the-badge">
<img src="https://img.shields.io/badge/Bookdown-Technical%20Report-darkgreen?style=for-the-badge">

<br><br>

### 23,151 Games · 356,600 Players · 62,816 Price Records

</div>

---

# Overview

This project analyzes the PlayStation Store ecosystem using real gaming market data obtained from Kaggle.

The objective is to study how variables such as:

- genre,
- platform,
- release year,
- market saturation,
- and game category

affect video game pricing behavior.

The project integrates:

- Exploratory Data Analysis (EDA)
- Statistical Analysis
- Machine Learning
- Interactive Dashboards
- Predictive Modeling
- Data Visualization
- Technical Reporting


# Tech Stack

## Data Science & Machine Learning

- Python
- R
- Pandas
- NumPy
- Scikit-learn
- XGBoost
- Random Forest
- glmnet
- caret

## Visualization & Analytics

- Plotly
- ggplot2
- Dash
- Shiny
- Bookdown

## Infrastructure

- Docker
- Git
- GitHub
- Jupyter Notebook

---

# Project Architecture

```text
ps-gaming-analytics-2025/

 data/ # Fuente principal de datos
 games.csv # 23,151 juegos PlayStation
 players.csv # 356,600 perfiles de jugadores
 prices.csv # 62,816 registros de precios

 python/
 
 notebooks/
 notebook_ps_gaming.ipynb
 # Entrenamiento y evaluación de modelos ML
 
 dash_app/
 app.py # Aplicación principal Dash
 data.py # Pipeline de carga y transformación
 requirements.txt
 Dockerfile
 docker-compose.yml
 README.md
 
 tabs/
 tab_introduccion.py
 tab_objetivos.py
 tab_metodologia.py
 tab_modelos.py
 tab_prediccion.py

 r/
 
 bookdown/
 index.Rmd
 01-introduccion.Rmd
 02-marco.Rmd
 03-metodologia.Rmd
 04-eda.Rmd
 05-modelos.Rmd
 06-resultados.Rmd
 07-conclusiones.Rmd
 style.css
 _bookdown.yml
 _output.yml
 
 shiny_app/
 app.R
 models.R
 README.md

 .gitignore
 INSTRUCCIONES.md
 README.md
```

---

# Dataset

Dataset used:

 https://www.kaggle.com/datasets/artyomkruglov/gaming-profiles-2025-steam-playstation-xbox

## Dataset Characteristics

| Dataset | Records | Description |
|---|---:|---|
| `games.csv` | 23,151 | Video game metadata |
| `players.csv` | 356,600 | Player profiles |
| `prices.csv` | 62,816 | Multi-currency pricing records |

## Features

- Real-world gaming market data
- Multi-platform ecosystem
- Multi-currency pricing
- Genre metadata
- Release dates
- Publisher information
- Market behavior patterns

---

# Quick Start

---

# 1⃣ Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/ps-gaming-analytics-2025.git

cd ps-gaming-analytics-2025
```

---

# 2⃣ Python Dash App

Interactive analytics dashboard built with Dash + Plotly.

## Installation

```bash
cd python/dash_app

pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Open:

```text
http://127.0.0.1:8050
```

---

# 3⃣ R Shiny Dashboard

## Install Dependencies

```r
install.packages(c(
 "shiny",
 "shinydashboard",
 "tidyverse",
 "plotly",
 "DT",
 "caret",
 "randomForest",
 "xgboost"
))
```

## Run App

```r
setwd("r/shiny_app")

shiny::runApp()
```

Open:

```text
http://127.0.0.1:3838
```

---

# 4⃣ Bookdown Technical Report

## Install Dependencies

```r
install.packages(c(
 "bookdown",
 "tidyverse",
 "ggplot2",
 "corrplot",
 "glmnet",
 "randomForest",
 "xgboost"
))
```

## Compile Report

```r
setwd("r/bookdown")

bookdown::render_book(
 "index.Rmd",
 "bookdown::gitbook"
)
```

Output:

```text
r/bookdown/_book/index.html
```

---

# 5⃣ Jupyter Notebook

```bash
cd python/notebooks

jupyter notebook notebook_ps_gaming.ipynb
```

---

# Machine Learning Models

The project evaluates multiple supervised learning models for video game price prediction.

| Model | R² | RMSE | MAE |
|---|---:|---:|---:|
| Lasso Regression | 0.3547 | 15.23 | 8.92 |
| Random Forest | 0.4892 | 11.34 | 6.21 |
| **XGBoost** | **0.5234** | **10.78** | **5.89** |

## Prediction Variables

- Genre
- Platform
- Release Year

## Best Performing Model

**XGBoost** achieved the best predictive performance with the lowest error metrics and highest explanatory power.

---

# Exploratory Data Analysis

Main findings include:

 Strong relationship between genre and pricing 
 Premium genres maintain higher median prices 
 Market saturation negatively correlates with price 
 PS5 titles exhibit higher pricing behavior 
 Multi-currency prices show near-perfect correlation 

---

# Docker Support

Run the Dash application using Docker.

## Build Container

```bash
cd python/dash_app

docker build -t ps-gaming-dash .
```

## Run Container

```bash
docker run -p 8050:8050 ps-gaming-dash
```

---

# Technical Report

The Bookdown report includes:

- methodology,
- exploratory analysis,
- statistical interpretation,
- machine learning evaluation,
- model comparison,
- conclusions,
- and future work.

---

# Why This Project Matters

This repository demonstrates practical skills in:

- data engineering,
- machine learning,
- analytical storytelling,
- dashboard development,
- statistical modeling,
- and reproducible research.

The project simulates a professional gaming analytics workflow commonly found in:

- gaming companies,
- product analytics teams,
- business intelligence environments,
- and market research organizations.

---

# Recommended GitHub Images

Create an `images/` folder in the project root.

Suggested screenshots:

| Image | Filename |
|---|---|
| Dash Dashboard | `dash-dashboard.png` |
| Bookdown Report | `bookdown-preview.png` |
| EDA Charts | `eda-analysis.png` |
| ML Results | `model-results.png` |
| Shiny Dashboard | `shiny-dashboard.png` |

---

# ‍ Author

**Alex Teran**

Academic and analytical project developed using real-world gaming data.

---

# License

This project uses data distributed under:

**CC0 Public Domain License**

Dataset author:

**Artyom Kruglov — Kaggle**

---

<div align="center">

## If you found this project interesting, consider starring the repository.

</div>
