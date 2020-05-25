from typing import Optional
from datetime import datetime

from pydantic import BaseModel

from backend.models.base import DBModelMixin

STOCKQUOTE_DOC_NAME = 'stock_quotes'


class StockQouteBase(BaseModel):
    date: datetime
    ticker_short_name: str
    ticker: str
    open_price: Optional[float] = None
    close_price: Optional[float] = None
    low_price: Optional[float] = None
    high_price: Optional[float] = None


class IssStockQouteBase(StockQouteBase):
    currency: str = 'RUB'


class IssStockQouteInDB(DBModelMixin, IssStockQouteBase):
    _id: str
    board_id: str

    class Meta:
        collection: str = 'stock_quotes'


class SPBStockQouteBase(StockQouteBase):
    currency: str
    market_price: float
    trading_volume: float


class SPBStockQouteInDB(DBModelMixin, IssStockQouteBase):
    _id: str
    board_id: str = 'SPB'

    class Meta:
        collection: str = 'stock_quotes_spb'
