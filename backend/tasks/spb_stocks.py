"""
    Parser for stock quotes from SPB.
"""

from datetime import datetime
from typing import Union

import requests

from bs4 import BeautifulSoup as bs
from bs4.element import NavigableString

from ..scrappers.base import BaseApiClient
from ..models.scrapers import BksIdeaInDB
from ..mongodb import get_mongo_connection


def get_shares(trade_date: str) -> tuple:
    """
        Get stock quotes for specified date.
        :param: trade_date: format - '2020.12.31'
    """
    page = 0
    url = f'https://spbexchange.ru/ru/market-data/totalsArch.aspx?date={trade_date}#EQF'


async def get_shares_between(date_from: str, date_to: str):
    """
        Get shares between dates inclusive.
        Date format: '2020-12-31'
    """
    fmt = '%Y-%m-%d'


class SPBparser:
    """
        PArse data from SPB stock securities
    """
    HOST = 'https://spbexchange.ru/'
    url = f'{HOST}ru/market-data/totalsArch.aspx'

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:73.0) '
                      'Gecko/20100101 Firefox/73.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'X-Requested-With': 'XMLHttpRequest',
        'X-MicrosoftAjax': 'Delta=true',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        'Origin': f'{HOST}',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
    }

    def __init__(self, trade_date: str):
        self.page = 0
        self.trade_date = trade_date
        self.cookies = {}
        self.request_data = {}
        self.params = (
            ('date', trade_date),
        )
        self.data = {}
        self.html: bs = ...

    def get_init_page(self) -> Union[bs, bool]:
        """
            Get start page with stock quotes
        """
        init_page = requests.get(self.url, self.params, verify=False)

        if init_page.status_code != 200:
            print(f'Wrong response: f{init_page.status_code}')
            return False

        self.page += 1
        self.cookies = dict(init_page.cookies)

        html = self.read_html(init_page.text)
        self.html = html

        self.data = {
            'bxValidationToken': html.find('input', {"name": "bxValidationToken"}).get('value'),
            '__VIEWSTATE': html.select_one('#__VIEWSTATE').get('value'),
            '__EVENTVALIDATION': html.select_one('#__EVENTVALIDATION').get('value'),
            '__VIEWSTATEGENERATOR': html.select_one('#__VIEWSTATEGENERATOR').get('value'),
        }

        return html

    @staticmethod
    def read_html(raw_html):
        return bs(raw_html, 'html.parser')

    def get_pager_links(self) -> [dict, bool]:
        """
            Return pager links
        """
        pager_element = self.html.select('#ctl00_BXContent_pager a')
        pager_links = {
            item.text: item['href'].split("'")[1]
            for item in pager_element
            if not item['href'].split("'")[1].endswith('$ctl00')
        }

        is_last_pager = '...' in pager_links.keys()

        return pager_links, is_last_pager

    def update_request_data(self, page: str):
        raw_string = self.html.contents[-1]
        if isinstance(raw_string, NavigableString):
            el = raw_string.split('|')
            if '__VIEWSTATE' in el:
                self.data['__VIEWSTATE'] = el[el.index('__VIEWSTATE') + 1]

            if '__EVENTVALIDATION' in el:
                self.data['__EVENTVALIDATION'] = el[el.index('__EVENTVALIDATION') + 1]

        self.data['ctl00$ScriptManager1'] = f'ctl00$BXContent$up|{page}'
        self.data['__EVENTTARGET'] = page

    def get_next_page(self) -> Union[bs, bool]:
        """
            Get page by new parameters
        """
        response = requests.post(
            self.url,
            headers=self.headers,
            params=self.params,
            cookies=self.cookies,
            data=self.data,
            verify=False,
        )

        if response.status_code != 200:
            print(f'Wrong response: {response.status_code}')
            return False

        self.html = self.read_html(response.text)
        self.page += 1

        return self.html


class HTMLParser:
    """
        Parse HTML with stocks quotes
    """


def get_for_date(trade_date: str):
    """
        Get stock quotes for specified date.
        And save to DB.
        :param: trade_date: format - '2020.12.31'
    """
    parser = SPBparser(trade_date=trade_date)
    htmls = list()
    is_last_pager = False

    html = parser.get_init_page()
    htmls.append(html)

    while not is_last_pager:
        pager_links, is_last_pager = parser.get_pager_links()
        print('** New pager block', pager_links)

        for page_name, page in pager_links.items():
            parser.update_request_data(page)
            html = parser.get_next_page()
            htmls.append(html)

    return htmls
