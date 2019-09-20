import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import pandas_datareader as pdr
import json


def get_portfolio_weights(argv):
    '''
    Desciption : Function takes in stock list, window length and investment capital, calculates portfolio weights using inverse variance strategy and outputs the portfolio weights
    
    Based on : https://stackoverflow.com/questions/23450534/how-to-call-a-python-function-from-node-js
    
    @params
    argv : Input string
        argv[0] : String of valid stock tickers in the portfolio
        argv[1] : Duration window (in days) for stock variance calculations
        argv[2] : Portfolio Capital (in cents)
        
    @return
    {"Ticker", weight} in JSON format
    
    '''
    stocks = argv[0].split()
    window = int(argv[1])
    initial_capital = int(argv[2])

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

    tickers = []
    invVar = []

    # Calculate Inverse Variance
    for ticker in stock_data.columns.levels[1]:
        tickers.append(ticker)
        invVar.append(stock_data['Return', ticker].var())

    weights = invVar/sum(invVar)

    portfolio_weights = dict()

    for index, ticker in enumerate(tickers):
        portfolio_weights[ticker] = weights[index]

    return json.dumps(portfolio_weights)

