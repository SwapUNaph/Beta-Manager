import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import pandas_datareader as pdr
from scipy.optimize import minimize
import sys
import json

'''
Based on : https://stackoverflow.com/questions/23450534/how-to-call-a-python-function-from-node-js
argv[1] : String of valid stock tickers in the portfolio
argv[2] : Duration window (in days) for stock variance calculations
argv[3] : Portfolio Capital (in cents)
'''
stocks = sys.argv[1].split()
window = int(sys.argv[2])
initial_capital = int(sys.argv[3])

# print(stocks, window, initial_capital)

# Get data
end_date = datetime.today()
start_date = end_date - timedelta(window+2)
# stocks = ['MSFT','AAPL','GOOG','AMZN','XOM','HSBC','BRK-B','JPM','BAC','WFC']
stock_data = pdr.get_data_yahoo(symbols=stocks, start=start_date, end=end_date)
stock_data = stock_data.dropna()

# Calculate returns
for ticker in stock_data.columns.levels[1]:
    stock_data['Return', ticker] = stock_data['Adj Close', ticker].pct_change(1)
    
stock_data = stock_data.dropna()
# print(stock_data)
cov = stock_data.Return.cov()
# print(covariance)
tickers = list(cov.columns.values)


# Optimization
def cost(w):
    global cov
    portfolio_variance = np.dot(np.dot(w.T, cov), w)
    return portfolio_variance
 
bnds = [(0.0001, 0.9999)]*len(cov)
cons = ({'type': 'eq', 'fun': lambda w: 1.0 - sum(w)})
w0 = np.random.randn(len(cov))/len(cov)

result = minimize(cost, w0, method='SLSQP', bounds=bnds, constraints=cons, tol=1e-6)
# print(result.message)

portfolio_weights = dict()

if result.success:
    weights = result.x
    for index, ticker in enumerate(tickers):
        portfolio_weights[ticker] = weights[index]

print(json.dumps(portfolio_weights))
