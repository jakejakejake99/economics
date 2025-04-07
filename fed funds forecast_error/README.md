# README for Forecast Accuracy Experiment Using `error_data.dta`

**Attribution:**  
This project builds on the empirical structure and comparison methodology introduced by:

> **Caballero, R. J., & Simsek, A. (2022).** "Monetary Policy with Opinionated Markets." *American Economic Review*, 112(7), 2353–2392. https://doi.org/10.1257/aer.20210271

We rely on their `.do` files to generate the processed panel `error_data8824_figure1.dta` from proprietary Bloomberg futures data. These original scripts are **not included in this repository** and must be obtained through the AER replication archive or directly from the authors.

Our contribution begins after this data has been constructed. We use their conventions for:
- Structuring quarterly futures-based forecasts (`ffq0`, `ffq1`, ..., `ffq11`)
- Shifting market-based forecasts back by one day to align with the forecast information set
- Comparing Greenbook and market forecasts over consistent horizons

We extend their setup by constructing **forecast accuracy metrics** (mean absolute errors), filtering the panel to ensure consistent forecast coverage, and producing new visualizations that compare forecast accuracy over time.

---

## Input

- `error_data.dta` — a proprietary panel of Fed Funds Futures and forecast data (must be obtained via Bloomberg and processed using Caballero & Simsek’s original Stata code).

### Dataset Description

The processed file `error_data8824_figure1.dta` is structured daily and spans several decades. It includes:

- Realized federal funds rates (`ffr`)
- Daily futures-implied forecasts for up to 36 days ahead (`ff0` to `ff35`)
- Monthly and quarterly average forecasts (`ffy0`–`ffy2`, `ffq0`–`ffq11`)
- Greenbook forecasts at multiple horizons (`ffrFq0`–`ffrFq23`)
- Dots plot projections (`dotsy0`–`dotsy3`)
- Realized values for output and inflation (`pgdpFq0`, `rt3mFq0`, etc.)
- Metadata: `book_date`, `date`, `month`, `quarter`, `year`

Forecast variables target future quarters (e.g., `q1`, `q2`, `q3`) from the perspective of each forecast date.

---

## Methodology

- Compares forecast values (Greenbook vs. market) against the realized federal funds rate for the targeted quarter
- Shifts market-implied forecasts (`ffq1`, `ffq2`, `ffq3`) back one day to align with the forecast timing conventions used in Caballero-Simsek (2022)
- Filters the panel to include only observations where both Greenbook and market forecasts are present
- Computes mean absolute errors (MAE) for each forecast type (Greenbook vs. market) at horizons `q1`, `q2`, and `q3`
- Produces bar graphs of average forecast error **by decade and forecast quarter**, separated by forecast source

---

## Output

- `forecast_accuracy_dataset.dta` — final dataset including:
  - Forecasts (Greenbook, market)
  - Realized outcomes
  - Absolute errors for each forecast
