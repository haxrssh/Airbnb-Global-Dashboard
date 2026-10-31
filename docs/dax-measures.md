# DAX measures

All 22 measures in the model, with where each one is used in the report. The source of truth is
[`Airbnb_Dashboard.SemanticModel/definition/tables/`](../Airbnb_Dashboard.SemanticModel/definition/tables/).

| Measure | Table | Format | Used in | Notes |
|---|---|---|---|---|
| `Entire Place` | Listings | `0` | Overview – growth line chart | Line on the growth chart. |
| `Hotel room` | Listings | `0` | Overview – growth line chart | Line on the growth chart. |
| `Private Room` | Listings | `0` | Overview – growth line chart | Line on the growth chart. |
| `Shared room` | Listings | `0` | Overview – growth line chart | Line on the growth chart. |
| `Total Listings` | Listings | `0` | via [City Rank], [Cumulative Listings], [Cumulative %], [Listings per host] | Base measure for the Pareto logic. (The KPI card uses an implicit count of `listing_id` instead.) |
| `Superhost Listings` | Listings | `0` | Ratings – Pareto combo chart | Stacked column in the Pareto chart. |
| `No Superhost Listings` | Listings | `0` | Ratings – Pareto combo chart | Stacked column in the Pareto chart. Listings with a blank superhost flag (165) fall in neither series. |
| `City Rank` | Listings | `0` | via [Cumulative Listings] | Ranks cities by listing count; helper for the Pareto. |
| `Cumulative Listings` | Listings | `0` | via [Cumulative %] | Running total of listings over cities ranked ≤ the current one. |
| `Cumulative %` | Listings | `0.0%;-0.0%;0.0%` | Ratings – Pareto combo chart | Pareto line: cumulative share of all listings. |
| `Avg Price` | Listings | `\$#,0;(\$#,0);\$#,0` | Ratings – price bar chart | ⚠️ Averages prices in different local currencies. Only meaningful within a single city. |
| `Avg Rating` | Listings | `0.0` | Ratings – rating column chart | Overall rating, 20–100 scale. Blanks are ignored. |
| `Accuracy` | Listings | `General` | Ratings – sub-score matrix | Sub-score, 2–10. |
| `Cleanliness` | Listings | `General` | Ratings – sub-score matrix | Sub-score, 2–10. |
| `location` | Listings | `General` | Ratings – sub-score matrix | Sub-score, 2–10. (Lower-case name.) |
| `Value` | Listings | `General` | Ratings – sub-score matrix | Sub-score, 2–10. |
| `Reviewers` | Reviews | `0` | — | Distinct guests who left a review. Currently unused. |
| `Reviews per reviewer` | Reviews | `0` | — | Review count per reviewer; only meaningful with `reviewer_id` on rows. Currently unused. |
| `Total Revivewers` | Listings | `0` | — | Typo in the name. Uses COUNT, so it counts reviews, not distinct reviewers. Currently unused. |
| `Total Hosts` | Listings | `0` | — | Distinct hosts. Currently unused; the KPI card uses an implicit distinct count. |
| `Listings per host` | Listings | `0.00` | — | Average listings per host (≈1.54). Currently unused. |
| `Top 3 City Listings Share %` | Listings | `General` | — | Share of listings held by the top 3 cities (48.4%). Respects slicers via ALLSELECTED. Currently unused; good candidate for a KPI card. |

## Definitions

### Entire Place

```dax
Entire Place =
CALCULATE (
    COUNT ( Listings[listing_id] ),
     Listings[room_type] = "Entire place"
)
```

### Hotel room

```dax
Hotel room =
CALCULATE (
    COUNT ( Listings[listing_id] ),
     Listings[room_type] = "Hotel room"
)
```

### Private Room

```dax
Private Room =
CALCULATE (
    COUNT ( Listings[listing_id] ),
     Listings[room_type] = "Private room"
)
```

### Shared room

```dax
Shared room =
CALCULATE (
    COUNT ( Listings[listing_id] ),
     Listings[room_type] = "Shared room"
)
```

### Total Listings

```dax
Total Listings =
DISTINCTCOUNT(Listings[listing_id])
```

### Superhost Listings

```dax
Superhost Listings =
CALCULATE(
    COUNT(Listings[listing_id]),
    Listings[host_is_superhost] = "t"
)
```

### No Superhost Listings

```dax
No Superhost Listings =
CALCULATE(
    COUNT(Listings[listing_id]),
    Listings[host_is_superhost] = "f"
)
```

### City Rank

```dax
City Rank =
RANKX (
    ALL (Listings[city] ),
    [Total Listings],
    ,DESC
)
```

### Cumulative Listings

```dax
Cumulative Listings =
VAR CurrentRank =
MAXX ( 
    VALUES(Listings[city]),
    [City Rank]

)
RETURN
CALCULATE (
    [Total Listings],
    FILTER(
        ALL(Listings[city]),
        [City Rank] <= CurrentRank
    )
)
```

### Cumulative %

```dax
Cumulative % =
DIVIDE( [Cumulative Listings], CALCULATE([Total Listings], ALL(Listings[city]))
)
```

### Avg Price

```dax
Avg Price =
AVERAGE(Listings[price])
```

### Avg Rating

```dax
Avg Rating =
AVERAGE( Listings[review_scores_rating] )
```

### Accuracy

```dax
Accuracy =
AVERAGE( Listings[review_scores_accuracy] )
```

### Cleanliness

```dax
Cleanliness =
AVERAGE(Listings[review_scores_cleanliness] )
```

### location

```dax
location =
AVERAGE( Listings[review_scores_location] )
```

### Value

```dax
Value =
AVERAGE(Listings[review_scores_value] )
```

### Reviewers

```dax
Reviewers =
DISTINCTCOUNT( Reviews[reviewer_id] )
```

### Reviews per reviewer

```dax
Reviews per reviewer =
CALCULATE(
    COUNT(Reviews[reviewer_id]),
    ALLEXCEPT( Reviews, Reviews[reviewer_id] )
)
```

### Total Revivewers

```dax
Total Revivewers =
COUNT(Reviews[reviewer_id])
```

### Total Hosts

```dax
Total Hosts =
DISTINCTCOUNT(Listings[host_id])
```

### Listings per host

```dax
Listings per host =
DIVIDE([Total Listings], [Total Hosts])
```

### Top 3 City Listings Share %

```dax
Top 3 City Listings Share % =
VAR CityTable =
    ADDCOLUMNS(
        ALLSELECTED(Listings[city]),
        "@Listings", CALCULATE([Total Listings])
    )
VAR TopCities =
    TOPN(
        3,
        CityTable,
        [@Listings], DESC,
        Listings[city], ASC
    )
VAR Top3Listings =
    SUMX(TopCities, [@Listings])
VAR AllCityListings =
    CALCULATE(
        [Total Listings],
        ALLSELECTED(Listings[city])
    )
RETURN
    DIVIDE(Top3Listings, AllCityListings)
```

## How the Pareto works

1. `[City Rank]` ranks each city by `[Total Listings]` using `RANKX(ALL(Listings[city]), …)`.
2. `[Cumulative Listings]` takes the current city's rank and sums `[Total Listings]` over every city with a rank less than or equal to it.
3. `[Cumulative %]` divides that by the grand total (`ALL(Listings[city])`).

Plotted on a secondary axis over columns sorted descending, this gives the Pareto line. Paris + New York + Sydney reach **48.4%**.

## Implicit measures used by the KPI cards

The five Overview cards use aggregations dragged straight from columns, not explicit measures:

| Card | Field | Aggregation |
|---|---|---|
| Listings | `Listings[listing_id]` | Count |
| Cities | `Listings[city]` | Count (Distinct) |
| Hosts | `Listings[host_id]` | Count (Distinct) |
| Property Types | `Listings[property_type]` | Count (Distinct) |
| Reviews | `Reviews[review_id]` | Count (Distinct) |

The internal query references read `Sum(...)` / `Min(...)` because the aggregation was changed after the field was added. The displayed values are correct.
