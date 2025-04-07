*******************************************************  
* forecast accuracy evaluation over 3 quarters
* compares forward (futures implied) ffr forecasts to realized ffr
*******************************************************

* load dataset
clear
use "error_data.dta", clear
tsset date, daily

* Safe calendar transformations — only if not already defined
capture confirm variable mdate
if _rc {
    gen mdate = mofd(date)
}

capture confirm variable quarter
if _rc {
    gen quarter = qofd(date)
}

* ========== MONTHLY HORIZONS ==========
local month_forecasts "ff3 ff6 ff12"

foreach var of local month_forecasts {
    local h = substr("`var'", 3, .)  // extract horizon, e.g., 3, 6, 12

    gen mdate_h`h' = mdate + `h'
    gen target_date_`var' = dofm(mdate_h`h')
    format target_date_`var' %td

    * Save realized ffr for target date
    preserve
    keep date ffr
    rename date target_date_`var'
    rename ffr ffr_realized_`var'
    tempfile realized_`var'
    save `realized_`var''
    restore

    * Merge realized ffr
    merge m:1 target_date_`var' using `realized_`var'', keep(match master) nogen

    * Compute forecast errors
    gen forecast_error_`var' = `var' - ffr_realized_`var'
    gen abs_error_`var' = abs(forecast_error_`var')
}

* ========== QUARTERLY HORIZONS (MARKET-IMPLIED) ==========
local quarter_forecasts "ffq1 ffq2 ffq3"

foreach var of local quarter_forecasts {
    local q = substr("`var'", 4, .)  // extract quarter horizon

    gen quarter_h`q' = quarter + `q'
    gen target_date_`var' = dofq(quarter_h`q')
    format target_date_`var' %td

    * Save realized ffr for target date
    preserve
    keep date ffr
    rename date target_date_`var'
    rename ffr ffr_realized_`var'
    tempfile realized_`var'
    save `realized_`var''
    restore

    * Merge realized ffr
    merge m:1 target_date_`var' using `realized_`var'', keep(match master) nogen

    * Compute forecast errors
    gen forecast_error_`var' = `var' - ffr_realized_`var'
    gen abs_error_`var' = abs(forecast_error_`var')
}

* ========== GREENBOOK FORECAST ACCURACY (1Q to 3Q ahead) ==========

* FIRST ensure proper sorting
sort date
tsset date, daily  // Re-establish time series after sorting

* Create lagged futures variables (THE ACTUAL FIX)
foreach q of numlist 1/3 {
    gen ffq`q'_lag = L1.ffq`q'  // Corrected syntax: L1. instead of L.
}

foreach q of numlist 1/3 {
    * Define variables
    local mkt_var = "ffq`q'_lag"    // Using properly lagged futures
    local gbk_var = "ffrFq`q'"      // Greenbook forecast

    * Error vs realized ffr
    gen gbk_forecast_error_q`q' = `gbk_var' - ffr_realized_ffq`q'
    gen gbk_abs_error_q`q' = abs(gbk_forecast_error_q`q')

    * Comparison to LAGGED market forecast
    gen gbk_vs_mkt_q`q' = `gbk_var' - `mkt_var'
    gen abs_diff_gbk_vs_mkt_q`q' = abs(gbk_vs_mkt_q`q')
}

* ========== Apples-to-Apples MAE Comparison Block ==========
gen is_greenbook = !missing(ffrFq1)

* ========== Optional: Trim the dataset for analysis ==========
keep date ffq1 ffq2 ffq3 ffq1_lag ffq2_lag ffq3_lag ///  // Added lagged vars <<<
     abs_error_ffq1 abs_error_ffq2 abs_error_ffq3 ///
     gbk_abs_error_q1 gbk_abs_error_q2 gbk_abs_error_q3 is_greenbook ///
     
drop if is_greenbook != 1
egen rowmiss = rowmiss(*)
drop if rowmiss > 0
drop rowmiss

display "=== Greenbook vs Market MAE Comparison on Greenbook Days ==="
foreach q of numlist 1/3 {
    display "----- Quarter `q' -----"
    quietly sum abs_error_ffq`q' if is_greenbook
    display "Market MAE (contemporaneous): " r(mean)
    quietly sum gbk_abs_error_q`q'
    display "Greenbook MAE: " r(mean)
    
}

* Save final analysis dataset
save "forecast_accuracy_dataset.dta", replace
