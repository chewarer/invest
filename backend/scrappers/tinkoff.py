from datetime import datetime

from dateutil.parser import parse

from .base import BaseApiClient
from ..models.scrapers import TinkoffIdeaInDB
from ..mongodb import get_mongo_connection


async def parse_ideas(limit: int = 20):
    """
        Get ideas from tinkoff.ru
    """
    url = 'https://api-invest.tinkoff.ru/smartfeed-public/v1/feed/api/ideas'
    params = {
        'limit': limit,
        'broker_id': 'all',
    }
    count = 0
    db = get_mongo_connection()

    api_client = BaseApiClient(url, params)

    response = api_client.execute_request()
    if not response:
        print('No response')
        return

    ideas = response.get('payload', {}).get('ideas', {})

    for i in ideas:
        _open_price = i.get('price_start', 0)
        _prognoze_profit_percent = i.get('target_yield')

        idea = TinkoffIdeaInDB(
            row_id=i.get('id'),
            date_open=parse(i.get('date_start')),
            date_close=parse(i.get('date_end')),
            currency=i.get('tickers', {})[0].get('currency'),
            open_price=_open_price,
            prognoze_profit_percent=_prognoze_profit_percent,
            target_price=round(_open_price + (_open_price / 100 * _prognoze_profit_percent), 2),
            prognoze_profit=round((_open_price
                                   + (_open_price / 100 * _prognoze_profit_percent)
                                   - _open_price), 2),
            title=i.get('title'),
            ticker_short_name=i.get('tickers', {})[0].get('name'),
            ticker=i.get('tickers', {})[0].get('ticker'),
            body=i.get('description'),
            market=i.get('market'),
            author=i.get('broker', {}).get('name'),
            accuracy=i.get('broker', {}).get('accuracy'),
            origin_data=i,

            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        exists_record = await TinkoffIdeaInDB.exists(
            db, {'row_id': idea.row_id, 'source': idea.source}
        )

        if not exists_record:
            count += 1
            await idea.insert_one(db, idea.dict())

    print(f'Added: {count} new ideas')
