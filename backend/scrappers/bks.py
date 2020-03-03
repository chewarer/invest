from datetime import datetime

from .base import BaseApiClient
from ..models.scrapers import BksIdeaInDB
from ..mongodb import get_mongo_connection


async def parse_ideas(limit: int = 20, offset: int = 0):
    """
        Get ideas from bks.ru
    """
    url = 'https://api.bcs.ru/express_ideas/v2'
    params = {
        'limit': limit,
        'offset': offset,
        'sort': 'new',
        # 'status': 'open',
    }
    count = 0
    db = get_mongo_connection()

    api_client = BaseApiClient(url, params)

    response = api_client.execute_request()
    if not response:
        print('No response')
        return

    ideas = response.get('ideas')

    for i in ideas:
        _open_price = i.get('open_price', 0)
        _target_price = i.get('target_price', 0)
        _prognoze_profit = _target_price - _open_price

        try:
            idea = BksIdeaInDB(
                row_id=i.get('id'),
                source='bks',
                date_open=datetime.fromtimestamp(i.get('date_open')),
                date_close=datetime.fromtimestamp(i.get('date_close')),
                currency=i.get('currency'),
                open_price=_open_price,
                target_price=_target_price,
                prognoze_profit=_prognoze_profit,
                prognoze_profit_percent=_prognoze_profit * 100 / _open_price,
                title=i.get('title'),
                ticker_short_name=i.get('ticker_short_name'),
                ticker=i.get('secur_code'),
                body=i.get('body'),
                status=i.get('status'),
                market=i.get('market'),
                recommendation=i.get('recommendation'),
                author=i.get('author'),
                author_type=i.get('authorType'),
                origin_data=i,

                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        except Exception as e:
            print(e)
            continue

        exists_record = await BksIdeaInDB.exists(
            db, {'row_id': idea.row_id, 'source': idea.source}
        )

        if not exists_record:
            count += 1
            await idea.insert_one(db, idea.dict())

    print(f'Added: {count} new ideas')
