"""
    Loader stock quotes from Moscow Exchange ISS server.
    Docs:
        https://www.moex.com/a2193
        http://iss.moex.com/iss/reference/
"""
from datetime import datetime, timedelta

from pydantic import ValidationError

from backend.scrappers.base import BaseApiClient
from backend.mongodb import get_mongo_connection
from backend.models.stock_quotes import StockQouteInDB


HOST = 'https://iss.moex.com/'


def get_fmt(resp_format: str = 'json'):
    """Return expected response format"""
    return dict(
        json='.json',
        xml='.xml',
        csv='.csv',
        html='',
    ).get(resp_format, '')


def shares_endpoint(api_client: BaseApiClient, start: int = 0) -> dict:
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
        share: dict = shares_endpoint(api_client, page)
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


async def get_shares_between(date_from: str, date_to: str):
    """
        Get shares between dates inclusive.
        Date format: '2020-12-31'
    """
    fmt = '%Y-%m-%d'
    date_from = datetime.strptime(date_from, fmt)
    date_to = datetime.strptime(date_to, fmt)

    days = date_to - date_from
    days = days.days

    for day in range(days + 1):
        trade_date = date_from + timedelta(days=day)
        await get_for_date(datetime.strftime(trade_date, fmt))


async def get_for_date(trade_date: str):
    """
        Get stock quotes for specified date.
        And save to DB.
        :param: trade_date: format - '2020-12-31'
    """

    db = get_mongo_connection()

    exists_record = await StockQouteInDB.exists(
        db, {'date': datetime.strptime(trade_date, '%Y-%m-%d'), 'board_id': 'TQBR'}
    )
    if exists_record:
        print(f'Stock quotes for the date {trade_date} already exists')
        return

    shares = get_shares(trade_date)

    print(f'Received stocks: {len(shares)}')

    for share in shares:
        try:
            stock = StockQouteInDB(
                date=datetime.strptime(share['TRADEDATE'], '%Y-%m-%d'),
                ticker_short_name=share['SECID'],
                ticker=share['SHORTNAME'],
                open_price=share['OPEN'],
                close_price=share['CLOSE'],
                low_price=share['LOW'],
                high_price=share['HIGH'],
                board_id=share['BOARDID'],
                # TODO: Need to add these fields automatically
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        except ValidationError as e:
            print(f'Validation error. Ticker: {share["SHORTNAME"]}. {e}')
            continue

        await stock.insert_one(db, stock.dict())
