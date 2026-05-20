"""
data.py — Carga y preparación de datos (ETL).

Técnicas del curso incorporadas:
- Detección de outliers (IQR) — módulo 3
- Estadísticas robustas (mediana, cuartiles)
- Validación y limpieza de datos
- Agregados listos para visualización

Autor: Ciencia de Datos — PS Gaming Analytics 2025
"""

from __future__ import annotations

import os
import numpy as np
import pandas as pd

# Busca datos en ./data/ o ../data/ o ../../data/ para compatibilidad de rutas
_THIS = os.path.dirname(os.path.abspath(__file__))
for _candidate in [
 os.path.join(_THIS, "data"),
 os.path.join(_THIS, "..", "data"),
 os.path.join(_THIS, "..", "..", "data"),
]:
 if os.path.isdir(_candidate):
 DATA = _candidate
 break
else:
 DATA = os.path.join(_THIS, "data")


def _detect_outliers_iqr(series: pd.Series) -> tuple:
 """
 Detección de outliers usando IQR (Rango Intercuartil).
 Q1 - 1.5×IQR ≤ valor ≤ Q3 + 1.5×IQR → Normal
 Fuera de ese rango → Outlier
 """
 q1, q3 = series.quantile([0.25, 0.75])
 iqr = q3 - q1
 lower = q1 - 1.5 * iqr
 upper = q3 + 1.5 * iqr
 mask = (series >= lower) & (series <= upper)
 return series[mask], ~mask


def load():
 g = pd.read_csv(f"{DATA}/games.csv", low_memory=False)
 pl = pd.read_csv(f"{DATA}/players.csv", low_memory=False)
 pr = pd.read_csv(f"{DATA}/prices.csv", low_memory=False)

 for df in (g, pl, pr):
 df.columns = df.columns.str.lower().str.strip()

 g["release_date"] = pd.to_datetime(g["release_date"], errors="coerce")
 g["year"] = g["release_date"].dt.year
 g["genres_clean"] = g["genres"].fillna("").str.replace(r"[\[\]']", "", regex=True)
 g["pub_clean"] = g["publishers"].fillna("").str.replace(r"[\[\]']", "", regex=True)
 g["dev_clean"] = g.get("developers", pd.Series([""] * len(g))).fillna("").str.replace(
 r"[\[\]']", "", regex=True
 )
 g = g.drop_duplicates()

 pl = pl.dropna(subset=["country"]).drop_duplicates()
 pl["country"] = pl["country"].str.strip()

 pr = pr[(pr["usd"].notna()) & (pr["usd"] > 0) & (pr["usd"] < 150)]
 pr["date_acquired"] = pd.to_datetime(pr["date_acquired"], errors="coerce")
 pr = pr.drop_duplicates()

 g_exp = g[g["genres_clean"] != ""].copy()
 g_exp = g_exp.assign(genre=g_exp["genres_clean"].str.split(",")).explode("genre")
 g_exp["genre"] = g_exp["genre"].str.strip()
 g_exp = g_exp[g_exp["genre"] != ""]

 gp = g.merge(pr[["gameid", "usd"]], on="gameid", how="inner")
 gp_exp = gp.assign(genre=gp["genres_clean"].str.split(",")).explode("genre")
 gp_exp["genre"] = gp_exp["genre"].str.strip()
 gp_exp = gp_exp[gp_exp["genre"] != ""]

 precio_gen = (
 gp_exp.groupby("genre")["usd"]
 .agg(precio_mediana="median", precio_media="mean", precio_sd="std", n="count")
 .reset_index()
 .query("n >= 15")
 .sort_values("precio_mediana", ascending=False)
 )

 gp_plat = (
 gp_exp[gp_exp["platform"].isin(["PS4", "PS5"])]
 .groupby(["genre", "platform"])["usd"]
 .agg(mediana="median", n="count")
 .reset_index()
 .query("n >= 10")
 )

 return g, pl, pr, g_exp, precio_gen, gp_plat, gp_exp


def missingness_summary() -> pd.DataFrame:
 """Porcentaje de NA por columna (datos crudos)."""
 parts = []
 for label, fname in (
 ("games", "games.csv"),
 ("players", "players.csv"),
 ("prices", "prices.csv"),
 ):
 raw = pd.read_csv(os.path.join(DATA, fname), low_memory=False)
 raw.columns = raw.columns.str.lower().str.strip()
 pct = (raw.isna().mean() * 100).round(2).rename("missing_pct").reset_index()
 pct.columns = ["column", "missing_pct"]
 pct["dataset"] = label
 pct = pct.sort_values("missing_pct", ascending=False).head(12)
 parts.append(pct)
 return pd.concat(parts, ignore_index=True)


games, players, prices, genres_exp, precio_genero, precio_gen_plat, genres_prices = load()
MISSINGNESS_DF = missingness_summary()

N_GAMES = len(games)
N_PLAYERS = len(players)
N_COUNTRIES = players["country"].nunique()
MED_PRICE = prices["usd"].median()

PLATFORMS = ["Todas"] + sorted(games["platform"].dropna().unique().tolist())
YEARS = sorted(games["year"].dropna().unique().astype(int).tolist())
GENRES_LIST = sorted(genres_exp["genre"].dropna().unique().tolist())


def filter_games(plat, years):
 df = games.copy()
 if plat != "Todas":
 df = df[df["platform"] == plat]
 df = df[(df["year"] >= years[0]) & (df["year"] <= years[1])]
 return df


def precio_genero_for_subset(games_subset: pd.DataFrame) -> pd.DataFrame:
 gp = games_subset.merge(prices[["gameid", "usd"]], on="gameid", how="inner")
 gp_exp = gp.assign(genre=gp["genres_clean"].str.split(",")).explode("genre")
 gp_exp["genre"] = gp_exp["genre"].str.strip()
 gp_exp = gp_exp[gp_exp["genre"] != ""]
 return (
 gp_exp.groupby("genre")["usd"]
 .agg(precio_mediana="median", precio_media="mean", precio_sd="std", n="count")
 .reset_index()
 .query("n >= 15")
 .sort_values("precio_mediana", ascending=False)
 )


def precio_gen_plat_for_subset(games_subset: pd.DataFrame) -> pd.DataFrame:
 gp = games_subset.merge(prices[["gameid", "usd"]], on="gameid", how="inner")
 gp_exp = gp.assign(genre=gp["genres_clean"].str.split(",")).explode("genre")
 gp_exp["genre"] = gp_exp["genre"].str.strip()
 gp_exp = gp_exp[gp_exp["genre"] != ""]
 return (
 gp_exp[gp_exp["platform"].isin(["PS4", "PS5"])]
 .groupby(["genre", "platform"])["usd"]
 .agg(mediana="median", n="count")
 .reset_index()
 .query("n >= 10")
 )


def price_dispersion_for_subset(games_subset: pd.DataFrame) -> pd.DataFrame:
 gp = games_subset.merge(prices[["gameid", "usd"]], on="gameid", how="inner")
 gp_exp = gp.assign(genre=gp["genres_clean"].str.split(",")).explode("genre")
 gp_exp["genre"] = gp_exp["genre"].str.strip()
 gp_exp = gp_exp[gp_exp["genre"] != ""]
 return (
 gp_exp.groupby("genre")
 .agg(n=("gameid", "count"), mediana=("usd", "median"), media=("usd", "mean"), std=("usd", "std"))
 .reset_index()
 .sort_values("std", ascending=False)
 )


def price_daily_for_games(game_ids):
 pr = prices[prices["gameid"].isin(game_ids)].copy()
 pr = pr[pr["date_acquired"].notna()]
 if pr.empty:
 return pr
 daily = pr.groupby("date_acquired", as_index=False)["usd"].mean().sort_values("date_acquired")
 daily["roll14"] = daily["usd"].rolling(14, min_periods=1).mean()
 return daily


def pricing_benchmark(genre: str, platform: str) -> dict:
 sub = genres_prices[genres_prices["genre"] == genre]
 if platform != "Todas":
 sub = sub[sub["platform"] == platform]
 out: dict = {"genre": genre, "platform": platform}
 if len(sub) < 10:
 out["error"] = "Menos de 10 observaciones en este segmento. Prueba otra plataforma."
 out["n"] = len(sub)
 return out
 out["q1"] = float(sub["usd"].quantile(0.25))
 out["median"] = float(sub["usd"].median())
 out["q3"] = float(sub["usd"].quantile(0.75))
 out["n"] = len(sub)
 return out


def format_benchmark_md(d: dict) -> str:
 if "error" in d:
 return f"**No disponible.** {d['error']} (n={d.get('n', 0)})"
 return (
 f"**Mediana:** ${d['median']:.2f} USD \n"
 f"**Rango típico (Q1–Q3):** ${d['q1']:.2f} – ${d['q3']:.2f} \n"
 f"**Títulos en segmento:** {d['n']:,} \n\n"
 f"*Valores descriptivos del catálogo (feb. 2025); no incluye ventas ni demanda.*"
 )
