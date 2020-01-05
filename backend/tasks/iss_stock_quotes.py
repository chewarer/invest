"""
    Loader stock quotes from Moscow Exchange ISS server.
    Docs:
        https://www.moex.com/a2193
        http://iss.moex.com/iss/reference/
"""

from typing import Union
from backend.scrappers.base import BaseApiClient


HOST = 'https://iss.moex.com/'


def get_fmt(resp_format: str = 'json'):
    """Return expected response format"""
    return dict(
        json='.json',
        xml='.xml',
        csv='.csv',
        html='',
    ).get(resp_format, '')


def shares_endpoint(api_client: BaseApiClient, start: int = 0) -> Union[dict, str]:
    """Get shares from api"""
    api_client.params['start'] = start

    return api_client.execute_request()


def get_shares(trade_date: str) -> tuple:
    """
        Get stock quotes for specified date.
        :param: trade_date: format - '2020-12-31'
    """
    page = 0
    history = dict()

    url = f'{HOST}iss/history/engines/stock/markets/shares/boards/tqbr/securities{get_fmt("json")}'
    params = dict(date=trade_date, start=page)

    api_client = BaseApiClient(url, params)

    while True:
        share = shares_endpoint(api_client, page)
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
