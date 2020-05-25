from typing import List
from fastapi import FastAPI

from .config import DEBUG
from .mongodb import close_mongo_connection, connect_to_mongo
from .models.stock_quotes import StockQoute, StockQouteInDB


app = FastAPI(debug=DEBUG)

# Init empty mongodb
app.mongodb = None


@app.on_event('startup')
async def startup():
    await connect_to_mongo(app)

app.add_event_handler("shutdown", close_mongo_connection)


@app.get("/")
async def read_root():
    db = app.mongodb
    await db['article_collection_name'].insert_one({'article_doc': 'test', 'dfd': '444'})
    return {"Hello": "World"}


# @app.get("/stock/{date}", response_model=StockQoute)
@app.get("/stock", response_model=List[StockQoute])
async def read_user():
    db = app.mongodb
    # xx = await StockQouteInDB.find_one(conn=db, q_filter={'ticker_short_name': 'ABRD'})
    xx = await StockQouteInDB.find(conn=db, q_filter={'ticker_short_name': 'ALNU'}, limit=20)
    print(xx)
    return xx


# db.drop_collection('article_collection_name')
