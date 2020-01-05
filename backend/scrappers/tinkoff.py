from dateutil.parser import parse

from .base import BaseApiClient, BaseModel


class Idea(BaseModel):
    """Idea item"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.source = 'tinkoff'
        self.date_open = parse(kwargs.get('date_start'))
        self.date_close = parse(kwargs.get('date_end'))
        self.currency = kwargs.get('tickers', {})[0].get('currency')
        self.open_price = kwargs.get('price_start', 0)
        self.prognoze_profit_percent = kwargs.get('target_yield')
        self.target_price = self.open_price + (self.open_price / 100 * self.prognoze_profit_percent)
        self.prognoze_profit = self.target_price - self.open_price
        self.title = kwargs.get('title')
        self.ticker_short_name = kwargs.get('tickers', {})[0].get('name')
        self.ticker = kwargs.get('tickers', {})[0].get('ticker')
        self.body = kwargs.get('description')
        self.status = 'open'
        self.market = kwargs.get('market')
        self.recommendation = 'Покупать'
        self.author = kwargs.get('broker', {}).get('name')
        self.accuracy = kwargs.get('broker', {}).get('accuracy')
        self.origin_data = kwargs


def parse_ideas():
    url = 'https://api-invest.tinkoff.ru/smartfeed-public/v1/feed/api/ideas'
    params = {
        'limit': 100,
        'broker_id': 'all',
    }
    ideas = []

    api_client = BaseApiClient(url, params)

    response = api_client.execute_request()
    if response:
        ideas = response.get('payload', {}).get('ideas', {})

    i = []

    for _idea in ideas:
        idea = Idea(**_idea)
        idea.save()
        i.append(idea)

    return i
