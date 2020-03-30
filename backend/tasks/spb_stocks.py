"""
    Parser for stock quotes from SPB.
"""

from datetime import datetime
import requests

from bs4 import BeautifulSoup
from bs4.element import NavigableString

from ..scrappers.base import BaseApiClient
from ..models.scrapers import BksIdeaInDB
from ..mongodb import get_mongo_connection

# data = {
#   'ctl00$ScriptManager1': 'ctl00$BXContent$up|ctl00$BXContent$pager$ctl00$ctl01',
#   '__EVENTTARGET': 'ctl00$BXContent$pager$ctl00$ctl01',
#   'bxValidationToken': 'b369f92935d137c3644d9c0a28b2112e',
#   '__VIEWSTATE': '/wEPDwULLTE2NzEyMDU5NjlkGAcFFWN0bDAwJEJYQ29udGVudCRwYWdlcg8UKwAEZGQCHgLoCWQFFWN0bDAwJEJYQ29udGVudCRjdGwwMg88KwAMAQgCAWQFFWN0bDAwJEJYQ29udGVudCRsdk1zZQ88KwAOAwhmDGYNAv////8PZAUVY3RsMDAkQlhDb250ZW50JGN0bDAxDzwrAAwBCGZkBRljdGwwMCRCWENvbnRlbnQkTGlzdFZpZXcxDxQrAA5kZGRkZGRkPCsAHgAC6AlkZGRmAh5kBRljdGwwMCRCWENvbnRlbnQkTGlzdFZpZXcyDxQrAA5kZGRkZGRkPCsAHwACH2RkZGYC/////w9kBR5fX0NvbnRyb2xzUmVxdWlyZVBvc3RCYWNrS2V5X18WAQUxY3RsMDAkc2VhcmNoZm9ybTEkc2VhcmNoZm9ybTEkc2VhcmNoZm9ybTEkYnRuU3JjaNCIVaDH4UmZvhm8YpatPnjP6ZEg',
#   '__EVENTVALIDATION': '/wEdAAguskZwOrUmMQPbniw/ApDffFsezz3GuGexXlwRGdGgE4jhaSetPRJbd7PpVxUwh7ErMztzIdeECOB8HduAT+aYatv6ulkbHiqn5jKmgpRD5KweYQs9CvY1lKV7PUZ5lQrBdyzUeOwNGqXC2OIcx2DgVlbSndBZ/D440pzDsjQwUDHI/ms5bhT0KNuiyNRpr08z+K1Z',
#
#   # 'bitrix_include_areas': 'N',
#   # '__EVENTARGUMENT': '',
#   # 'ctl00$searchform1$searchform1$searchform1$query': '\u041F\u043E\u0438\u0441\u043A...',
#   # '__VIEWSTATEGENERATOR': '1E76840D',
#   # '__ASYNCPOST': 'true',
# }


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


def get_for_date(trade_date: str):
    """
        Get stock quotes for specified date.
        And save to DB.
        :param: trade_date: format - '2020.12.31'
    """

    # db = get_mongo_connection()

    url = 'https://spbexchange.ru/ru/market-data/totalsArch.aspx'

    params = (
        ('date', trade_date),
    )

    init_page = requests.get(url, params, verify=False)

    if init_page.status_code != 200:
        print(f'Wrong response: f{init_page.status_code}')
        return

    html = BeautifulSoup(init_page.text)

    bx_validation_token = html.find('input', {"name":"bxValidationToken"}).get('value')
    viewstate = html.select_one('#__VIEWSTATE').get('value')
    event_validation = html.select_one('#__EVENTVALIDATION').get('value')
    view_state_generator = html.select_one('#__VIEWSTATEGENERATOR').get('value')

    cookies = dict(init_page.cookies)

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'X-Requested-With': 'XMLHttpRequest',
        'X-MicrosoftAjax': 'Delta=true',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        'Origin': 'https://spbexchange.ru',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
    }

    htmls = []
    is_last_pager = False

    for i in range(100):
        if is_last_pager:
            break

        pager_links = [
            (item.text, item['href'].split("'")[1])
            for item in html.select('#ctl00_BXContent_pager a')
        ]

        if i != 0:
            is_last_pager = len([x[0] for x in pager_links if x[0] == '...']) < 2

        print('** New pager block', pager_links)

        for page_name, page in pager_links:
            if page_name == '...' and page.endswith('$ctl00'):
                continue

            raw_srtring = html.select_one('body').contents[-1]
            if isinstance(raw_srtring, NavigableString):
                el = raw_srtring.split('|')
                if '__VIEWSTATE' in el:
                    viewstate = el[el.index('__VIEWSTATE') + 1]

                if '__EVENTVALIDATION' in el:
                    event_validation = el[el.index('__EVENTVALIDATION') + 1]

            data = {
                'ctl00$ScriptManager1': f'ctl00$BXContent$up|{page}',
                '__EVENTTARGET': page,
                'bxValidationToken': bx_validation_token,
                '__VIEWSTATE': viewstate,
                '__EVENTVALIDATION': event_validation,
                '__VIEWSTATEGENERATOR': view_state_generator,
            }

            response = requests.post(
                url,
                headers=headers,
                params=params,
                cookies=cookies,
                data=data,
                verify=False,
            )

            if response.status_code != 200:
                print(f'Wrong response: {response.status_code}')
                return

            html = BeautifulSoup(response.text)
            htmls.append(html)


def bypass_pages(url: str, pager: list) -> list:
    """"""
