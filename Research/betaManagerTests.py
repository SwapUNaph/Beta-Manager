import betaManagerFunctions as bm


def main():
    stocks_list = "MSFT AAPL GOOG AMZN XOM HSBC BRK-B JPM BAC WFC"
    window = "100"
    capital = "100000"

    print(bm.get_portfolio_weights([stocks_list, window, capital]))


if __name__ == '__main__':
    main()


