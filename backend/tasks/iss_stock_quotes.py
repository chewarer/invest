"""
    Loader stock quotes from Moscow Exchange ISS server.
    Docs:
        https://www.moex.com/a2193
        http://iss.moex.com/iss/reference/
"""

import json
from urllib.error import HTTPError

import requests
from requests import ReadTimeout
from user_agent import generate_user_agent

from ..repeater import repeater


HOST = 'https://iss.moex.com/'
HEADERS = {'User-Agent': generate_user_agent(device_type="desktop", os=('mac', 'linux'))}


@repeater()
def get_url_data(url: str, params=None) -> str:
    """Download page from url"""
    try:
        html = requests.get(url, params=params, headers=HEADERS, timeout=30)
        print(f'{html.status_code}: {html.url}')
    except HTTPError as e:
        print(f'Error on url {url}: {e}')
    except ReadTimeout as e:
        print(f'Error on url {url}: {e}')
    else:
        return html.text


def shares_endpoint(trade_date: str, resp_format: str = 'json', start: int = 0) -> dict:
    """Get shares from api"""
    fmt = dict(
        json='.json',
        xml='.xml',
        csv='.csv',
        html='',
    ).get(resp_format, '')

    url = f'{HOST}iss/history/engines/stock/markets/shares/boards/tqbr/securities{fmt}'

    params = dict(date=trade_date, start=start)

    stock = get_url_data(url, params)

    return json.loads(stock)


def get_shares(trade_date: str) -> tuple:
    """
        Get stock quotes for specified date.
        :param: trade_date: format - '2020-12-31'
    """
    page = 0
    history = dict()

    while True:
        share = shares_endpoint(trade_date, 'json', page)
        if not history:
            # first iteration
            history = share.get('history')
        else:
            _history_data = share.get('history', {}).get('data')
            if _history_data:
                history['data'].extend(_history_data)

        # Pager data
        p_cols = share.get('history.cursor', {}).get('columns')
        p_data = share.get('history.cursor', {}).get('data')

        cursor = dict(zip(p_cols, p_data[0]))

        if int(cursor['INDEX']) + int(cursor['PAGESIZE']) < int(cursor['TOTAL']):
            page = int(cursor['INDEX']) + int(cursor['PAGESIZE'])
        else:
            break

    # convert each data row to dict
    history_data = tuple(
        (dict(zip(history.get('columns'), row)))
        for row in history.get('data')
    )

    return history_data
