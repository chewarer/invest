# Tickers
# ftp://ftp.nasdaqtrader.com/symboldirectory
# ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqlisted.txt
# ftp://ftp.nasdaqtrader.com/symboldirectory/otherlisted.txt
# https://www.nasdaq.com/market-activity/stocks/screener

import shutil
import urllib.request as request
from contextlib import closing
import csv
from typing import Union

from bs4 import BeautifulSoup

from backend.scrappers.base import BaseApiClient


def get_tickers(url):
    tmpfile = '/tmp/tmp.csv'

    with closing(request.urlopen(url)) as resp:
        with open(tmpfile, 'wb') as f:
            shutil.copyfileobj(resp, f)

    with open(tmpfile, 'r') as f:
        reader = csv.DictReader(f, delimiter='|')
        data = [row for row in reader]

    tickers = [x.get('Symbol') for x in data]

    return tickers


def all_tickers():
    urls = dict(
        url_nasdaq='ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqlisted.txt',
        url_other='ftp://ftp.nasdaqtrader.com/symboldirectory/otherlisted.txt',
    )

    tickers = {name: get_tickers(url) for name, url in urls.items()}

    return tickers


def get_sp500_tickers_list() -> Union[tuple, None]:
    """Get Tickers list from S&P 500 components"""
    url = 'https://www.slickcharts.com/sp500'
    api_client = BaseApiClient(url, response_type='text')

    response = api_client.execute_request()
    if not response:
        print('No response')
        return

    html = BeautifulSoup(response, 'html.parser')
    table = html.select('table tbody tr')

    tickers = tuple(row.select('td')[2].text for row in table)

    return tickers
