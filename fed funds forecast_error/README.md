# readme for forecast accuracy experiment using error_data8824_figure1.dta

**input:**  
- `error_data8824_figure1.dta` (proprietary fed funds futures data must obtain from bloomberg)

**dataset description:**  
the file `error_data8824_figure1.dta` is a proprietary panel of fed funds futures and forecast data used to evaluate the accuracy of monetary policy expectations. it includes:

- realized fed funds rates (`ffr`)  
- daily futures-based forecasts for up to 36 days ahead (`ff0` to `ff35`)  
- monthly and quarterly average futures forecasts (`ffy0`–`ffy2`, `ffq0`–`ffq11`)  
- greenbook (fomc staff) forecasts of the fed funds rate at multiple horizons (`ffrFq0`–`ffrFq23`)  
- realized outcomes (e.g. `ffrFq0`, `pgdpFq0`, `rt3mFq0`)  
- dots plot forecasts (`dotsy0`–`dotsy3`)  
- publication timing via `book_date`  
- temporal metadata including `date`, `month`, `quarter`, and `year`  

the panel is structured daily and spans several decades, enabling comparisons of greenbook vs. market expectations across time. all forecast variables target future quarters (`q1`, `q2`, `q3`, etc.) from the perspective of the forecast date.

**description:**    
- forecasts are compared to the realized fed funds rate on the specific future date the forecast was targeting  
- market-implied forecasts (`ffq1`, `ffq2`, `ffq3`) are shifted back one day (like in Caballero-Simsek 2022)  
- keeps only rows where both greenbook and market forecasts are available to ensure apples-to-apples comparison and avoid  
  bias from the more frequent market data  
- computes mean absolute errors (mae) for each forecast type (Greenbook vs. market) over q1, q2, and q3  
- includes bar graphs of average forecast error **by decade and quarter**, split by forecast type  

**output:**  
- `forecast_accuracy_dataset.dta` (final dataset containing lagged forecasts, realized target values, and absolute error metrics)
