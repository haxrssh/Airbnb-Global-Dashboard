"""
Recompute the dashboard's KPIs and narrative claims straight from the CSVs.

Use it to sanity-check the Power BI numbers after a data refresh, or to see
the analysis without opening Power BI.

    python analysis/validate_insights.py                 # uses data/raw if present, else data/sample
    python analysis/validate_insights.py --data data/raw  # explicit folder

The folder must contain Listings.csv and Reviews.csv (Maven Analytics format).
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCORE_COLS = {
    "Accuracy": "review_scores_accuracy",
    "Cleanliness": "review_scores_cleanliness",
    "Check-in": "review_scores_checkin",
    "Communication": "review_scores_communication",
    "Location": "review_scores_location",
    "Value": "review_scores_value",
}


def pick_data_dir(arg: str | None) -> Path:
    if arg:
        return Path(arg)
    raw = ROOT / "data" / "raw"
    if (raw / "Listings.csv").exists():
        return raw
    return ROOT / "data" / "sample"


def load(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    # Encodings match the Power Query source steps (Listings = UTF-8, Reviews = Windows-1252).
    listings = pd.read_csv(
        data_dir / "Listings.csv", encoding="utf-8", parse_dates=["host_since"], low_memory=False
    )
    reviews = pd.read_csv(
        data_dir / "Reviews.csv",
        encoding="cp1252",
        usecols=["listing_id", "review_id", "date", "reviewer_id"],
        parse_dates=["date"],
    )
    return listings, reviews


def pct(x: float) -> str:
    return f"{x:.1%}"


def section(title: str) -> None:
    print(f"\n{title}\n{'-' * len(title)}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", help="folder containing Listings.csv and Reviews.csv")
    data_dir = pick_data_dir(ap.parse_args().data)
    listings, reviews = load(data_dir)
    is_sample = data_dir.name == "sample"

    print(f"Data folder: {data_dir}")
    if is_sample:
        print("NOTE: running on the 1,000-listing sample. Numbers will NOT match the dashboard;")
        print("      download the full dataset into data/raw/ for real figures (see data/README.md).")

    section("KPI cards (Overview page)")
    print(f"Listings        {listings['listing_id'].nunique():>12,}")
    print(f"Cities          {listings['city'].nunique():>12,}")
    print(f"Hosts           {listings['host_id'].nunique():>12,}")
    print(f"Property types  {listings['property_type'].nunique():>12,}")
    print(f"Reviews         {reviews['review_id'].nunique():>12,}  "
          f"({len(reviews) - reviews['review_id'].nunique():,} duplicate review_id rows)")

    section("Listings by host join year (the 'New Listings' chart)")
    by_year = listings["host_since"].dt.year.value_counts().sort_index()
    for year, n in by_year.items():
        print(f"{int(year)}  {n:>8,}")
    print(f"Peak year: {int(by_year.idxmax())}")

    section("Market share by city (Pareto)")
    city_l = listings["city"].value_counts()
    cum = city_l.cumsum() / city_l.sum()
    for city, n in city_l.items():
        print(f"{city:<16}{n:>9,}   cumulative {pct(cum[city])}")
    top3 = list(city_l.index[:3])
    print(f"Top-3 cities by listings ({', '.join(top3)}): {pct(city_l.iloc[:3].sum() / city_l.sum())}")

    rv_city = reviews.merge(listings[["listing_id", "city"]], on="listing_id", how="left")["city"].value_counts()
    print(f"Same three cities' share of reviews: {pct(rv_city.reindex(top3).sum() / rv_city.sum())}")
    print(f"Top-3 cities by reviews ({', '.join(rv_city.index[:3])}): {pct(rv_city.iloc[:3].sum() / rv_city.sum())}")

    section("Price (local currency!)")
    print("Average price by room type, all cities mixed (what the dashboard shows):")
    print(listings.groupby("room_type")["price"].mean().round(0).to_string())
    paris = listings[listings["city"] == "Paris"].groupby("room_type")["price"].median()
    if {"Hotel room", "Entire place"} <= set(paris.index):
        print(f"\nParis median, hotel room vs entire place: {paris['Hotel room']:.0f} vs "
              f"{paris['Entire place']:.0f} EUR ({paris['Hotel room'] / paris['Entire place']:.1f}x)")

    section("Ratings")
    rating = listings.groupby("city")["review_scores_rating"].mean().sort_values(ascending=False)
    print(rating.round(2).to_string())
    print("\nAverage sub-scores (all listings, lowest first):")
    print(listings[list(SCORE_COLS.values())].mean().rename(dict(zip(SCORE_COLS.values(), SCORE_COLS))).sort_values().round(2).to_string())
    unrated = listings["review_scores_rating"].isna().mean()
    print(f"\nListings without a rating: {pct(unrated)}")


if __name__ == "__main__":
    main()
