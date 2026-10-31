# Data

The full dataset is **not committed** because it is too large for Git: about 280k listings and 5.4M reviews, a few hundred MB as CSV.

## Source

**Airbnb Listings & Reviews**, free download from the [Maven Analytics Data Playground](https://mavenanalytics.io/data-playground/airbnb-listings-reviews). The data originally comes from [Inside Airbnb](http://insideairbnb.com/). Check the dataset page for its current license terms before redistributing.

| File | Rows | Grain |
|---|---:|---|
| `Listings.csv` | 279,712 | one row per listing (10 cities, snapshot up to early 2021) |
| `Reviews.csv` | 5,373,143 | one row per guest review (Nov 2008 – Mar 2021) |

## Set-up

1. Download and unzip the dataset.
2. Put both CSVs in `data/raw/`. That folder is git-ignored.
   ```
   data/raw/Listings.csv
   data/raw/Reviews.csv
   ```
3. In Power BI Desktop, open `Airbnb_Dashboard.pbip`. Then go to **Transform data → Edit parameters → DataFolder** and set it to the full path of that folder, **ending with a backslash**. For example: `C:\Projects\airbnb-powerbi-dashboard\data\raw\`
4. Click **Refresh**.

## `sample/`

`sample/` holds a stratified sample: 100 random listings per city (1,000 total) plus all 17,355 of their reviews. It has the same columns and encodings as the originals. Use it to:

- run the Python scripts in `analysis/` without downloading anything, and
- point `DataFolder` at it for a quick, lightweight refresh while editing the report.

Numbers computed on the sample will not match the dashboard.

See [`docs/data-dictionary.md`](../docs/data-dictionary.md) for column definitions.
