from datetime import datetime
from pandas import Timestamp

import yfinance as yf
import pandas as pd
import logging


def get_historical_prices(symbol):
    ticket = yf.Ticker(symbol)
    data = ticket.history()

    return data



print(get_historical_prices('AAPL'))