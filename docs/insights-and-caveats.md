# Insights, verification and caveats

Every number below was recomputed from the raw CSVs with
[`analysis/validate_insights.py`](../analysis/validate_insights.py) and cross-checked against the dashboard.

## Insights

| # | Claim on the dashboard | Verified result | Status |
|---|---|---|---|
| 1 | 2015 had the most new listings | 44,886 listings belong to hosts who joined in 2015, the peak year | ✅ (see caveat A) |
| 2 | Paris, NYC and Sydney hold almost half of all listings | 64,690 + 37,012 + 33,630 = **48.4%** | ✅ |
| 3 | …and 48% of reviews | **47.3%** of reviews | ≈ (rounding) |
| 4 | Paris has the most listings and reviews | 64,690 listings (23.1%) and 1.21M reviews (22.6%) | ✅ |
| 5 | Paris hotel rooms cost about twice as much as an Airbnb | Paris median: hotel room €158 vs entire place €82 (**1.9×**) | ✅ within Paris (see caveat B) |
| 6 | Mexico City and Rio are the best rated | 94.8 and 94.6 out of 100 | ✅ |
| 7 | Hong Kong and Istanbul are the worst rated | 89.7 and 91.1 | ✅ |
| 8 | Cleanliness and value score lowest | 9.31 and 9.34, the lowest of the 6 sub-scores | ✅ |

**Extra findings worth surfacing**

- Ranked by **reviews** instead of listings, the top 3 are Paris, **Rome** and New York, with 59.1% of all reviews. Rome has fewer listings than Sydney but more than twice as many reviews, which suggests much higher booking turnover per listing.
- 18% of listings belong to superhosts. The share is highest in Mexico City (32%) and Rome (26%) and lowest in Paris and Sydney (12–13%).
- Hosts with several listings are common: 279,712 listings across 182,024 hosts is about 1.54 listings per host.
- 86,156 listings (31%) have no reviews at all, which is why 32.7% of listings have a blank rating.

## Caveats

**A. "New listings" is really "host join year".** The growth chart groups listings by `host_since`, the date the *host* joined Airbnb. The dataset is a 2021 snapshot of listings that were *still active*, so:

- older years are undercounted, because listings removed before 2021 aren't in the data (survivorship bias);
- 2021 looks like a collapse only because the snapshot ends in early 2021.

A fairer proxy for activity over time is the review count per year from `Reviews[date]`. It shows steady growth to 1.63M reviews in 2019, then a 54% drop in 2020 (COVID-19).

**B. Prices are in local currency.** `price` is in EUR, USD, AUD, THB, ZAR, MXN, BRL, TRY or HKD depending on the city. Averaging across cities, as the *Avg Price by room type* chart does, mixes currencies. Bangkok and Cape Town prices are large numbers that inflate the average. To fix this, either:

- add a currency-conversion table (city → rate to USD) and an `Avg Price (USD)` measure, or
- add a city slicer or filter to the chart.

**C. Duplicates and blanks.**

- 160 duplicate `review_id` rows. The KPI uses a distinct count, so it is unaffected.
- 165 listings have no host data (`host_since` and `host_is_superhost` blank).
- `district` is only populated for New York.

## Model and report housekeeping (roadmap)

- [ ] Add USD price conversion, or a city filter on the price chart (caveat B).
- [ ] Relabel the growth chart "Listings by host join year", or switch it to reviews per year (caveat A).
- [ ] Rename `Total Revivewers` → `Total Reviews` (it uses COUNT) and add a true distinct-reviewer KPI with `[Reviewers]`.
- [ ] Replace implicit KPI aggregations with explicit measures (`[Total Listings]`, `[Total Hosts]`, …).
- [ ] Add a proper `Date` table and turn off *auto date/time* to remove the hidden local date tables.
- [ ] Change the Reviews → Listings relationship from **both** directions to **single** unless bidirectional filtering is required.
- [ ] Remove or wire up the two orphaned bookmarks ("Overall", "Detailed"). They target visuals that no longer exist.
- [ ] Use `[Top 3 City Listings Share %]` in a KPI card so the 48% insight updates dynamically.
- [ ] Add a city slicer and a map page using `latitude` and `longitude`.
