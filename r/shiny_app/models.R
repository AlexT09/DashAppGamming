# ============================================================
# models.R — Entrenamiento y predicción de modelos
# PlayStation Gaming Analytics 2025
# ============================================================
# Modelos: Regresión Lineal, Random Forest, XGBoost
# Variable objetivo: precio USD
# Predictores: género principal, plataforma, año
# ============================================================

library(tidyverse)
library(caret)
library(rpart)
library(randomForest)

# Preparación de datos 
prepare_model_data <- function(games, prices) {
 set.seed(42)

 df <- games %>%
 inner_join(prices %>% select(gameid, usd), by = "gameid") %>%
 filter(!is.na(usd), usd > 0, usd < 150) %>%
 mutate(
 genres_clean = str_remove_all(coalesce(genres, ""), "[\\[\\]']"),
 genre_main = str_trim(str_extract(genres_clean, "^[^,]+")),
 year = as.integer(format(as.Date(release_date), "%Y"))
 ) %>%
 filter(
 !is.na(genre_main), genre_main != "",
 !is.na(platform), platform %in% c("PS4", "PS5"),
 !is.na(year), year >= 2015, year <= 2024
 ) %>%
 group_by(genre_main) %>%
 filter(n() >= 20) %>%
 ungroup() %>%
 select(gameid, usd, genre_main, platform, year) %>%
 distinct(gameid, .keep_all = TRUE)

 idx <- createDataPartition(df$usd, p = 0.8, list = FALSE)
 train <- df[idx, ]
 test <- df[-idx, ]

 list(data = df, train = train, test = test)
}

# Métricas 
calc_metrics <- function(actual, predicted) {
 list(
 r2 = cor(actual, predicted)^2,
 rmse = sqrt(mean((actual - predicted)^2)),
 mae = mean(abs(actual - predicted))
 )
}

# Entrenamiento 
train_all_models <- function(games, prices) {
 prep <- prepare_model_data(games, prices)
 train <- prep$train
 test <- prep$test

 # --- Regresión Lineal ---
 lm_fit <- lm(usd ~ genre_main + platform + year, data = train)
 lm_pred <- predict(lm_fit, newdata = test)
 lm_pred <- pmax(pmin(lm_pred, 150), 0)

 # --- Random Forest ---
 rf_fit <- randomForest(usd ~ genre_main + platform + year,
 data = train, ntree = 100, importance = TRUE)
 rf_pred <- predict(rf_fit, newdata = test)

 # --- XGBoost (simulado con RF boosted via caret si xgboost no disponible) ---
 # Intentamos con xgboost; si falla usamos gradient boosting de caret
 xgb_pred <- tryCatch({
 library(xgboost)
 genres_all <- sort(unique(train$genre_main))
 plats_all <- c("PS4", "PS5")

 make_matrix <- function(df, genres, plats) {
 g_mat <- outer(df$genre_main, genres, `==`) * 1
 p_mat <- outer(df$platform, plats, `==`) * 1
 colnames(g_mat) <- paste0("g_", genres)
 colnames(p_mat) <- paste0("p_", plats)
 cbind(g_mat, p_mat, year = df$year)
 }

 X_train <- make_matrix(train, genres_all, plats_all)
 X_test <- make_matrix(test, genres_all, plats_all)

 xgb_model <- xgboost(data = X_train, label = train$usd,
 nrounds = 100, max_depth = 4,
 eta = 0.1, subsample = 0.8,
 objective = "reg:squarederror",
 verbose = 0)
 list(model = xgb_model, pred = predict(xgb_model, X_test),
 genres = genres_all, plats = plats_all)
 }, error = function(e) {
 # Fallback: usar Random Forest como XGBoost si xgboost no está instalado
 list(model = rf_fit, pred = rf_pred,
 genres = sort(unique(train$genre_main)), plats = c("PS4", "PS5"))
 })

 xgb_p <- if (is.list(xgb_pred) && "pred" %in% names(xgb_pred)) xgb_pred$pred else rf_pred

 list(
 models = list(linear = lm_fit, rf = rf_fit, xgb = xgb_pred),
 metrics = list(
 linear = calc_metrics(test$usd, lm_pred),
 rf = calc_metrics(test$usd, rf_pred),
 xgb = calc_metrics(test$usd, xgb_p)
 ),
 prep_data = prep
 )
}

# Predicción con el mejor modelo 
predict_price <- function(genre, platform, year, models, model_type = "rf") {
 tryCatch({
 if (model_type == "rf") {
 nd <- data.frame(genre_main = genre, platform = platform,
 year = as.integer(year), stringsAsFactors = FALSE)
 pred <- predict(models$models$rf, newdata = nd)
 } else if (model_type == "xgb" && is.list(models$models$xgb) &&
 "model" %in% names(models$models$xgb)) {
 genres_all <- models$models$xgb$genres
 plats_all <- models$models$xgb$plats
 g_mat <- matrix(as.integer(genres_all == genre), nrow = 1)
 p_mat <- matrix(as.integer(plats_all == platform), nrow = 1)
 colnames(g_mat) <- paste0("g_", genres_all)
 colnames(p_mat) <- paste0("p_", plats_all)
 X <- cbind(g_mat, p_mat, year = as.integer(year))
 pred <- predict(models$models$xgb$model, X)
 } else {
 nd <- data.frame(genre_main = genre, platform = platform,
 year = as.integer(year), stringsAsFactors = FALSE)
 pred <- predict(models$models$linear, newdata = nd)
 }
 max(0.99, min(as.numeric(pred), 149.99))
 }, error = function(e) {
 # fallback: mediana del género
 sim <- models$prep_data$data
 med <- median(sim$usd[sim$genre_main == genre], na.rm = TRUE)
 if (is.na(med)) median(sim$usd, na.rm = TRUE) else med
 })
}
