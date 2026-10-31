"""
Regenerate the README figures in docs/images/ from the CSVs.

    python analysis/make_charts.py --data data/raw
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from validate_insights import ROOT, SCORE_COLS, load, pick_data_dir

CORAL, DARK, GREY, LIGHT = "#FE585D", "#484848", "#767676", "#E6E6E6"
ROOM_COLORS = {"Entire place": CORAL, "Private room": DARK, "Hotel room": "#00A699", "Shared room": "#FFB400"}
OUT = ROOT / "docs" / "images"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": GREY, "axes.labelcolor": DARK, "xtick.color": DARK, "ytick.color": DARK,
    "axes.titleweight": "bold", "axes.titlesize": 13, "axes.titlelocation": "left",
})


def save(fig, name: str) -> None:
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=160, facecolor="white")
    plt.close(fig)
    print("wrote", OUT / name)


def growth(listings: pd.DataFrame) -> None:
    df = listings.dropna(subset=["host_since"]).copy()
    df["year"] = df["host_since"].dt.year.astype(int)
    df = df[df["year"] <= 2020]  # 2021 is a partial year (data snapshot ends early 2021)
    pivot = df.pivot_table(index="year", columns="room_type", values="listing_id", aggfunc="count").fillna(0)
    total = pivot.sum(axis=1)
    fig, ax = plt.subplots(figsize=(10, 4.6))
    ax.fill_between(total.index, total.values, color=LIGHT, label="Total")
    for room in ["Entire place", "Private room", "Hotel room", "Shared room"]:
        if room in pivot:
            ax.plot(pivot.index, pivot[room], color=ROOM_COLORS[room], lw=2.2, label=room)
    peak = total.idxmax()
    ax.annotate(f"Peak {peak}: {int(total[peak]):,}", xy=(peak, total[peak]), xytext=(peak + 0.7, total[peak] * 1.04),
                arrowprops=dict(arrowstyle="-", color=GREY), color=DARK)
    ax.axvspan(2019.5, 2020.5, color=CORAL, alpha=0.08)
    ax.text(2019.55, total.max() * 0.80, "COVID-19", color=CORAL, fontsize=9)
    ax.set_ylim(0, total.max() * 1.25)
    ax.set_title("Listings by host join year, split by room type")
    ax.set_ylabel("Listings")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v / 1000:.0f}k"))
    ax.legend(frameon=False, ncol=5, loc="upper left", fontsize=9)
    save(fig, "listings-growth.png")


def pareto(listings: pd.DataFrame) -> None:
    sup = listings.pivot_table(index="city", columns="host_is_superhost", values="listing_id", aggfunc="count").fillna(0)
    sup["total"] = sup.sum(axis=1)
    sup = sup.sort_values("total", ascending=False)
    cum = sup["total"].cumsum() / sup["total"].sum()
    fig, ax = plt.subplots(figsize=(10, 4.6))
    x = range(len(sup))
    ax.bar(x, sup.get("t", 0), color=CORAL, label="Superhost")
    ax.bar(x, sup.get("f", 0), bottom=sup.get("t", 0), color=DARK, label="Not superhost")
    ax.set_xticks(list(x), sup.index, rotation=30, ha="right")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v / 1000:.0f}k"))
    ax2 = ax.twinx()
    ax2.plot(list(x), cum.values, color="#00A699", marker="o", lw=2)
    ax2.set_ylim(0, 1.05)
    ax2.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax2.spines["top"].set_visible(False)
    ax2.annotate(f"Top 3 = {cum.iloc[2]:.1%}", xy=(2, cum.iloc[2]), xytext=(1.2, cum.iloc[2] + 0.22),
                 arrowprops=dict(arrowstyle="-", color=GREY), color=DARK, fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=LIGHT))
    ax.set_title("Market share by city (Pareto)")
    ax.legend(frameon=False, loc="center right")
    save(fig, "city-pareto.png")


def ratings(listings: pd.DataFrame) -> None:
    r = listings.groupby("city")["review_scores_rating"].mean().sort_values()
    fig, ax = plt.subplots(figsize=(10, 4.6))
    colors = [CORAL if v >= r.iloc[-2] else (DARK if v <= r.iloc[1] else LIGHT) for v in r.values]
    ax.barh(r.index, r.values, color=colors)
    for i, v in enumerate(r.values):
        ax.text(v + 0.05, i, f"{v:.1f}", va="center", fontsize=9, color=DARK)
    ax.set_xlim(r.min() - 2, 100)
    ax.set_title("Average guest rating by city (out of 100)")
    save(fig, "ratings-by-city.png")


def subscores(listings: pd.DataFrame) -> None:
    s = listings.groupby("city")[list(SCORE_COLS.values())].mean().rename(columns=dict(zip(SCORE_COLS.values(), SCORE_COLS)))
    s = s.loc[listings.groupby("city")["review_scores_rating"].mean().sort_values(ascending=False).index]
    fig, ax = plt.subplots(figsize=(10, 4.8))
    im = ax.imshow(s.values, cmap="RdYlGn", vmin=8.9, vmax=9.9, aspect="auto")
    ax.set_xticks(range(s.shape[1]), s.columns)
    ax.set_yticks(range(s.shape[0]), s.index)
    for i in range(s.shape[0]):
        for j in range(s.shape[1]):
            ax.text(j, i, f"{s.values[i, j]:.2f}", ha="center", va="center", fontsize=8.5, color="#222")
    ax.spines[:].set_visible(False)
    ax.set_title("Rating sub-scores by city (out of 10)")
    fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    save(fig, "subscores-heatmap.png")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data")
    listings, _ = load(pick_data_dir(ap.parse_args().data))
    OUT.mkdir(parents=True, exist_ok=True)
    growth(listings)
    pareto(listings)
    ratings(listings)
    subscores(listings)


if __name__ == "__main__":
    main()
