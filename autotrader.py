from flask import Flask, request, render_template
import pandas as pd
import numpy as np
import quandl
quandl.ApiConfig.api_key = 'yDsZNbJArbvQby72sxM9'

portfolio_df = pd.read_excel('portfolio.xlsx').set_index('stock')
start_date = '2014-01-01'
end_date = '2019-01-01'



app = Flask(__name__)

@app.route('/')
def display_portfolio():
   return render_template('index.html', table = portfolio_df.to_html())

if __name__ == '__main__':
   app.run(debug=True)
