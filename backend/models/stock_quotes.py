from typing import Optional
from datetime import datetime

from pydantic import BaseModel

from backend.models.base import DBModelMixin

STOCKQUOTE_DOC_NAME = 'stock_quotes'


class StockQoute(BaseModel):
    date: datetime
    ticker_short_name: str
    ticker: str
    open_price: Optional[float] = None
    close_price: Optional[float] = None
    low_price: Optional[float] = None
    high_price: Optional[float] = None
    currency: str = 'RUB'


class StockQouteInDB(DBModelMixin, StockQoute):
    _id: str
    board_id: str

    class Meta:
        collection: str = STOCKQUOTE_DOC_NAME
