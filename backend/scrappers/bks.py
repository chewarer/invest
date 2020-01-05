from datetime import datetime

from .base import BaseApiClient, BaseModel


class Idea(BaseModel):
    """Idea item"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.source = 'bks'
        self.date_open = datetime.fromtimestamp(kwargs.get('date_open'))
        self.date_close = datetime.fromtimestamp(kwargs.get('date_close'))
        self.currency = kwargs.get('currency')
        self.open_price = kwargs.get('open_price', 0)
        self.target_price = kwargs.get('target_price', 0)
        self.prognoze_profit = self.target_price - self.open_price
        self.prognoze_profit_percent = self.prognoze_profit * 100 / self.open_price
        self.title = kwargs.get('title')
        self.ticker_short_name = kwargs.get('ticker_short_name')
        self.ticker = kwargs.get('secur_code')
        self.body = kwargs.get('body')
        self.status = kwargs.get('status')
        self.market = kwargs.get('market')
        self.recommendation = kwargs.get('recommendation')
        self.author = kwargs.get('author')
        self.author_type = kwargs.get('authorType')
        self.origin_data = kwargs


def parse_ideas():
    url = 'https://api.bcs.ru/express_ideas/v2'
    params = {
        'limit': 10,
        'offset': 0,
        'sort': 'new',
        'status': 'open',
    }
    ideas = []

    api_client = BaseApiClient(url, params)

    response = api_client.execute_request()
    if response:
        ideas = response.get('ideas')

    i = []

    for _idea in ideas:
        idea = Idea(**_idea)
        idea.save()
        i.append(idea)

    return i
