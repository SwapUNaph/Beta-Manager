import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Flask, request, render_template
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
import pandas_datareader as pdr



app = Flask(__name__)

@app.route('/')
def display_portfolio():
   return render_template('index.html')


@app.route('/result', methods = ['POST','GET'])
def result():
    if request.method == 'POST':
        print(request.form)
        stocks = request.form['stocks'].split()
        strt_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        window = int(request.form['window'])
        print(stocks)

        # Get data
        start_date = strt_date - timedelta(window+5)
        end_date = datetime.today()
        initial_capital = 1000000

        # stocks = ['MSFT','AAPL','GOOG','AMZN','XOM','HSBC','BRK-B','JPM','BAC','WFC']

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
            stock_data['InvVar', ticker] = stock_data['Return', ticker].rolling(window).apply(lambda x: 1/x.var(), raw=False)

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
            port_val[ind] = port_val[ind] - traded_value[ind].sum() - trading_cost[ind].sum()

        print("Calculated Portfolio returns ...")

        Portfolio['Value'] = pd.DataFrame(data=port_val, index=Portfolio['Adj Close'].index)
        # Portfolio['Return'] = Portfolio['Value'].pct_change(1)
        Traded_Volume = pd.DataFrame(data=traded_volume, index=Portfolio['Adj Close'].index, columns=Portfolio['Adj Close'].columns)
        # Traded_Value = pd.DataFrame(data=traded_value, index=Portfolio['Adj Close'].index, columns=Portfolio['Adj Close'].columns)
        # Trading_Cost = pd.DataFrame(data=trading_cost)
        # Shares_Holding = pd.DataFrame(data=shares_holding, index=Portfolio['Adj Close'].index, columns=Portfolio['Adj Close'].columns)

        del stock_val
        del stock_weight
        del port_val
        del shares_holding
        del traded_volume
        del traded_value
        del trading_cost

        to_trade = Traded_Volume.iloc[-1].to_dict()

        #Plot traded volume and shares holding

        # ax1 = plt.gca()
        # (Portfolio['Value']/Portfolio['Value'].iloc[0])[start_date:].plot(figsize=(10,6), ax=ax1, title="Portfolio Performance");
        # (spy['Adj Close']/spy['Adj Close'][Portfolio['Value'].index.values[0]])[start_date:].plot(ax=ax1);
        # ax1.legend(['Portfolio','S&P 500'])
        # portfolio_value_url = 'static/img/portfolio_value.png'
        # plt.savefig(portfolio_value_url)

        fig = plt.figure(figsize=(10,6))
        ax = plt.subplot(111)
        ax.plot((Portfolio['Value']/Portfolio['Value'].iloc[0])[start_date:])
        ax.plot((spy['Adj Close']/spy['Adj Close'][Portfolio['Value'].index.values[0]])[start_date:])
        plt.xlabel("Date")
        plt.ylabel("Returns")
        plt.title('Portfolio Value')
        ax.legend(['Portfolio','SP 500'])
        #plt.show()
        portfolio_value_url = 'static/img/portfolio_value.png'
        fig.savefig(portfolio_value_url)

        fig2 = plt.figure(figsize=(10,6))
        ax2 = plt.subplot(111)
        ax2.pie(Portfolio['Weights'].iloc[-1], autopct='%.2f%%', labels=Portfolio['Weights'].columns)
        plt.title('Portfolio Composition')

        portfolio_weights_url = 'static/img/portfolio_weights.png'
        fig2.savefig(portfolio_weights_url)

        # ax2 = plt.gca()
        # Portfolio['Weights'].iloc[-1].plot(kind='pie', autopct='%.2f%%', ax=ax2, title="Portfolio Weights", legend=False);
        # portfolio_weights_url = 'static/img/portfolio_weights.png'
        # plt.savefig(portfolio_weights_url)

        return render_template('results.html', stocks=stocks, start_date=strt_date, to_trade=to_trade,
                                window=window,portfolio_weights_url=portfolio_weights_url,
                                portfolio_value_url=portfolio_value_url)

if __name__ == '__main__':
   app.run(debug=True)
