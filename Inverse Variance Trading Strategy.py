#!/usr/bin/env python
# coding: utf-8

# # Inverse Variance Trading strategy
# 1. Get the EOD data of top large cap stocks.
# 2. Calculate inverse variance of the stocks.
# 3. Calculate the portfolio weights.

import pandas as pd
import pandas_datareader as pdr
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
# get_ipython().run_line_magic('matplotlib', 'inline')

# Get data
start_date = datetime(1999, 1, 1)
end_date = datetime.today()
initial_capital = 1000000

stocks = ['MSFT','AAPL','GOOG','AMZN','XOM','HSBC','BRK-B','JPM','BAC','WFC']

print("Loading data for following stocks: ")
print(stocks)
spy = pdr.get_data_yahoo(symbols='SPY', start=start_date, end=end_date)
stock_data = pdr.get_data_yahoo(symbols=stocks, start=start_date, end=end_date)
print("Stock data loaded ...")

# Calculate Benchmark Returns
spy['Returns'] = spy['Adj Close'].pct_change(1)


# Calculate returns
for ticker in stock_data.columns.levels[1]:
    stock_data['Return', ticker] = stock_data['Adj Close', ticker].pct_change(1)
print("Calculated Returns ...")

# Calculate Inverse Variance
for ticker in stock_data.columns.levels[1]:
    stock_data['InvVar', ticker] = stock_data['Return', ticker].rolling(200).apply(lambda x: 1/x.var(), raw=False)
    
# Calculate Portfolio weights
df = stock_data.InvVar
df = df.div(df.sum(axis=1), axis=0)
for ticker in stock_data.columns.levels[1]:
    stock_data['Weights', ticker] = df[ticker].round(2)
del df
print("Calculated Portfolio Weights ...")

# Remove NaN values
stock_data.dropna(inplace=True)


# # Portfolio Returns
# 1. Get Change in weights
# 2. Get number of shares
# 3. Get Trading costs
# 4. Calculate Porfolio Value and Cumulative returns.


Portfolio = stock_data[['Adj Close', 'Weights']]

stock_val = np.array(Portfolio['Adj Close'])
stock_weight = np.array(Portfolio['Weights'])
port_val = np.empty(shape=stock_val.shape[0])
shares_holding = np.empty(shape=stock_val.shape)
traded_volume = np.zeros(shape=stock_val.shape)
traded_value = np.zeros(shape=stock_val.shape)
trading_cost = np.zeros(shape=stock_val.shape)

shares_holding[0] = np.round_(stock_weight[0]/stock_val[0]*initial_capital)
port_val[0] = np.dot(shares_holding[0], stock_val[0])

for ind in range(1, len(stock_val)):
    shares_holding[ind] = shares_holding[ind-1] + np.round_((stock_weight[ind]-stock_weight[ind-1])/stock_val[ind]*port_val[ind-1])
    traded_volume[ind] = shares_holding[ind] - shares_holding[ind-1]
    traded_value[ind] = traded_volume[ind]*stock_val[ind]
    trading_cost[ind] = 0.01*abs(traded_value[ind])   
    port_val[ind] = np.dot(shares_holding[ind], stock_val[ind])
    port_val[ind] = port_val[ind] - traded_value[ind].sum() + trading_cost[ind].sum()

print("Calculated Portfolio returns ...")

Portfolio['Value'] = pd.DataFrame(data=port_val, index=Portfolio['Adj Close'].index) 
Portfolio['Return'] = Portfolio['Value'].pct_change(1)
Traded_Volume = pd.DataFrame(data=traded_volume, index=Portfolio['Adj Close'].index, columns=Portfolio['Adj Close'].columns)
Traded_Value = pd.DataFrame(data=traded_value, index=Portfolio['Adj Close'].index, columns=Portfolio['Adj Close'].columns)
Trading_Cost = pd.DataFrame(data=trading_cost)
Shares_Holding = pd.DataFrame(data=shares_holding, index=Portfolio['Adj Close'].index, columns=Portfolio['Adj Close'].columns)

del stock_val 
del stock_weight 
del port_val 
del shares_holding
del traded_volume
del traded_value
del trading_cost


# Plot traded volume and shares holding

Traded_Volume['2018-1-1':].plot(kind='bar')
plt.title("Traded Volume")
#plt.figure()
Shares_Holding['2018-1-1':].plot(kind='line')
plt.title("Shares Holding")
#plt.figure()
Portfolio['Value']['2006-1-1':].plot(kind='line')
plt.title("Portfolio Value")

plt.show()

