from flask import Flask, request, render_template
import pandas as pd
import numpy as np
from datetime import datetime
import pandas_datareader as pdr
import matplotlib.pyplot as plt


start_date = '2014-01-01'
end_date = '2019-01-01'



app = Flask(__name__)

@app.route('/')
def display_portfolio():
   return render_template('index.html')


@app.route('/result', methods = ['POST','GET'])
def result():
    if request.method == 'POST':
        print(request.form)
        stocks = request.form['stocks'].split()
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        window = int(request.form['window'])
        print(stocks)
        return render_template('results.html', stocks=stocks, start_date=start_date, window=window)

if __name__ == '__main__':
   app.run(debug=True)
