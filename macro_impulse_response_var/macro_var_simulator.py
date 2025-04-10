import matplotlib
matplotlib.use('TkAgg')  # set the backend for matplotlib to work on PyCharm
import matplotlib.pyplot as plt

from fredapi import Fred
import pandas as pd
import numpy as np
from statsmodels.tsa.api import VAR

# -----------------------------------------
# 1. download data from FRED
# -----------------------------------------

# initialize the FRED client with your API key
fred = Fred(api_key='1c4f5ab7a59343d596f9567d245840dc')

# download real gdp (GDPC1): quarterly data
gdp = fred.get_series('GDPC1')
gdp = gdp.to_frame(name='gdp')
gdp.index = pd.to_datetime(gdp.index)
gdp.index = gdp.index.to_period('Q')

# download cpi (CPIAUCSL): monthly data
cpi = fred.get_series('CPIAUCSL')
cpi = cpi.to_frame(name='cpi')
cpi.index = pd.to_datetime(cpi.index)

# download ffr (FEDFUNDS): monthly data
ffr = fred.get_series('FEDFUNDS')
ffr = ffr.to_frame(name='ffr')
ffr.index = pd.to_datetime(ffr.index)

# download real personal consumption expenditures (PCEC96): quarterly data
cons = fred.get_series('PCEC96')
cons = cons.to_frame(name='consumption')
cons.index = pd.to_datetime(cons.index)
cons.index = cons.index.to_period('Q')

# -----------------------------------------
# 2. transform data
# -----------------------------------------

# compute gdp growth: annualized quarterly growth (using log differences)
gdp['gdp_growth'] = 400 * np.log(gdp['gdp'] / gdp['gdp'].shift(1))

# resample cpi from monthly to quarterly using quarter-end frequency ('QE-DEC')
cpi_q = cpi.resample('QE-DEC').mean()
cpi_q['inflation'] = 400 * np.log(cpi_q['cpi'] / cpi_q['cpi'].shift(1))
cpi_q.index = cpi_q.index.to_period('Q')

# resample ffr from monthly to quarterly using quarter-end frequency ('QE-DEC')
ffr_q = ffr.resample('QE-DEC').mean()
ffr_q.rename(columns={'ffr': 'interest_rate'}, inplace=True)
ffr_q.index = ffr_q.index.to_period('Q')

# compute consumption growth
cons['cons_growth'] = 400 * np.log(cons['consumption'] / cons['consumption'].shift(1))
cons_q = cons[['cons_growth']].dropna()

# -----------------------------------------
# 3. merge the data
# -----------------------------------------

gdp_q = gdp[['gdp_growth']].dropna()
cpi_q = cpi_q[['inflation']].dropna()
ffr_q = ffr_q[['interest_rate']].dropna()

df = gdp_q.join(cpi_q, how='inner').join(ffr_q, how='inner').join(cons_q, how='inner')

print("\nFinal merged dataset:")
print(df.head())
print("\nMerged date range:", df.index.min(), "to", df.index.max())

# -----------------------------------------
# 4. estimate the VAR model
# -----------------------------------------

model = VAR(df)

lag_selection = model.select_order(maxlags=8)
print("\nLag order selection criteria:")
print(lag_selection.summary())

optimal_lag = lag_selection.aic
results = model.fit(optimal_lag)

print("\nVAR Model Summary:")
print(results.summary())

# -----------------------------------------
# 5. generate and save IRFs
# -----------------------------------------

irf = results.irf(12)
irf.plot(orth=True)
plt.tight_layout()
plt.savefig("irf_plot.png")

# -----------------------------------------
# 6. generate and save FEVD
# -----------------------------------------

fevd = results.fevd(12)
fevd.plot()
plt.tight_layout()
plt.savefig("fevd_plot.png")
