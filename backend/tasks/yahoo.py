import yfinance as yf
import pandas as pd


class Ticker:
    """
    Detailed info by ticker name
    """

    def __init__(self, ticker_name: str):
        self.ticker_name = ticker_name
        self.company = yf.Ticker(ticker_name)

    def history(self, period: str = '1d', start: str = None, end: str = None) -> pd.DataFrame:
        """
        Get history for period
        :param period:
            Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        :param start: str
            Download start date string (YYYY-MM-DD) or _datetime.
                Default is 1900-01-01
        :param end: str
            Download end date string (YYYY-MM-DD) or _datetime.
            Default is now
        """
        return self.company.history(period=period, start=start, end=end)

    def info(self):
        """
        Get company info
        """