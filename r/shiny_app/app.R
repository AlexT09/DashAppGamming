# 
# PlayStation Gaming Analytics 2025 — Modern Shiny 
# Alex Terán · Ciencia de Datos · Grupo 13 
# 

library(shiny)
library(shinydashboard)
library(tidyverse)
library(plotly)
library(DT)
library(scales)
library(lubridate)

`%||%` <- function(a, b) if (!is.null(a) && length(a) > 0 && !is.na(a[1])) a else b

# Paleta Modern 2026 
PS_DARKER <- "#0A0E1A"
PS_DARK <- "#0D1226"
PS_CARD <- "#111827"
PS_BORDER <- "#1E2D4A"
PS_BLUE <- "#0070D1"
PS_ACCENT <- "#00AAFF"
PS_GREEN <- "#22C55E"
PS_AMBER <- "#F59E0B"
PS_RED <- "#EF4444"
PS_PURPLE <- "#A78BFA"
PS_TEXT <- "#F0F4FF"
PS_MUTED <- "#8B9BB4"

# Carga de datos 
base_dir <- if (file.exists("data/games.csv")) "data" else if (file.exists("../data/games.csv")) "../data" else "../../data"

games <- read_csv(file.path(base_dir, "games.csv"), show_col_types = FALSE) %>%
 distinct() %>%
 mutate(
 release_date = as.Date(release_date),
 year = year(release_date),
 genres_clean = str_remove_all(coalesce(genres, ""), "[\\[\\]\\']"),
 publishers_clean = str_remove_all(coalesce(publishers, ""), "[\\[\\]\\']"),
 developers_clean = str_remove_all(coalesce(developers, ""), "[\\[\\]\\']")
 )

players <- read_csv(file.path(base_dir, "players.csv"), show_col_types = FALSE) %>%
 distinct() %>% filter(!is.na(country), country != "")

prices <- read_csv(file.path(base_dir, "prices.csv"), show_col_types = FALSE) %>%
 distinct() %>%
 filter(!is.na(usd), usd > 0, usd < 150) %>%
 mutate(date_acquired = as.Date(date_acquired))

games_prices <- games %>% inner_join(prices, by = "gameid")

genres_long <- games %>%
 filter(genres_clean != "") %>%
 separate_rows(genres_clean, sep = ",\\s*") %>%
 filter(genres_clean != "") %>%
 mutate(genres_clean = str_trim(genres_clean))

precio_genero <- genres_long %>%
 inner_join(prices %>% select(gameid, usd), by = "gameid") %>%
 group_by(genres_clean) %>%
 summarise(precio_prom = mean(usd, na.rm = TRUE),
 precio_med = median(usd, na.rm = TRUE),
 n = n(), .groups = "drop") %>%
 filter(n >= 15)

sim_base <- games %>%
 inner_join(prices %>% select(gameid, usd), by = "gameid") %>%
 filter(genres_clean != "") %>%
 separate_rows(genres_clean, sep = ",\\s*") %>%
 mutate(genres_clean = str_trim(genres_clean)) %>%
 filter(genres_clean != "")

GENRES_SIM <- sort(unique(sim_base$genres_clean))
N_GAMES <- nrow(games)
N_PLAYERS <- nrow(players)
N_COUNTRIES <- n_distinct(players$country)
PLATS <- c("Todas", sort(unique(na.omit(games$platform))))
YEAR_RANGE <- range(games$year, na.rm = TRUE)

na_pct_table <- function(path, lab) {
 df <- read_csv(path, show_col_types = FALSE)
 purrr::map_dfr(names(df), function(nm) {
 tibble(dataset = lab, column = nm, missing_pct = 100 * mean(is.na(df[[nm]])))
 }) %>% filter(missing_pct > 0) %>%
 group_by(dataset) %>% arrange(desc(missing_pct)) %>%
 slice_head(n = 12) %>% ungroup()
}

miss_plot_df <- bind_rows(
 na_pct_table(file.path(base_dir, "games.csv"), "games"),
 na_pct_table(file.path(base_dir, "players.csv"), "players"),
 na_pct_table(file.path(base_dir, "prices.csv"), "prices")
) %>% mutate(label = paste(dataset, column, sep = ": "))

source("models.R", local = TRUE)

TRAINED_MODELS <- tryCatch({
 train_all_models(games, prices)
}, error = function(e) { message("Error modelos: ", e$message); NULL })

PRED_GENRES <- if (!is.null(TRAINED_MODELS)) sort(unique(TRAINED_MODELS$prep_data$data$genre_main)) else character(0)

# 
# CSS PREMIUM — Modern 2026 · Dark theme · Glassmorphism
# 
PREMIUM_CSS <- "
/* Reset & base */
* { box-sizing: border-box; }
body, html { background: #0A0E1A !important; font-family: 'Inter', 'Segoe UI', system-ui, sans-serif; font-size: 15px; }

/* Sidebar */
.skin-blue .main-sidebar {
 background: linear-gradient(180deg, #0D1226 0%, #0A0E1A 100%) !important;
 border-right: 1px solid rgba(0,112,209,0.2);
}
.skin-blue .sidebar-menu > li > a {
 color: #A8BCCF !important;
 border-left: 3px solid transparent;
 transition: all 0.25s ease;
 font-size: 0.93rem;
 padding: 11px 15px;
 border-radius: 6px;
 margin: 2px 8px;
}
.skin-blue .sidebar-menu > li > a:hover,
.skin-blue .sidebar-menu > li.active > a {
 background: rgba(0,112,209,0.15) !important;
 border-left-color: #0070D1 !important;
 color: #00AAFF !important;
 font-weight: 600;
}
.sidebar .sidebar-menu .treeview-menu > li > a { color: #8FA8C8 !important; font-size: 0.88rem; }

/* Header */
.skin-blue .main-header .logo,
.skin-blue .main-header .navbar {
 background: linear-gradient(90deg, #0D1226 0%, #001A3D 100%) !important;
 border-bottom: 1px solid rgba(0,112,209,0.15);
}
.skin-blue .main-header .logo {
 font-weight: 700 !important;
 letter-spacing: 0.5px;
 color: #F0F4FF !important;
 font-size: 1.05rem !important;
}

/* Main content */
.content-wrapper, .right-side {
 background: #0A0E1A !important;
}
.content { padding: 24px !important; }

/* Boxes → modern cards */
.box {
 background: #111827 !important;
 border: 1px solid #1E2D4A !important;
 border-radius: 12px !important;
 box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
 margin-bottom: 18px !important;
 overflow: hidden;
}
.box-header {
 background: #0D1226 !important;
 border-bottom: 1px solid #1E2D4A !important;
 padding: 14px 18px !important;
}
.box-title {
 color: #F0F4FF !important;
 font-size: 1.0rem !important;
 font-weight: 700 !important;
 letter-spacing: 0.3px;
}
.box-body { padding: 18px 20px !important; color: #B8C8DC !important; font-size: 0.95rem; }
.box.box-primary { border-top: 2px solid #0070D1 !important; }
.box.box-success { border-top: 2px solid #22C55E !important; }
.box.box-warning { border-top: 2px solid #F59E0B !important; }
.box.box-info { border-top: 2px solid #00AAFF !important; }
.box.box-danger { border-top: 2px solid #EF4444 !important; }

/* KPI cards */
.kpi-card {
 background: #111827;
 border: 1px solid #1E2D4A;
 border-radius: 12px;
 padding: 20px 18px;
 margin-bottom: 14px;
 position: relative;
 overflow: hidden;
 transition: all 0.2s ease;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.4); }
.kpi-card::before {
 content: '';
 position: absolute;
 top: 0; left: 0; right: 0;
 height: 2px;
}
.kpi-blue::before { background: linear-gradient(90deg, #00AAFF, #0070D1); }
.kpi-green::before { background: linear-gradient(90deg, #22C55E, #0070D1); }
.kpi-gold::before { background: linear-gradient(90deg, #F59E0B, #EF4444); }
.kpi-purple::before{ background: linear-gradient(90deg, #A78BFA, #00AAFF); }

.kpi-icon {
 font-size: 1.8rem;
 margin-bottom: 8px;
 display: block;
 opacity: 0.8;
}
.kpi-value {
 font-size: 2.1rem;
 font-weight: 800;
 color: #F0F4FF;
 line-height: 1.1;
 display: block;
 margin-bottom: 4px;
}
.kpi-label {
 font-size: 0.78rem;
 color: #A8BCCF;
 text-transform: uppercase;
 letter-spacing: 0.7px;
 font-weight: 600;
}

/* Page header */
.page-hero {
 background: linear-gradient(135deg, rgba(0,112,209,0.2) 0%, rgba(167,139,250,0.15) 100%);
 border: 1px solid rgba(0,112,209,0.25);
 border-radius: 12px;
 padding: 24px 28px;
 margin-bottom: 20px;
 position: relative;
 overflow: hidden;
}
.page-hero h3 {
 color: #F0F4FF !important;
 font-size: 1.45rem !important;
 font-weight: 800 !important;
 margin: 0 0 6px 0;
}
.page-hero p { color: #A8BCCF; margin: 0; font-size: 0.95rem; }

/* Insight cards */
.insight-card {
 background: rgba(0,112,209,0.08);
 border: 1px solid rgba(0,112,209,0.2);
 border-radius: 8px;
 padding: 12px 14px;
 margin-bottom: 10px;
 font-size: 0.92rem;
 color: #A8B8D0;
 line-height: 1.45;
}
.insight-card strong { color: #F0F4FF; }

/* Tables */
.dataTables_wrapper { color: #A8BCCF !important; }
table.dataTable { background: transparent !important; color: #A8B8D0 !important; }
table.dataTable thead th {
 background: rgba(0,112,209,0.15) !important;
 color: #F0F4FF !important;
 border-bottom: 1px solid #1E2D4A !important;
 font-size: 0.86rem !important;
 text-transform: uppercase;
 letter-spacing: 0.4px;
 font-weight: 700;
}
table.dataTable tbody tr:hover td { background: rgba(0,112,209,0.08) !important; }
table.dataTable tbody td { border-top: 1px solid #1E2D4A !important; font-size: 0.90rem; color: #C8D8F0 !important; }

/* Inputs */
.form-control, .selectize-input {
 background: #111827 !important;
 border: 1px solid #1E2D4A !important;
 color: #F0F4FF !important;
 border-radius: 8px !important;
}
.form-control:focus, .selectize-input.focus {
 border-color: #0070D1 !important;
 box-shadow: 0 0 0 2px rgba(0,112,209,0.15) !important;
}
.selectize-dropdown {
 background: #0D1226 !important;
 border: 1px solid #1E2D4A !important;
 border-radius: 8px !important;
}
.selectize-dropdown .option:hover,
.selectize-dropdown .option.selected { background: rgba(0,112,209,0.15) !important; }
.control-label { color: #A8BCCF !important; font-size: 0.85rem !important; font-weight: 600 !important; text-transform: uppercase; }

/* Buttons */
.btn {
 border-radius: 8px !important;
 font-weight: 600 !important;
 font-size: 0.95rem !important;
 transition: all 0.2s ease;
}
.btn-primary {
 background: linear-gradient(135deg, #0070D1, #00AAFF) !important;
 border: none !important;
 color: #FFF !important;
}
.btn-primary:hover { opacity: 0.9; transform: translateY(-1px); }
.btn-secondary {
 background: #1E2D4A !important;
 border: 1px solid #1E2D4A !important;
 color: #F0F4FF !important;
}

/* Prediction box */
.pred-result-box {
 background: linear-gradient(135deg, rgba(0,112,209,0.15), rgba(0,170,255,0.1));
 border: 1px solid rgba(0,170,255,0.25);
 border-radius: 12px;
 padding: 28px;
 text-align: center;
}
.pred-price {
 font-size: 3rem;
 font-weight: 900;
 background: linear-gradient(135deg, #00AAFF, #F0F4FF);
 -webkit-background-clip: text;
 -webkit-text-fill-color: transparent;
 line-height: 1;
 margin: 10px 0;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0A0E1A; }
::-webkit-scrollbar-thumb { background: #1E2D4A; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #0070D1; }

/* DataTables (complemento tema oscuro) */
table.dataTable tbody td {
 color: #C8D8F0 !important;
 border-radius: 6px !important;
 padding: 4px 8px;
}
.dataTables_info, .dataTables_paginate { color: #8FA8C8 !important; font-size: 0.88rem; }
.paginate_button { color: #8FA8C8 !important; border-radius: 6px !important; }
.paginate_button.current { background: rgba(0,212,255,0.15) !important; color: #00D4FF !important; border: 1px solid rgba(0,212,255,0.3) !important; }

/* Inputs */
.form-control, .selectize-input {
 background: rgba(255,255,255,0.06) !important;
 border: 1px solid rgba(255,255,255,0.12) !important;
 color: #C8D8F0 !important;
 border-radius: 8px !important;
}
.selectize-input.focus, .form-control:focus {
 border-color: rgba(0,212,255,0.5) !important;
 box-shadow: 0 0 0 2px rgba(0,212,255,0.1) !important;
}
.selectize-dropdown {
 background: #141828 !important;
 border: 1px solid rgba(255,255,255,0.12) !important;
 border-radius: 8px !important;
 color: #C8D8F0 !important;
}
.selectize-dropdown .option:hover,
.selectize-dropdown .option.selected { background: rgba(0,212,255,0.1) !important; }
.control-label { color: #8FA3C7 !important; font-size: 0.88rem !important; font-weight: 500 !important; text-transform: uppercase; letter-spacing: 0.5px; }
.irs--shiny .irs-bar { background: linear-gradient(90deg, #003087, #00D4FF) !important; }
.irs--shiny .irs-handle > i:first-child {
 background: #00D4FF !important;
 border-color: #00D4FF !important;
}
.irs--shiny .irs-from, .irs--shiny .irs-to, .irs--shiny .irs-single {
 background: #003087 !important;
 font-size: 0.82rem;
}

/* Buttons */
.btn-predict {
 background: linear-gradient(135deg, #003087, #00D4FF) !important;
 border: none !important;
 color: #FFF !important;
 border-radius: 10px !important;
 font-weight: 700 !important;
 padding: 12px 24px !important;
 font-size: 1.0rem !important;
 width: 100%;
 letter-spacing: 0.4px;
 transition: opacity 0.2s, transform 0.15s;
 box-shadow: 0 4px 16px rgba(0,212,255,0.3);
}
.btn-predict:hover { opacity: 0.85; transform: scale(1.02); }

/* Prediction result */
.pred-result-box {
 background: linear-gradient(135deg, rgba(0,48,135,0.4), rgba(0,212,255,0.15));
 border: 1px solid rgba(0,212,255,0.3);
 border-radius: 16px;
 padding: 32px;
 text-align: center;
}
.pred-price {
 font-size: 3.5rem;
 font-weight: 900;
 background: linear-gradient(135deg, #00D4FF, #FFFFFF);
 -webkit-background-clip: text;
 -webkit-text-fill-color: transparent;
 background-clip: text;
 line-height: 1;
 margin: 12px 0;
}
.pred-label { color: #8FA8C8; font-size: 0.92rem; text-transform: uppercase; letter-spacing: 1px; }

/* Benchmark block */
.bench-row {
 display: flex;
 align-items: center;
 justify-content: space-between;
 background: rgba(255,255,255,0.04);
 border-radius: 10px;
 padding: 14px 18px;
 margin-bottom: 10px;
 border: 1px solid rgba(255,255,255,0.07);
}
.bench-label { color: #8FA8C8; font-size: 0.88rem; text-transform: uppercase; letter-spacing: 0.5px; }
.bench-value { color: #FFFFFF; font-size: 1.3rem; font-weight: 700; }
.bench-value.highlight { color: #00D4FF; font-size: 1.6rem; text-shadow: 0 0 16px rgba(0,212,255,0.5); }

/* Methodology steps */
.step-card {
 background: rgba(255,255,255,0.04);
 border: 1px solid rgba(255,255,255,0.08);
 border-radius: 12px;
 padding: 16px 18px;
 margin-bottom: 12px;
 display: flex;
 gap: 14px;
 align-items: flex-start;
}
.step-num {
 width: 32px; height: 32px;
 background: linear-gradient(135deg, #003087, #00D4FF);
 border-radius: 8px;
 display: flex; align-items: center; justify-content: center;
 color: #FFF; font-weight: 800; font-size: 0.85rem;
 flex-shrink: 0;
}
.step-content h5 { color: #C8D8F0; margin: 0 0 4px 0; font-size: 0.96rem; font-weight: 600; }
.step-content p { color: #8FA8C8; margin: 0; font-size: 0.88rem; line-height: 1.5; }

/* Alert override */
.alert-warning {
 background: rgba(244,162,97,0.1) !important;
 border: 1px solid rgba(244,162,97,0.3) !important;
 color: #C8A870 !important;
 border-radius: 8px !important;
 font-size: 0.92rem;
}

/* Scrollbar (panel secundario) */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0D1226; }
::-webkit-scrollbar-thumb { background: rgba(0,212,255,0.3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,212,255,0.5); }

/* Sidebar bottom tag */
.sidebar-brand { padding: 10px 15px; border-top: 1px solid rgba(255,255,255,0.06); margin-top: 10px; }
.sidebar-brand span { color: #6878A0; font-size: 0.82rem; display: block; line-height: 1.6; }

/* HR */
hr { border-color: rgba(255,255,255,0.07) !important; }

/* Model best card */
.model-best {
 background: linear-gradient(135deg, rgba(6,214,160,0.1), rgba(0,48,135,0.2));
 border: 1px solid rgba(6,214,160,0.3);
 border-radius: 14px;
 padding: 24px;
 text-align: center;
}
.model-name { color: #06D6A0; font-size: 1.55rem; font-weight: 800; margin-bottom: 16px; }
.metric-pill {
 display: inline-block;
 padding: 8px 18px;
 border-radius: 20px;
 font-weight: 700;
 font-size: 0.98rem;
 margin: 4px;
}
.mp-r2 { background: rgba(0,212,255,0.15); color: #00D4FF; border: 1px solid rgba(0,212,255,0.3); }
.mp-rmse { background: rgba(230,57,70,0.15); color: #E63946; border: 1px solid rgba(230,57,70,0.3); }
.mp-mae { background: rgba(244,162,97,0.15); color: #F4A261; border: 1px solid rgba(244,162,97,0.3); }

/* Obj card */
.obj-card {
 background: rgba(255,255,255,0.04);
 border: 1px solid rgba(255,255,255,0.08);
 border-radius: 12px;
 padding: 18px;
 height: 100%;
 transition: border-color 0.2s, background 0.2s;
}
.obj-card:hover { border-color: rgba(0,212,255,0.3); background: rgba(0,212,255,0.04); }
.obj-card .obj-num { color: #00D4FF; font-size: 1.5rem; font-weight: 900; line-height: 1; margin-bottom: 6px; }
.obj-card h5 { color: #C8D8F0; font-size: 0.92rem; font-weight: 600; margin: 0 0 6px 0; text-transform: uppercase; letter-spacing: 0.4px; }
.obj-card p { color: #8FA8C8; font-size: 0.88rem; line-height: 1.5; margin: 0; }
"

# Helper: plotly base layout 
ps_layout <- function(p, ...) {
 p %>% layout(
 paper_bgcolor = "rgba(0,0,0,0)",
 plot_bgcolor = "rgba(10,14,26,0)",
 font = list(color = "#8FA3C7", family = "Segoe UI, system-ui, sans-serif", size = 11),
 xaxis = list(gridcolor = "rgba(255,255,255,0.05)", zerolinecolor = "rgba(255,255,255,0.08)"),
 yaxis = list(gridcolor = "rgba(255,255,255,0.05)", zerolinecolor = "rgba(255,255,255,0.08)"),
 ...
 ) %>% config(displayModeBar = FALSE, responsive = TRUE)
}

# Helper: custom KPI box 
kpi_box <- function(value, label, icon_emoji, color_class, glow_class) {
 tags$div(class = paste("kpi-card", color_class),
 tags$span(icon_emoji, class = "kpi-icon"),
 tags$span(value, class = paste("kpi-value", glow_class)),
 tags$span(label, class = "kpi-label")
 )
}

# 
# UI
# 
ui <- dashboardPage(
 skin = "blue",
 
 dashboardHeader(
 title = tags$span(
 tags$img(
 src = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Playstation_logo_colour.svg/60px-Playstation_logo_colour.svg.png",
 height = "38px",
 style = "margin-right:10px; vertical-align:middle; filter: brightness(1.4) drop-shadow(0 0 6px rgba(0,212,255,0.5));"
 ),
 tags$span("Gaming Analytics", style = "color:#FFFFFF; font-weight:800; letter-spacing:0.3px;"),
 tags$span(" 2025", style = "color:#00D4FF; font-weight:800;")
 ),
 titleWidth = 300
 ),
 
 dashboardSidebar(
 width = 240,
 tags$style(HTML(PREMIUM_CSS)),
 sidebarMenu(
 id = "sidebar",
 menuItem("Introducción", tabName = "introduccion", icon = icon("book-open")),
 menuItem("Objetivos", tabName = "objetivos", icon = icon("bullseye")),
 menuItem("Metodología", tabName = "metodologia", icon = icon("flask")),
 tags$hr(),
 menuItem("Resumen", tabName = "resumen", icon = icon("home")),
 menuItem("Catálogo", tabName = "catalogo", icon = icon("gamepad")),
 menuItem("Jugadores", tabName = "jugadores", icon = icon("users")),
 menuItem("Precios", tabName = "precios", icon = icon("dollar-sign")),
 menuItem("Simulador", tabName = "simulador", icon = icon("sliders-h")),
 menuItem("Calidad datos", tabName = "calidad", icon = icon("clipboard-check")),
 menuItem("Explorador", tabName = "explorador", icon = icon("table")),
 tags$hr(),
 menuItem("Modelos ML", tabName = "modelos", icon = icon("robot")),
 menuItem("Predictor", tabName = "prediccion", icon = icon("magic"))
 ),
 tags$hr(),
 tags$div(style = "padding:0 14px 6px;",
 tags$p(tags$span("Filtros globales", style = "color:#6878A0; font-size:0.82rem; text-transform:uppercase; letter-spacing:0.8px; font-weight:600;"),
 style = "margin-bottom:8px;"),
 selectInput("f_plat", "Plataforma:", choices = PLATS, selected = "Todas"),
 sliderInput("f_year", "Año de lanzamiento:",
 min = YEAR_RANGE[1], max = 2024, value = c(2015, 2024), sep = "", step = 1)
 ),
 tags$div(class = "sidebar-brand",
 tags$span("Alex Terán · Ciencia de Datos"),
 tags$span("Gaming Profiles 2025 · Grupo 13")
 )
 ),
 
 dashboardBody(
 
 tabItems(
 
 # 
 # INTRODUCCIÓN
 # 
 tabItem(tabName = "introduccion",
 tags$div(class = "page-hero",
 tags$h3("Introducción"),
 tags$p("Análisis exploratorio y modelado predictivo de precios en PlayStation Store — snapshot febrero 2025")
 ),
 fluidRow(
 column(6,
 box(width = NULL, title = "Contexto del mercado", status = "primary", solidHeader = TRUE,
 tags$p(style = "color:#A8B8D0; font-size:0.97rem; line-height:1.7;",
 "El mercado digital de videojuegos en consola ha crecido de forma acelerada. PlayStation Store
 concentra decenas de miles de títulos distribuidos en múltiples géneros y plataformas (PS3, PS4, PS5),
 con precios que varían considerablemente entre categorías."),
 tags$p(style = "color:#A8B8D0; font-size:0.97rem; line-height:1.7;",
 "A diferencia de bienes físicos, el costo marginal digital es cero: los precios responden a percepción
 de valor, audiencia objetivo, competencia por género y estrategia de publishers.")
 )
 ),
 column(6,
 box(width = NULL, title = "Pregunta de investigación", status = "warning", solidHeader = TRUE,
 tags$blockquote(style = "border-left:3px solid #00D4FF; padding:12px 16px; margin:0 0 16px 0;
 background:rgba(0,212,255,0.05); border-radius:0 8px 8px 0; color:#C8D8F0; font-style:italic;",
 "¿Existe una asociación entre el género declarado de un juego y el precio listado en
 PlayStation Store (snapshot 2025)?"
 ),
 tags$p(tags$b("Subpreguntas:", style = "color:#C8D8F0;"), style = "margin-bottom:8px;"),
 tags$ol(style = "color:#8FA3C7; font-size:0.95rem; line-height:1.8; padding-left:18px;",
 tags$li("¿Qué géneros presentan medianas de precio más altas o más bajas?"),
 tags$li("¿Cómo se relaciona el volumen de títulos por género con la mediana de precio?"),
 tags$li("¿Se observan diferencias entre PS4 y PS5 dentro del mismo género?")
 )
 )
 )
 ),
 fluidRow(
 column(12,
 box(width = NULL, title = "Dataset: Gaming Profiles 2025", status = "primary", solidHeader = TRUE,
 tags$p(style = "color:#8FA8C8; font-size:0.92rem; margin-bottom:16px;",
 "Fuente: Kruglov, A. (2025). Gaming Profiles 2025. Kaggle — licencia CC0 (dominio público)."),
 fluidRow(
 column(4, tags$div(
 style = "background:linear-gradient(135deg,rgba(0,48,135,0.4),rgba(0,212,255,0.1));
 border:1px solid rgba(0,212,255,0.2); border-radius:12px; padding:20px; text-align:center;",
 tags$div(style = "font-size:2rem; margin-bottom:8px;", ""),
 tags$div(style = "color:#FFFFFF; font-size:1.4rem; font-weight:800;", "23,152"),
 tags$div(style = "color:#00D4FF; font-size:0.84rem; text-transform:uppercase; letter-spacing:0.8px; font-weight:600; margin-top:4px;", "Juegos"),
 tags$div(style = "color:#6878A0; font-size:0.84rem; margin-top:6px;", "games.csv")
 )),
 column(4, tags$div(
 style = "background:linear-gradient(135deg,rgba(6,214,160,0.15),rgba(0,48,135,0.1));
 border:1px solid rgba(6,214,160,0.2); border-radius:12px; padding:20px; text-align:center;",
 tags$div(style = "font-size:2rem; margin-bottom:8px;", ""),
 tags$div(style = "color:#FFFFFF; font-size:1.4rem; font-weight:800;", "356,600"),
 tags$div(style = "color:#06D6A0; font-size:0.84rem; text-transform:uppercase; letter-spacing:0.8px; font-weight:600; margin-top:4px;", "Jugadores"),
 tags$div(style = "color:#6878A0; font-size:0.84rem; margin-top:6px;", "players.csv")
 )),
 column(4, tags$div(
 style = "background:linear-gradient(135deg,rgba(244,162,97,0.15),rgba(230,57,70,0.1));
 border:1px solid rgba(244,162,97,0.2); border-radius:12px; padding:20px; text-align:center;",
 tags$div(style = "font-size:2rem; margin-bottom:8px;", ""),
 tags$div(style = "color:#FFFFFF; font-size:1.4rem; font-weight:800;", "62,816"),
 tags$div(style = "color:#F4A261; font-size:0.84rem; text-transform:uppercase; letter-spacing:0.8px; font-weight:600; margin-top:4px;", "Precios"),
 tags$div(style = "color:#6878A0; font-size:0.84rem; margin-top:6px;", "prices.csv")
 ))
 )
 )
 )
 )
 ),
 
 # 
 # OBJETIVOS
 # 
 tabItem(tabName = "objetivos",
 tags$div(class = "page-hero",
 tags$h3("Objetivos del análisis"),
 tags$p("Metas del proyecto de precios en el catálogo PlayStation")
 ),
 fluidRow(
 column(12,
 box(width = NULL, status = "primary", solidHeader = TRUE,
 title = "Objetivo general",
 tags$p(style = "color:#A8B8D0; font-size:1.0rem; line-height:1.7;",
 "Describir la distribución de precios del catálogo PlayStation Store (2025) y comparar patrones
 entre géneros y plataformas mediante gráficos reproducibles en R (ggplot2 / Shiny) y Python (Plotly / Dash).")
 )
 )
 ),
 fluidRow(
 column(3, tags$div(class = "obj-card",
 tags$div(class = "obj-num", "01"),
 tags$h5("ETL Reproducible"),
 tags$p("Flujo de limpieza transparente: normalización de géneros, filtro de precios válidos y expansión por género.")
 )),
 column(3, tags$div(class = "obj-card",
 tags$div(class = "obj-num", "02"),
 tags$h5("Visualizaciones"),
 tags$p("Gráficos con ggplot2 y Plotly: distribuciones, medianas por género, comparativas PS4 vs PS5.")
 )),
 column(3, tags$div(class = "obj-card",
 tags$div(class = "obj-num", "03"),
 tags$h5("Dashboard interactivo"),
 tags$p("App Shiny con filtros por plataforma y año para explorar catálogo y distribución de precios.")
 )),
 column(3, tags$div(class = "obj-card",
 tags$div(class = "obj-num", "04"),
 tags$h5("Simulador"),
 tags$p("Mediana y cuartiles (Q1–Q3) de precios por género y plataforma como benchmark de mercado.")
 ))
 ),
 tags$div(style = "margin-top:18px;"),
 fluidRow(
 column(12,
 box(width = NULL, status = "warning", solidHeader = TRUE, title = " Justificación",
 fluidRow(
 column(4,
 tags$h5(style = "color:#F4A261; font-size:0.94rem; text-transform:uppercase; letter-spacing:0.5px;", "¿Por qué videojuegos?"),
 tags$p(style = "color:#8FA3C7; font-size:0.94rem; line-height:1.6;",
 "El mercado digital genera miles de millones anuales. Entender la distribución de precios por
 género tiene valor práctico para desarrolladores y consumidores.")
 ),
 column(4,
 tags$h5(style = "color:#F4A261; font-size:0.94rem; text-transform:uppercase; letter-spacing:0.5px;", "¿Por qué PlayStation?"),
 tags$p(style = "color:#8FA3C7; font-size:0.94rem; line-height:1.6;",
 "PS Store es una de las tiendas digitales más grandes del mundo. El dataset de Kaggle ofrece
 un snapshot real de precios en 5 monedas, ideal para análisis exploratorio.")
 ),
 column(4,
 tags$h5(style = "color:#F4A261; font-size:0.94rem; text-transform:uppercase; letter-spacing:0.5px;", "Alcance"),
 tags$p(style = "color:#8FA3C7; font-size:0.94rem; line-height:1.6;",
 "Análisis descriptivo, exploratorio y predictivo (ML). Alineado con los módulos del curso de
 Visualización de Datos en R y Python.")
 )
 )
 )
 )
 )
 ),
 
 # 
 # METODOLOGÍA
 # 
 tabItem(tabName = "metodologia",
 tags$div(class = "page-hero",
 tags$h3(" Metodología"),
 tags$p("Fuente de datos, flujo ETL y decisiones de análisis")
 ),
 fluidRow(
 column(8,
 box(width = NULL, status = "primary", solidHeader = TRUE, title = " Proceso ETL — 6 pasos",
 tags$div(class = "step-card",
 tags$div(class = "step-num", "1"),
 tags$div(class = "step-content",
 tags$h5("Extracción"),
 tags$p("Carga de games.csv, players.csv y prices.csv desde Kaggle (CC0).")
 )
 ),
 tags$div(class = "step-card",
 tags$div(class = "step-num", "2"),
 tags$div(class = "step-content",
 tags$h5("Limpieza de géneros"),
 tags$p("La columna genres viene en formato lista Python. Se eliminan corchetes y comillas. Se extrae el año de release_date.")
 )
 ),
 tags$div(class = "step-card",
 tags$div(class = "step-num", "3"),
 tags$div(class = "step-content",
 tags$h5("Filtro de precios"),
 tags$p("Se eliminan precios nulos, cero o mayores a $150 USD para excluir errores y outliers.")
 )
 ),
 tags$div(class = "step-card",
 tags$div(class = "step-num", "4"),
 tags$div(class = "step-content",
 tags$h5("Expansión de géneros"),
 tags$p("Cada juego con múltiples géneros se expande a una fila por género para comparar precios dentro de cada categoría.")
 )
 ),
 tags$div(class = "step-card",
 tags$div(class = "step-num", "5"),
 tags$div(class = "step-content",
 tags$h5("Filtro de representatividad"),
 tags$p("Solo se analizan géneros con al menos 50 juegos con precio disponible.")
 )
 ),
 tags$div(class = "step-card",
 tags$div(class = "step-num", "6"),
 tags$div(class = "step-content",
 tags$h5("Variables derivadas"),
 tags$p("Se calculan mediana, Q1, Q3, media y desviación estándar por género y combinación género × plataforma.")
 )
 ),
 tags$div(class = "alert alert-warning",
 tags$b("Nota: "),
 "La expansión multi-género implica que un mismo gameid puede aparecer en varias filas. Los conteos por género son conteos de etiquetas."
 )
 )
 ),
 column(4,
 box(width = NULL, status = "info", solidHeader = TRUE, title = " Herramientas",
 lapply(list(
 list("R / ggplot2", "Visualizaciones estáticas y bookdown"),
 list("R Shiny", "Dashboard interactivo"),
 list("Python / Plotly", "Gráficos interactivos"),
 list("Python Dash", "App web multipágina"),
 list("glmnet", "Regresión Lasso"),
 list("randomForest", "Ensamble de árboles"),
 list("xgboost", "Gradient boosting")
 ), function(row) {
 tags$div(style = "display:flex; justify-content:space-between; align-items:center;
 padding:8px 0; border-bottom:1px solid rgba(255,255,255,0.05);",
 tags$span(style = "color:#C8D8F0; font-size:0.92rem; font-weight:600;", row[[1]]),
 tags$span(style = "color:#8FA8C8; font-size:0.88rem;", row[[2]])
 )
 })
 ),
 box(width = NULL, status = "warning", solidHeader = TRUE, title = " Variables clave",
 lapply(list(
 list("usd", "Precio en dólares (feb. 2025)"),
 list("genres", "Géneros: se expande a filas"),
 list("platform", "PS3, PS4 o PS5"),
 list("country", "País del jugador")
 ), function(row) {
 tags$div(style = "display:flex; justify-content:space-between; align-items:center;
 padding:8px 0; border-bottom:1px solid rgba(255,255,255,0.05);",
 tags$code(style = "color:#00D4FF; font-size:0.9rem; background:rgba(0,212,255,0.1);
 padding:2px 8px; border-radius:4px;", row[[1]]),
 tags$span(style = "color:#8FA8C8; font-size:0.88rem;", row[[2]])
 )
 })
 )
 )
 )
 ),
 
 # 
 # RESUMEN
 # 
 tabItem(tabName = "resumen",
 tags$div(class = "page-hero",
 tags$h3("Resumen ejecutivo"),
 tags$p("Vista global del catálogo PlayStation Store 2025")
 ),
 fluidRow(
 column(3, uiOutput("kpi_juegos")),
 column(3, uiOutput("kpi_jugadores")),
 column(3, uiOutput("kpi_paises")),
 column(3, uiOutput("kpi_precio"))
 ),
 fluidRow(
 box(title = "Catálogo por plataforma",
 status = "primary", solidHeader = TRUE, width = 5,
 plotlyOutput("p_plataforma", height = "280px")),
 box(title = " Lanzamientos anuales",
 status = "primary", solidHeader = TRUE, width = 7,
 plotlyOutput("p_años", height = "280px"))
 ),
 fluidRow(
 box(title = " Top 10 países — jugadores",
 status = "success", solidHeader = TRUE, width = 6,
 plotlyOutput("p_mapa_resumen", height = "280px")),
 box(title = "Insights clave",
 status = "warning", solidHeader = TRUE, width = 6,
 tags$div(class = "insight-card",
 tags$span("", class = "ic-emoji"),
 tags$div(class = "ic-text", tags$strong("PS4 sigue dominando: "),
 "Con el 61% del catálogo (14.163 juegos), supera a PS5 a pesar de llevar 4+ años en el mercado.")
 ),
 tags$div(class = "insight-card",
 tags$span("", class = "ic-emoji"),
 tags$div(class = "ic-text", tags$strong("Crecimiento explosivo: "),
 "Los lanzamientos crecieron 1.570% en una década: de 305 juegos en 2013 a 5.091 en 2024.")
 ),
 tags$div(class = "insight-card",
 tags$span("", class = "ic-emoji"),
 tags$div(class = "ic-text", tags$strong("Mercado ultra-accesible: "),
 "El 86% de los juegos cuesta menos de $20 (mediana: $7.99). PlayStation apuesta por volumen.")
 ),
 tags$div(class = "insight-card",
 tags$span("", class = "ic-emoji"),
 tags$div(class = "ic-text", tags$strong("EE.UU. + Europa = 59%: "),
 "Norteamérica y Europa Occidental concentran más de la mitad de los jugadores globales.")
 ),
 tags$div(class = "insight-card",
 tags$span("", class = "ic-emoji"),
 tags$div(class = "ic-text", tags$strong("El indie es el motor: "),
 "Los 3 publishers más activos (eastasiasoft, Ratalaika, ThiGames) son indie de alto volumen.")
 )
 )
 )
 ),
 
 # 
 # CATÁLOGO
 # 
 tabItem(tabName = "catalogo",
 tags$div(class = "page-hero",
 tags$h3(" Catálogo PlayStation"),
 tags$p("Análisis de géneros, publishers y precios por categoría")
 ),
 fluidRow(
 column(4, uiOutput("cat_total")),
 column(4, uiOutput("cat_plats")),
 column(4, uiOutput("cat_generos"))
 ),
 fluidRow(
 box(title = "Top géneros por volumen",
 status = "primary", solidHeader = TRUE, width = 6,
 sliderInput("sl_ngen", "Mostrar top N géneros:", min = 5, max = 20, value = 12, step = 1),
 plotlyOutput("p_generos", height = "320px")),
 box(title = "Top publishers",
 status = "primary", solidHeader = TRUE, width = 6,
 plotlyOutput("p_publishers", height = "370px"))
 ),
 fluidRow(
 box(title = "Precio mediano por género — top 12 más caros",
 status = "info", solidHeader = TRUE, width = 12,
 plotlyOutput("p_precio_gen", height = "300px"))
 ),
 fluidRow(
 box(title = "Catálogo completo",
 status = "primary", solidHeader = TRUE, width = 12,
 DTOutput("tabla_catalogo"))
 )
 ),
 
 # 
 # JUGADORES
 # 
 tabItem(tabName = "jugadores",
 tags$div(class = "page-hero",
 tags$h3(" Geografía de jugadores"),
 tags$p("Distribución global de la base de jugadores PlayStation")
 ),
 fluidRow(
 column(4, uiOutput("jug_total")),
 column(4, uiOutput("jug_paises")),
 column(4, uiOutput("jug_lider"))
 ),
 fluidRow(
 box(title = " Filtros",
 status = "warning", solidHeader = TRUE, width = 3,
 selectInput("dd_pais", "País:", choices = c("Todos", sort(unique(players$country))), selected = "Todos"),
 sliderInput("sl_top_paises", "Top N países:", min = 5, max = 30, value = 15, step = 5),
 tags$hr(),
 tags$p(style = "color:#8FA8C8; font-size:0.9rem;",
 "Selecciona un país para ver sus datos, o 'Todos' para vista global.")
 ),
 box(title = " Jugadores por país",
 status = "success", solidHeader = TRUE, width = 9,
 plotlyOutput("p_paises", height = "380px"))
 ),
 fluidRow(
 box(title = " Concentración geográfica",
 status = "success", solidHeader = TRUE, width = 8,
 plotlyOutput("p_burbuja_paises", height = "320px")),
 box(title = " Distribución top 6 países",
 status = "success", solidHeader = TRUE, width = 4,
 plotlyOutput("p_pie_paises", height = "320px"))
 )
 ),
 
 # 
 # PRECIOS
 # 
 tabItem(tabName = "precios",
 tags$div(class = "page-hero",
 tags$h3(" Análisis de precios"),
 tags$p("Distribución, rangos, monedas y series temporales — snapshot febrero 2025")
 ),
 fluidRow(
 column(3, uiOutput("pr_prom")),
 column(3, uiOutput("pr_mediana")),
 column(3, uiOutput("pr_min")),
 column(3, uiOutput("pr_max"))
 ),
 fluidRow(
 box(title = " Distribución de precios (USD)",
 status = "success", solidHeader = TRUE, width = 7,
 plotlyOutput("p_hist_precio", height = "320px")),
 box(title = " Segmentos de precio",
 status = "success", solidHeader = TRUE, width = 5,
 plotlyOutput("p_rangos", height = "320px"))
 ),
 fluidRow(
 box(title = " Boxplot por moneda",
 status = "primary", solidHeader = TRUE, width = 6,
 plotlyOutput("p_box_monedas", height = "290px")),
 box(title = "Correlación entre monedas",
 status = "primary", solidHeader = TRUE, width = 6,
 plotlyOutput("p_correlacion", height = "290px"))
 ),
 fluidRow(
 box(title = " Precio medio diario + media móvil 14 días",
 status = "info", solidHeader = TRUE, width = 12,
 plotlyOutput("p_ts_precio", height = "300px"))
 )
 ),
 
 # 
 # SIMULADOR
 # 
 tabItem(tabName = "simulador",
 tags$div(class = "page-hero",
 tags$h3(" Simulador de benchmark"),
 tags$p("Consulta la mediana y cuartiles de precio para tu combinación género × plataforma")
 ),
 fluidRow(
 box(title = " Configurar consulta",
 status = "warning", solidHeader = TRUE, width = 4,
 selectInput("sim_genre", "Género declarado:", choices = GENRES_SIM, selected = GENRES_SIM[1]),
 selectInput("sim_plat", "Plataforma objetivo:", choices = PLATS,
 selected = if ("PS5" %in% PLATS) "PS5" else PLATS[1]),
 tags$hr(),
 tags$p(style = "color:#8FA8C8; font-size:0.9rem; line-height:1.5;",
 "«Todas» agrega todas las plataformas. Basado en precios listados (feb. 2025), sin datos de ventas ni demanda.")
 ),
 box(title = " Benchmark de mercado",
 status = "primary", solidHeader = TRUE, width = 8,
 uiOutput("sim_ui"))
 )
 ),
 
 # 
 # CALIDAD DE DATOS
 # 
 tabItem(tabName = "calidad",
 tags$div(class = "page-hero",
 tags$h3(" Calidad de datos"),
 tags$p("Valores faltantes en los archivos crudos antes del ETL")
 ),
 fluidRow(
 box(title = " % de valores faltantes por columna (CSV sin filtrar)",
 status = "warning", solidHeader = TRUE, width = 12,
 tags$p(style = "color:#8FA8C8; font-size:0.92rem; margin-bottom:12px;",
 "Mismo criterio que la vista equivalente en Dash: % NA por columna sobre los CSV sin aplicar filtros."),
 plotlyOutput("p_miss", height = "400px"))
 )
 ),
 
 # 
 # EXPLORADOR
 # 
 tabItem(tabName = "explorador",
 tags$div(class = "page-hero",
 tags$h3(" Explorador interactivo"),
 tags$p("Filtra, cruza y busca en el catálogo completo")
 ),
 fluidRow(
 box(title = " Filtros de búsqueda",
 status = "warning", solidHeader = TRUE, width = 12,
 fluidRow(
 column(4, sliderInput("exp_precio", "Rango de precio USD:", min = 0, max = 100, value = c(0, 60))),
 column(4, selectInput("exp_plat2", "Plataforma:", choices = PLATS, selected = "Todas")),
 column(4, selectInput("exp_gen", "Género:", choices = NULL))
 ))
 ),
 fluidRow(
 box(title = " USD vs EUR — dispersión por juego",
 status = "primary", solidHeader = TRUE, width = 7,
 plotlyOutput("exp_scatter", height = "340px")),
 box(title = " Precio promedio por género (filtro actual)",
 status = "primary", solidHeader = TRUE, width = 5,
 plotlyOutput("exp_gen_precio", height = "340px"))
 ),
 fluidRow(
 box(title = " Resultados filtrados",
 status = "primary", solidHeader = TRUE, width = 12,
 DTOutput("exp_tabla"))
 )
 ),
 
 # 
 # MODELOS ML
 # 
 tabItem(tabName = "modelos",
 tags$div(class = "page-hero",
 tags$h3(" Modelos predictivos"),
 tags$p("Comparación de Regresión Lineal, Random Forest y XGBoost")
 ),
 fluidRow(
 box(title = " Mejor modelo", status = "success", solidHeader = TRUE, width = 4,
 uiOutput("best_model_box")),
 box(title = " Comparativa de métricas", status = "primary", solidHeader = TRUE, width = 8,
 DTOutput("metrics_table"))
 ),
 fluidRow(
 box(title = " Visualización de métricas por modelo",
 status = "primary", solidHeader = TRUE, width = 12,
 plotlyOutput("metrics_plot", height = "380px"))
 ),
 fluidRow(
 box(title = " Justificación del modelo ganador",
 status = "info", solidHeader = TRUE, width = 12,
 uiOutput("model_justification"))
 )
 ),
 
 # 
 # PREDICTOR
 # 
 tabItem(tabName = "prediccion",
 tags$div(class = "page-hero",
 tags$h3(" Predictor de precios"),
 tags$p("Estima el precio de un juego PlayStation con Random Forest")
 ),
 fluidRow(
 box(title = " Características del juego",
 status = "warning", solidHeader = TRUE, width = 4,
 selectInput("pred_genre", " Género:", choices = NULL),
 selectInput("pred_platform", " Plataforma:", choices = NULL),
 sliderInput("pred_year", " Año:", min = 2015, max = 2024, value = 2024, sep = ""),
 tags$br(),
 actionButton("predict_btn", " Predecir precio",
 class = "btn btn-predict")
 ),
 box(title = " Precio estimado",
 status = "success", solidHeader = TRUE, width = 8,
 uiOutput("prediction_result"))
 ),
 fluidRow(
 box(title = " Rango de precios predichos por género",
 status = "primary", solidHeader = TRUE, width = 12,
 plotlyOutput("sensitivity_plot", height = "440px"))
 ),
 fluidRow(
 box(title = " Sobre el modelo",
 status = "info", solidHeader = TRUE, width = 12,
 fluidRow(
 column(3, tags$div(style = "text-align:center; padding:12px;",
 tags$div(style = "font-size:1.8rem;", ""),
 tags$div(style = "color:#C8D8F0; font-weight:700; font-size:1.0rem; margin-top:6px;", "Random Forest"),
 tags$div(style = "color:#8FA8C8; font-size:0.88rem;", "Modelo ganador")
 )),
 column(3, tags$div(style = "text-align:center; padding:12px;",
 tags$div(style = "font-size:1.8rem;", ""),
 tags$div(style = "color:#C8D8F0; font-weight:700; font-size:1.0rem; margin-top:6px;", "Predictores"),
 tags$div(style = "color:#8FA8C8; font-size:0.88rem;", "Género, plataforma, año")
 )),
 column(3, tags$div(style = "text-align:center; padding:12px;",
 tags$div(style = "font-size:1.8rem;", ""),
 tags$div(style = "color:#C8D8F0; font-weight:700; font-size:1.0rem; margin-top:6px;", "Validado"),
 tags$div(style = "color:#8FA8C8; font-size:0.88rem;", "80/20 train-test split")
 )),
 column(3, tags$div(style = "text-align:center; padding:12px;",
 tags$div(style = "font-size:1.8rem;", ""),
 tags$div(style = "color:#C8D8F0; font-weight:700; font-size:1.0rem; margin-top:6px;", "Solo referencial"),
 tags$div(style = "color:#8FA8C8; font-size:0.88rem;", "Herramienta educativa")
 ))
 )
 )
 )
 )
 )
 )
)

# 
# SERVER
# 
server <- function(input, output, session) {
 
 # Reactive filters 
 gf <- reactive({
 df <- games
 if (input$f_plat != "Todas") df <- df %>% filter(platform == input$f_plat)
 df %>% filter(!is.na(year), year >= input$f_year[1], year <= input$f_year[2])
 })
 pf <- reactive({
 df <- prices
 if (input$f_plat != "Todas") {
 ids <- games %>% filter(platform == input$f_plat) %>% pull(gameid)
 df <- df %>% filter(gameid %in% ids)
 }
 df
 })
 
 # Reactivos derivados cacheados (evitan separate_rows repetido) 
 gf_genres <- reactive({
 gf() %>%
 filter(genres_clean != "") %>%
 separate_rows(genres_clean, sep = ",\\s*") %>%
 filter(genres_clean != "") %>%
 mutate(genres_clean = str_trim(genres_clean))
 })
 
 gf_publishers <- reactive({
 gf() %>%
 filter(publishers_clean != "") %>%
 separate_rows(publishers_clean, sep = ",\\s*") %>%
 filter(publishers_clean != "") %>%
 mutate(publishers_clean = str_trim(publishers_clean))
 })
 
 # Explorador géneros
 observe({
 gen <- genres_long %>% pull(genres_clean) %>% unique() %>% sort()
 updateSelectInput(session, "exp_gen", choices = c("Todos", gen), selected = "Todos")
 })
 
 # KPIs RESUMEN 
 output$kpi_juegos <- renderUI(
 kpi_box(comma(nrow(gf())), "Juegos en catálogo", "", "kpi-blue", "kpi-glow-blue"))
 output$kpi_jugadores <- renderUI(
 kpi_box(comma(N_PLAYERS), "Jugadores registrados", "", "kpi-green", "kpi-glow-green"))
 output$kpi_paises <- renderUI(
 kpi_box(N_COUNTRIES, "Países representados", "", "kpi-purple", "kpi-glow-purple"))
 output$kpi_precio <- renderUI(
 kpi_box(dollar(round(median(pf()$usd, na.rm = TRUE), 2)),
 "Precio mediano USD", "", "kpi-gold", "kpi-glow-gold"))
 
 # Plataforma
 output$p_plataforma <- renderPlotly({
 gf() %>% count(platform, sort = TRUE) %>%
 mutate(pct = round(n/sum(n)*100, 1)) %>%
 plot_ly(y = ~reorder(platform, n), x = ~n, type = "bar", orientation = "h",
 marker = list(
 color = ~n,
 colorscale = list(c(0, "#003087"), c(1, "#00D4FF")),
 showscale = FALSE,
 line = list(color = "rgba(0,0,0,0)")
 ),
 text = ~paste0(comma(n), " (", pct, "%)"),
 textfont = list(color = "#C8D8F0", size = 11),
 textposition = "outside",
 hovertemplate = "<b>%{y}</b><br>%{text}<extra></extra>") %>%
 ps_layout(xaxis = list(title = "Juegos", tickfont = list(size=10)),
 yaxis = list(title = ""), margin = list(l=5, r=60, t=5, b=30))
 })
 
 # Años
 output$p_años <- renderPlotly({
 gf() %>% filter(!is.na(year)) %>%
 count(year, platform) %>%
 plot_ly(x = ~year, y = ~n, color = ~platform,
 colors = c("#001f5b","#003087","#0070CC","#00D4FF"),
 type = "bar",
 hovertemplate = "Año: %{x}<br>Juegos: %{y:,}<extra></extra>") %>%
 ps_layout(barmode = "stack",
 xaxis = list(title = "Año", dtick = 1, tickfont = list(size=10)),
 yaxis = list(title = "Juegos lanzados"),
 legend = list(orientation = "h", y = -0.3, font = list(size=10)))
 })
 
 # Mapa resumen
 output$p_mapa_resumen <- renderPlotly({
 players %>% count(country, sort = TRUE) %>% slice_head(n = 10) %>%
 mutate(pct = round(n/N_PLAYERS*100, 1)) %>%
 plot_ly(x = ~n, y = ~reorder(country, n), type = "bar", orientation = "h",
 marker = list(color = ~n,
 colorscale = list(c(0,"#06D6A0"), c(1,"#003087")),
 showscale = FALSE),
 text = ~paste0(comma(n), " (", pct, "%)"),
 hovertemplate = "<b>%{y}</b><br>%{text}<extra></extra>") %>%
 ps_layout(xaxis = list(title = "Jugadores"), yaxis = list(title = ""))
 })
 
 # CATÁLOGO KPIs 
 output$cat_total <- renderUI(kpi_box(comma(nrow(gf())), "Juegos", "", "kpi-blue", "kpi-glow-blue"))
 output$cat_plats <- renderUI(kpi_box(n_distinct(gf()$platform), "Plataformas", "", "kpi-purple", "kpi-glow-purple"))
 output$cat_generos <- renderUI({
 n <- gf_genres() %>% pull(genres_clean) %>% n_distinct()
 kpi_box(n, "Géneros únicos", "", "kpi-gold", "kpi-glow-gold")
 })
 
 output$p_generos <- renderPlotly({
 gf_genres() %>%
 count(genres_clean, sort = TRUE) %>%
 slice_head(n = input$sl_ngen) %>%
 plot_ly(x = ~n, y = ~reorder(genres_clean, n), type = "bar", orientation = "h",
 marker = list(color = ~n,
 colorscale = list(c(0, "#003087"), c(1, "#00D4FF")),
 showscale = FALSE),
 hovertemplate = "<b>%{y}</b><br>%{x:,} juegos<extra></extra>") %>%
 ps_layout(xaxis = list(title = "Juegos"), yaxis = list(title = ""))
 })
 
 output$p_publishers <- renderPlotly({
 gf_publishers() %>%
 count(publishers_clean, sort = TRUE) %>%
 slice_head(n = 10) %>%
 plot_ly(x = ~n, y = ~reorder(publishers_clean, n), type = "bar", orientation = "h",
 marker = list(color = ~n,
 colorscale = list(c(0, "#7B2FBE"), c(1, "#00D4FF")),
 showscale = FALSE),
 hovertemplate = "<b>%{y}</b><br>%{x:,} juegos<extra></extra>") %>%
 ps_layout(xaxis = list(title = "Juegos"), yaxis = list(title = ""))
 })
 
 output$p_precio_gen <- renderPlotly({
 precio_genero %>%
 slice_max(precio_med, n = 12) %>%
 plot_ly(x = ~precio_med, y = ~reorder(genres_clean, precio_med),
 type = "bar", orientation = "h",
 marker = list(color = ~precio_med,
 colorscale = list(c(0,"#F4A261"), c(1,"#E63946")),
 showscale = FALSE),
 text = ~paste0("$", round(precio_med, 2), " — n=", comma(n)),
 hovertemplate = "<b>%{y}</b><br>%{text}<extra></extra>") %>%
 ps_layout(xaxis = list(title = "Precio mediano (USD)", tickprefix = "$"),
 yaxis = list(title = ""))
 })
 
 output$tabla_catalogo <- renderDT({
 gf() %>%
 select(gameid, title, platform, year, genres_clean, publishers_clean) %>%
 rename(ID = gameid, Título = title, Plataforma = platform,
 Año = year, Géneros = genres_clean, Publisher = publishers_clean)
 }, options = list(pageLength = 8, scrollX = TRUE,
 language = list(search = "Buscar:")),
 rownames = FALSE,
 class = "display compact")
 
 # JUGADORES KPIs 
 output$jug_total <- renderUI(kpi_box(comma(N_PLAYERS), "Jugadores", "", "kpi-blue", "kpi-glow-blue"))
 output$jug_paises <- renderUI(kpi_box(N_COUNTRIES, "Países", "", "kpi-purple", "kpi-glow-purple"))
 output$jug_lider <- renderUI({
 top <- players %>% count(country, sort = TRUE) %>% slice_head(n = 1)
 kpi_box(top$country, paste0("País líder — ", comma(top$n)), "", "kpi-gold", "kpi-glow-gold")
 })
 
 jug_filtrado <- reactive({
 df <- players
 if (input$dd_pais != "Todos") df <- df %>% filter(country == input$dd_pais)
 df %>% count(country, sort = TRUE) %>% slice_head(n = input$sl_top_paises)
 })
 
 output$p_paises <- renderPlotly({
 jug_filtrado() %>%
 mutate(pct = round(n/N_PLAYERS*100, 1)) %>%
 plot_ly(x = ~n, y = ~reorder(country, n), type = "bar", orientation = "h",
 marker = list(color = ~n,
 colorscale = list(c(0,"#06D6A0"), c(1,"#003087")),
 showscale = FALSE),
 text = ~paste0(comma(n), " (", pct, "%)"),
 hovertemplate = "<b>%{y}</b><br>%{text}<extra></extra>") %>%
 ps_layout(xaxis = list(title = "Jugadores"), yaxis = list(title = ""))
 })
 
 output$p_burbuja_paises <- renderPlotly({
 players %>% count(country, sort = TRUE) %>% slice_head(n = 25) %>%
 mutate(rank = row_number()) %>%
 plot_ly(x = ~rank, y = ~n, type = "scatter", mode = "markers+text",
 text = ~country, textposition = "top center",
 textfont = list(color = "#6A84B0", size = 9),
 marker = list(size = ~sqrt(n)*1.8, sizemode = "diameter",
 color = ~n,
 colorscale = list(c(0,"#003087"), c(1,"#00D4FF")),
 showscale = FALSE,
 line = list(color = "rgba(0,212,255,0.3)", width = 1)),
 hovertemplate = "<b>%{text}</b><br>%{y:,} jugadores<extra></extra>") %>%
 ps_layout(xaxis = list(title = "Ranking", showgrid = FALSE),
 yaxis = list(title = "Jugadores"))
 })
 
 output$p_pie_paises <- renderPlotly({
 top6 <- players %>% count(country, sort = TRUE) %>% slice_head(n = 6)
 otros <- tibble(country = "Otros", n = N_PLAYERS - sum(top6$n))
 bind_rows(top6, otros) %>%
 plot_ly(labels = ~country, values = ~n, type = "pie", hole = 0.5,
 marker = list(colors = c("#001f5b","#003087","#004DB3","#0070CC","#00A3D4","#00D4FF","#1A2744"),
 line = list(color = "#0A0E1A", width = 2)),
 textinfo = "label+percent",
 textfont = list(size = 10, color = "#C8D8F0"),
 hovertemplate = "<b>%{label}</b><br>%{value:,}<extra></extra>") %>%
 ps_layout(showlegend = FALSE)
 })
 
 # PRECIOS KPIs 
 output$pr_prom <- renderUI(kpi_box(dollar(round(mean(pf()$usd, na.rm=TRUE),2)), "Precio promedio", "", "kpi-blue", "kpi-glow-blue"))
 output$pr_mediana <- renderUI(kpi_box(dollar(round(median(pf()$usd, na.rm=TRUE),2)), "Precio mediano", "", "kpi-green", "kpi-glow-green"))
 output$pr_min <- renderUI(kpi_box(dollar(min(pf()$usd, na.rm=TRUE)), "Precio mínimo", "", "kpi-purple", "kpi-glow-purple"))
 output$pr_max <- renderUI(kpi_box(dollar(max(pf()$usd, na.rm=TRUE)), "Precio máximo", "", "kpi-gold", "kpi-glow-gold"))
 
 output$p_hist_precio <- renderPlotly({
 med_p <- median(pf()$usd, na.rm = TRUE)
 prom_p <- mean(pf()$usd, na.rm = TRUE)
 pf() %>% filter(usd <= 70) %>%
 plot_ly(x = ~usd, type = "histogram", nbinsx = 32,
 marker = list(color = "rgba(0,212,255,0.7)",
 line = list(color = "#0A0E1A", width = 0.6)),
 hovertemplate = "$%{x:.0f} — %{y:,} juegos<extra></extra>") %>%
 ps_layout(
 xaxis = list(title = "Precio (USD)", tickprefix = "$"),
 yaxis = list(title = "Frecuencia"),
 shapes = list(
 list(type="line", x0=med_p, x1=med_p, y0=0, y1=1, yref="paper",
 line=list(color="#E63946", dash="dash", width=2)),
 list(type="line", x0=prom_p, x1=prom_p, y0=0, y1=1, yref="paper",
 line=list(color="#F4A261", dash="dot", width=2))
 ),
 annotations = list(
 list(x=med_p, y=0.93, yref="paper", text=paste0("Mediana $",round(med_p,2)),
 font=list(color="#E63946",size=11), showarrow=FALSE, xanchor="left"),
 list(x=prom_p, y=0.82, yref="paper", text=paste0("Media $",round(prom_p,2)),
 font=list(color="#F4A261",size=11), showarrow=FALSE, xanchor="left")
 )
 )
 })
 
 output$p_rangos <- renderPlotly({
 pf() %>%
 mutate(rango = factor(case_when(
 usd <= 5 ~ "≤$5", usd <= 20 ~ "$5–20",
 usd <= 40 ~ "$20–40", usd <= 70 ~ "$40–70", TRUE ~ ">$70"),
 levels = c("≤$5","$5–20","$20–40","$40–70",">$70"))) %>%
 count(rango) %>%
 mutate(pct = round(n/sum(n)*100, 1)) %>%
 plot_ly(x = ~rango, y = ~pct, type = "bar",
 marker = list(color = c("#001f5b","#003087","#0070CC","#00A3D4","#00D4FF"),
 line = list(color = "#0A0E1A", width = 1)),
 text = ~paste0(pct, "%"), textposition = "outside",
 textfont = list(color = "#C8D8F0", size = 12),
 hovertemplate = "%{x}<br>%{y:.1f}%<extra></extra>") %>%
 ps_layout(yaxis = list(title = "%", ticksuffix = "%"),
 xaxis = list(title = "Segmento de precio"), showlegend = FALSE)
 })
 
 output$p_box_monedas <- renderPlotly({
 prices %>%
 select(usd, eur, gbp) %>%
 filter(if_all(everything(), ~!is.na(.) & . > 0 & . < 80)) %>%
 pivot_longer(everything(), names_to = "Moneda", values_to = "Precio") %>%
 mutate(Moneda = toupper(Moneda)) %>%
 plot_ly(x = ~Moneda, y = ~Precio, type = "box", color = ~Moneda,
 colors = c("#00D4FF","#7B2FBE","#06D6A0"),
 hovertemplate = "%{x}: %{y:.2f}<extra></extra>") %>%
 ps_layout(showlegend = FALSE,
 xaxis = list(title = "Moneda"),
 yaxis = list(title = "Precio", tickprefix = "$"))
 })
 
 output$p_correlacion <- renderPlotly({
 cor_data <- prices %>% select(usd, eur, gbp, jpy, rub) %>% filter(complete.cases(.))
 cor_mat <- cor(cor_data)
 plot_ly(z = cor_mat, x = colnames(cor_mat), y = rownames(cor_mat),
 type = "heatmap",
 colorscale = list(c(0,"#0A0E1A"), c(0.5,"#003087"), c(1,"#00D4FF")),
 zmin = -1, zmax = 1,
 text = round(cor_mat, 2),
 texttemplate = "%{text}",
 hovertemplate = "%{y} vs %{x}<br>r = %{z:.2f}<extra></extra>") %>%
 ps_layout()
 })
 
 output$p_ts_precio <- renderPlotly({
 game_ids <- gf()$gameid
 df <- pf() %>%
 filter(!is.na(date_acquired), gameid %in% game_ids) %>%
 group_by(date_acquired) %>%
 summarise(mean_usd = mean(usd, na.rm = TRUE), .groups = "drop") %>%
 arrange(date_acquired)
 if (nrow(df) < 2) return(plot_ly() %>% layout(title = "Sin datos para el filtro actual"))
 n_rows <- nrow(df)
 roll <- vapply(seq_len(n_rows), function(i) mean(df$mean_usd[max(1L, i-13L):i], na.rm=TRUE), numeric(1))
 plot_ly(df, x = ~date_acquired) %>%
 add_lines(y = ~mean_usd, name = "Media diaria",
 line = list(color = "rgba(0,212,255,0.35)", width = 1),
 hovertemplate = "%{x|%Y-%m-%d}<br>$%{y:.2f}<extra></extra>") %>%
 add_lines(x = ~date_acquired, y = roll, name = "Media móvil 14d",
 line = list(color = "#00D4FF", width = 2.5),
 hovertemplate = "%{x|%Y-%m-%d}<br>$%{y:.2f}<extra></extra>") %>%
 ps_layout(xaxis = list(title = "Fecha"),
 yaxis = list(title = "USD", tickprefix = "$"),
 legend = list(orientation = "h", y = 1.12, x = 0, font = list(size=10)))
 })
 
 # SIMULADOR 
 output$sim_ui <- renderUI({
 req(input$sim_genre)
 sub <- sim_base %>% filter(genres_clean == input$sim_genre)
 if (input$sim_plat != "Todas") sub <- sub %>% filter(platform == input$sim_plat)
 if (nrow(sub) < 10) {
 return(tags$div(class = "alert alert-warning",
 paste0("Menos de 10 observaciones (n = ", nrow(sub), "). Prueba otra plataforma.")))
 }
 q1 <- quantile(sub$usd, 0.25)
 med <- median(sub$usd)
 q3 <- quantile(sub$usd, 0.75)
 tagList(
 tags$div(class = "bench-row",
 tags$span(class = "bench-label", "Q1 — Percentil 25"),
 tags$span(class = "bench-value", dollar(round(q1, 2)))),
 tags$div(class = "bench-row",
 tags$span(class = "bench-label", "Mediana"),
 tags$span(class = "bench-value highlight", dollar(round(med, 2)))),
 tags$div(class = "bench-row",
 tags$span(class = "bench-label", "Q3 — Percentil 75"),
 tags$span(class = "bench-value", dollar(round(q3, 2)))),
 tags$div(class = "bench-row",
 tags$span(class = "bench-label", "Observaciones"),
 tags$span(class = "bench-value", comma(nrow(sub)))),
 tags$p(style = "color:#6878A0; font-size:0.87rem; margin-top:10px;",
 "Basado en precios listados (snapshot feb. 2025). Sin datos de ventas ni demanda.")
 )
 })
 
 # CALIDAD 
 output$p_miss <- renderPlotly({
 if (nrow(miss_plot_df) == 0) {
 return(plot_ly() %>% layout(title = "Sin NA detectados"))
 }
 miss_plot_df %>%
 plot_ly(x = ~missing_pct, y = ~reorder(label, missing_pct), color = ~dataset,
 type = "bar", orientation = "h",
 colors = c(games = "#00D4FF", players = "#06D6A0", prices = "#F4A261")) %>%
 ps_layout(xaxis = list(title = "% faltante", ticksuffix = "%"),
 yaxis = list(title = ""),
 legend = list(title = list(text = "Tabla", font = list(color="#C8D8F0")),
 font = list(size=10)))
 })
 
 # EXPLORADOR 
 datos_exp <- reactive({
 df <- games_prices
 if (input$exp_plat2 != "Todas") df <- df %>% filter(platform == input$exp_plat2)
 if (!is.null(input$exp_gen) && input$exp_gen != "Todos")
 df <- df %>% filter(str_detect(genres_clean, fixed(input$exp_gen, TRUE)))
 df %>% filter(usd >= input$exp_precio[1], usd <= input$exp_precio[2])
 })
 
 output$exp_scatter <- renderPlotly({
 datos_exp() %>% filter(!is.na(eur), eur > 0, eur < 100) %>%
 plot_ly(x = ~usd, y = ~eur, type = "scatter", mode = "markers",
 color = ~platform,
 colors = c("#001f5b","#003087","#0070CC","#00D4FF"),
 marker = list(size = 5, opacity = 0.55,
 line = list(color = "rgba(0,0,0,0)")),
 text = ~paste0("<b>", title, "</b><br>", platform, "<br>USD $", usd, " | EUR €", eur),
 hovertemplate = "%{text}<extra></extra>") %>%
 ps_layout(xaxis = list(title = "USD", tickprefix = "$"),
 yaxis = list(title = "EUR", tickprefix = "€"),
 legend = list(orientation = "h", y = -0.25, font = list(size=10)))
 })
 
 output$exp_gen_precio <- renderPlotly({
 datos_exp() %>% filter(genres_clean != "") %>%
 separate_rows(genres_clean, sep = ",\\s*") %>% filter(genres_clean != "") %>%
 group_by(genres_clean) %>%
 summarise(precio = mean(usd, na.rm = TRUE), n = n(), .groups = "drop") %>%
 filter(n >= 3) %>% slice_max(precio, n = 10) %>%
 plot_ly(x = ~precio, y = ~reorder(genres_clean, precio), type = "bar", orientation = "h",
 marker = list(color = ~precio,
 colorscale = list(c(0,"#003087"), c(1,"#06D6A0")),
 showscale = FALSE),
 hovertemplate = "<b>%{y}</b><br>$%{x:.2f}<extra></extra>") %>%
 ps_layout(xaxis = list(title = "Precio promedio", tickprefix = "$"),
 yaxis = list(title = ""))
 })
 
 output$exp_tabla <- renderDT({
 datos_exp() %>%
 select(title, platform, year, genres_clean, publishers_clean, usd, eur, gbp) %>%
 rename(Título = title, Plataforma = platform, Año = year,
 Géneros = genres_clean, Publisher = publishers_clean,
 USD = usd, EUR = eur, GBP = gbp)
 }, options = list(pageLength = 6, scrollX = TRUE, language = list(search = "Buscar:")),
 rownames = FALSE, class = "display compact")
 
 # MODELOS 
 output$best_model_box <- renderUI({
 models <- TRAINED_MODELS
 if (is.null(models)) return(tags$div(class = "alert alert-warning", "Modelos no disponibles. Verifica que xgboost y randomForest estén instalados."))
 best_name <- if (models$metrics$rf$r2 > models$metrics$xgb$r2 &&
 models$metrics$rf$r2 > models$metrics$linear$r2) "Random Forest"
 else if (models$metrics$xgb$r2 > models$metrics$linear$r2) "XGBoost"
 else "Regresión Lineal"
 bm <- if (best_name == "Random Forest") models$metrics$rf
 else if (best_name == "XGBoost") models$metrics$xgb
 else models$metrics$linear
 tags$div(class = "model-best",
 tags$div(class = "model-name", paste0("", best_name)),
 tags$div(class = "metric-pill mp-r2", paste0("R² = ", sprintf("%.4f", bm$r2))),
 tags$div(class = "metric-pill mp-rmse", paste0("RMSE = $", sprintf("%.2f", bm$rmse))),
 tags$div(class = "metric-pill mp-mae", paste0("MAE = $", sprintf("%.2f", bm$mae)))
 )
 })
 
 output$metrics_table <- renderDT({
 models <- TRAINED_MODELS
 if (is.null(models)) return(datatable(tibble(Mensaje = "Modelos no disponibles")))
 tibble(
 Modelo = c("Regresión Lineal","XGBoost","Random Forest"),
 `R²` = c(sprintf("%.4f", models$metrics$linear$r2),
 sprintf("%.4f", models$metrics$xgb$r2),
 sprintf("%.4f", models$metrics$rf$r2)),
 RMSE = c(sprintf("$%.2f", models$metrics$linear$rmse),
 sprintf("$%.2f", models$metrics$xgb$rmse),
 sprintf("$%.2f", models$metrics$rf$rmse)),
 MAE = c(sprintf("$%.2f", models$metrics$linear$mae),
 sprintf("$%.2f", models$metrics$xgb$mae),
 sprintf("$%.2f", models$metrics$rf$mae))
 ) %>% arrange(desc(`R²`))
 }, options = list(paging=FALSE, searching=FALSE, info=FALSE,
 columnDefs = list(list(targets=0:3, className="dt-center"))),
 class = "display compact")
 
 output$metrics_plot <- renderPlotly({
 models <- TRAINED_MODELS
 if (is.null(models)) return(plot_ly() %>% layout(title = "Modelos no disponibles"))
 df_plot <- tibble(
 Modelo = rep(c("Reg. Lineal","XGBoost","Random Forest"), each=3),
 Métrica = rep(c("R²","RMSE ($)","MAE ($)"), 3),
 Valor = c(models$metrics$linear$r2, models$metrics$linear$rmse, models$metrics$linear$mae,
 models$metrics$xgb$r2, models$metrics$xgb$rmse, models$metrics$xgb$mae,
 models$metrics$rf$r2, models$metrics$rf$rmse, models$metrics$rf$mae)
 )
 plot_ly(df_plot, x = ~Modelo, y = ~Valor, color = ~Métrica, type = "bar",
 colors = c("#00D4FF","#E63946","#F4A261"),
 hovertemplate = "<b>%{x}</b><br>%{fullData.name}: %{y:.4f}<extra></extra>") %>%
 ps_layout(barmode = "group",
 xaxis = list(title = ""),
 yaxis = list(title = "Valor"),
 legend = list(orientation="h", y=1.1, font=list(size=10)))
 })
 
 output$model_justification <- renderUI({
 models <- TRAINED_MODELS
 if (is.null(models)) return(tags$div(class="alert alert-warning","Modelos no disponibles."))
 items <- list(
 list(" Precisión superior", sprintf("R² de %.4f vs %.4f de Regresión Lineal.", models$metrics$rf$r2, models$metrics$linear$r2)),
 list(" No-linealidades", "Captura interacciones complejas entre género, plataforma y año."),
 list(" Robustez a outliers", "Los árboles son menos sensibles a valores extremos de precio."),
 list(" Balance sesgo-varianza", "100 árboles en ensamble evitan sobreajuste."),
 list(" Feature importance", "Revela qué variables (género, plataforma, año) influyen más.")
 )
 tagList(
 fluidRow(lapply(items, function(item) {
 column(12,
 tags$div(class = "insight-card",
 tags$span(substr(item[[1]], 1, 2), class = "ic-emoji"),
 tags$div(class = "ic-text",
 tags$strong(sub("^.. ", "", item[[1]]), ": "),
 item[[2]])
 )
 )
 })),
 tags$p(style = "color:#6878A0; font-size:0.88rem; margin-top:8px;",
 "Modelo entrenado con 80% de datos; métricas evaluadas en el 20% de prueba.")
 )
 })
 
 # PREDICTOR 
 observe({
 models <- TRAINED_MODELS
 if (is.null(models)) return()
 genres <- sort(unique(models$prep_data$data$genre_main))
 updateSelectInput(session, "pred_genre", choices = genres, selected = genres[1])
 updateSelectInput(session, "pred_platform", choices = c("PS4","PS5"), selected = "PS5")
 })
 
 
 pred_result <- eventReactive(input$predict_btn, {
 models <- TRAINED_MODELS
 if (is.null(models) || is.null(input$pred_genre) || is.null(input$pred_platform)) return(NULL)
 list(
 genre = input$pred_genre,
 platform = input$pred_platform,
 year = input$pred_year,
 prediction = predict_price(input$pred_genre, input$pred_platform,
 input$pred_year, models, "rf")
 )
 })
 
 output$prediction_result <- renderUI({
 result <- pred_result()
 if (is.null(result)) {
 return(tags$div(style = "text-align:center; padding:48px;",
 tags$div(style = "font-size:3rem; margin-bottom:12px;", ""),
 tags$p(style = "color:#6878A0; font-size:1.0rem;",
 "Configura el juego y pulsa «Predecir precio»")))
 }
 tagList(
 tags$div(class = "pred-result-box",
 tags$div(class = "pred-label", "Precio estimado para"),
 tags$div(style = "color:#C8D8F0; font-size:1rem; font-weight:600; margin:4px 0;",
 paste0(result$genre, " · ", result$platform, " · ", result$year)),
 tags$div(class = "pred-price", sprintf("$%.2f", result$prediction)),
 tags$div(class = "pred-label", "USD — basado en historial de precios PlayStation")
 )
 )
 })
 
 output$sensitivity_plot <- renderPlotly({
 models <- TRAINED_MODELS
 if (is.null(models)) return(plot_ly() %>% layout(title = "Modelos no disponibles"))
 genres <- sort(unique(models$prep_data$data$genre_main))
 plat <- input$pred_platform %||% "PS5"
 yr <- input$pred_year %||% 2024
 preds <- sapply(genres, function(g) predict_price(g, plat, yr, models, "rf"))
 df_s <- tibble(genre = genres, price = preds) %>% arrange(price)
 plot_ly(df_s, x = ~price, y = ~reorder(genre, price), type = "bar", orientation = "h",
 marker = list(color = ~price,
 colorscale = list(c(0,"#003087"), c(0.5,"#7B2FBE"), c(1,"#00D4FF")),
 showscale = FALSE),
 text = ~sprintf("$%.2f", price),
 hovertemplate = "<b>%{y}</b><br>$%{x:.2f}<extra></extra>") %>%
 ps_layout(title = list(text = sprintf("Precios predichos — %s (%d)", plat, yr),
 font = list(color="#C8D8F0", size=13)),
 xaxis = list(title = "Precio predicho (USD)", tickprefix = "$"),
 yaxis = list(title = ""))
 })
 
}

shinyApp(ui = ui, server = server)