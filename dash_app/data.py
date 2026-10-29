"""
data.py — Carga de las tablas procesadas por el ETL (data/processed/).

El ETL (etl/etl_playstation.py) ya hizo la limpieza pesada. Aquí solo se leen
los CSV y se dejan funciones de filtro que usan las páginas del dashboard.
"""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

_HERE = Path(__file__).resolve().parent
_CANDIDATES = [Path(os.environ["PS_DATA_DIR"])] if os.environ.get("PS_DATA_DIR") else []
_CANDIDATES += [_HERE / "data" / "processed", _HERE.parent / "data" / "processed"]
DATA = next((p for p in _CANDIDATES if (p / "games_clean.csv").exists()), _CANDIDATES[-1])


def _read(name: str, **kw) -> pd.DataFrame:
    return pd.read_csv(DATA / name, **kw)


games = _read("games_clean.csv", parse_dates=["release_date"])
game_genres = _read("game_genres.csv")
snapshots = _read("prices_snapshots.csv", parse_dates=["date"])
countries = _read("countries.csv")
player_library = _read("player_library.csv")
activity_monthly = _read("activity_monthly.csv")
activity_monthly["month"] = pd.to_datetime(activity_monthly["month"])
activity_heatmap = _read("activity_heatmap.csv")
rarity_summary = _read("rarity_summary.csv")
rarest_trophies = _read("rarest_trophies.csv")
etl_quality = _read("etl_quality.csv")
missing_raw = _read("missing_raw.csv")
fx_rates = _read("fx_rates.csv")
_summary = _read("summary.csv")
S = dict(zip(_summary["key"], _summary["display"]))  # cifras clave ya formateadas (mismas que en Shiny)

PLATFORMS = ["Todas"] + sorted(games["platform"].unique())
GENRES = ["Todos"] + games["genre_main"].value_counts().index.tolist()
YEAR_MIN, YEAR_MAX = int(games["year"].min()), int(games["year"].max())
RARITY_ORDER = ["Bronze", "Silver", "Gold", "Platinum"]
CURRENCIES = ["usd", "eur", "gbp", "jpy", "rub"]


def filter_games(platform: str = "Todas", years=None, genre: str = "Todos") -> pd.DataFrame:
    """Aplica los filtros globales del menú lateral."""
    df = games
    if platform and platform != "Todas":
        df = df[df["platform"] == platform]
    if years:
        df = df[df["year"].between(years[0], years[1])]
    if genre and genre != "Todos":
        df = df[df["genre_main"] == genre]
    return df


def genres_for(df: pd.DataFrame) -> pd.DataFrame:
    """Juegos filtrados expandidos a una fila por género."""
    return game_genres[game_genres["gameid"].isin(df["gameid"])].merge(
        df.drop(columns=["genres"]), on="gameid")
