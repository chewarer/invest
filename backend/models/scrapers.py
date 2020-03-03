from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from ..models.base import DBModelMixin


IDEAS_DOC_NAME = 'ideas'


class Idea(BaseModel):
    """Idea item"""
    row_id: int
    source: str
    date_open: datetime
    date_close: datetime
    currency: str
    open_price: float
    prognoze_profit_percent: float
    target_price: float
    prognoze_profit: float
    title: str
    ticker_short_name: str
    ticker: str
    body: str
    status: str
    market: Optional[str]
    recommendation: str
    author: str
    author_type: Optional[str]
    accuracy: Optional[float]


class IdeaInDB(DBModelMixin, Idea):
    _id: str
    origin_data: Optional[dict]

    class Meta:
        collection: str = IDEAS_DOC_NAME


class TinkoffIdeaInDB(IdeaInDB):
    source: str = 'tinkoff'
    status: str = 'open'
    recommendation: str = 'Покупать'


class BksIdeaInDB(IdeaInDB):
    source: str = 'bks'
