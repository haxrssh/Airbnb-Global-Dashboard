# Data dictionary

Types are the Power BI types set in Power Query.

## Listings (279,712 rows, 33 columns)

| Column | Type | Description / notes |
|---|---|---|
| `listing_id` | Int64 | Unique listing ID. Primary key (no duplicates). |
| `name` | Text | Listing title. |
| `host_id` | Int64 | Host ID. 182,024 distinct hosts. |
| `host_since` | Date | Date the **host** joined Airbnb. This is not the listing's creation date. 165 blanks. |
| `host_location` | Text | Host's self-reported location, e.g. "Paris, Ile-de-France, France". |
| `host_response_time` | Text | within an hour / within a few hours / within a day / a few days or more / blank. |
| `host_response_rate` | Text | Stored as a decimal fraction in text ("1", "0.9"). Blank for ~46% of listings. |
| `host_acceptance_rate` | Text | Same format as response rate. |
| `host_is_superhost` | Text | `t` / `f` (165 blanks). |
| `host_total_listings_count` | Int64 | Number of listings the host has on Airbnb. |
| `host_has_profile_pic` | Text | `t` / `f`. |
| `host_identity_verified` | Text | `t` / `f`. |
| `neighbourhood` | Text | Neighbourhood name (660 distinct). |
| `district` | Text | Populated **only for New York** (the five boroughs). |
| `city` | Text | One of 10: Paris, New York, Sydney, Rome, Rio de Janeiro, Istanbul, Mexico City, Bangkok, Cape Town, Hong Kong. |
| `latitude`, `longitude` | Decimal | Approximate coordinates. |
| `property_type` | Text | 144 distinct values, e.g. "Entire apartment" or "Private room in house". |
| `room_type` | Text | Entire place (182,005) · Private room (86,988) · Hotel room (5,857) · Shared room (4,862). |
| `accommodates` | Int64 | Guest capacity (up to 16). |
| `bedrooms` | Int64 | ~10.5% blank. |
| `amenities` | Text | JSON-style list, e.g. `["Wifi", "Kitchen", ...]`. |
| `price` | Int64 | Nightly price in **local currency**: EUR for Paris and Rome, USD for New York, AUD for Sydney, THB for Bangkok, ZAR for Cape Town, and so on. Do not average across cities without converting. |
| `minimum_nights`, `maximum_nights` | Int64 | Booking constraints. |
| `review_scores_rating` | Int64 | Overall rating, 20–100. Blank for 32.7% of listings, mostly ones with no reviews. |
| `review_scores_accuracy` | Int64 | Sub-score, 2–10. |
| `review_scores_cleanliness` | Int64 | Sub-score, 2–10. |
| `review_scores_checkin` | Int64 | Sub-score, 2–10. |
| `review_scores_communication` | Int64 | Sub-score, 2–10. |
| `review_scores_location` | Int64 | Sub-score, 2–10. |
| `review_scores_value` | Int64 | Sub-score, 2–10. |
| `instant_bookable` | Text | `t` / `f`. |

## Reviews (5,373,143 rows, 4 columns)

| Column | Type | Description / notes |
|---|---|---|
| `listing_id` | Int64 | Foreign key to `Listings[listing_id]`. Every review matches a listing. 86,156 listings have no reviews. |
| `review_id` | Int64 | Review ID. 5,372,983 distinct, so 160 rows are duplicates. |
| `date` | Date | Review date, 2008-11-16 to 2021-03-01. |
| `reviewer_id` | Int64 | Guest ID. 4,450,005 distinct reviewers. |

## Model

```
Reviews[listing_id]  *  ──►  1  Listings[listing_id]     (cross-filter: both directions)
```

Power BI's *auto date/time* feature is on. It creates hidden local date tables for `Listings[host_since]` and `Reviews[date]`, and these drive the Year axis of the growth chart.
