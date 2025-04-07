# macro var simulator

this project estimates a vector autoregression (var) model using quarterly u.s. macroeconomic data from the federal reserve economic data (FRED) API. it computes impulse response functions (IRFs) and forecast error variance decompositions (FEVD) to visualize the dynamic relationships between key macroeconomic variables.

## included variables

- real gdp growth (GDPC1)
- inflation (CPIAUCSL)
- federal funds rate (FEDFUNDS)
- real personal consumption growth (PCEC96)
- unemployment rate (UNRATE) [optional]

variables are transformed into quarterly growth rates or averages where applicable, and all data are merged on a common quarterly PeriodIndex.

## functionality

- downloads and processes data directly from FRED
- estimates optimal lag length using akaike information criterion (AIC)
- fits a reduced-form VAR model
- plots orthogonalized IRFs for 12 quarters ahead
- plots FEVD to show contribution of shocks to forecast error variance

## requirements

- python 3.8+
- pandas
- numpy
- matplotlib
- statsmodels
- fredapi


