from os import stat
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import psycopg2
import redis

import logging
from configparser import ConfigParser

from scripts import search, fetch, news, top_stocks

MODE = "development"

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)


def db_config(filename, section):
    parser = ConfigParser()
    parser.read(filename)

    if parser.has_section(section):
        params = parser.items(section)

    creds = {}

    for param in params:
        creds[param[0]] = param[1]

    return creds

try:
    logging.log(msg="Connecting to PG database", level=logging.INFO)
    creds = db_config('./database.ini', 'development')
    conn = psycopg2.connect(
        host=creds['host'],
        database=creds['database'],
        user=creds['user'],
        password=creds['password'],
        keepalives_idle=10
    )
    logging.log(msg=f"Connection to {MODE} PG database established", level=logging.INFO)

except Exception as e:
    logging.critical("Error Connecting to PG database")


try:
    logging.log(msg="Connecting to Redis database", level=logging.INFO)
    redis_client = redis.Redis(host='redis-server', port=6379, db=1)
    logging.log(msg=f"Connection to {MODE} redis established", level=logging.INFO)

except Exception as e:
    logging.critical(f"Error Connecting to Redis database: {e}")

class SearchResource(BaseModel):
    query: str

@app.post('/search')
def _search(request_body: SearchResource):
    logging.log(msg=f"Search hit with {request_body.query=}", level=logging.DEBUG)
    results = search.search_stocks(redis_client, conn, request_body.query)

    return results


class StockResource(BaseModel):
    symbol: str

@app.post('/performance')
def _performance(request_body: StockResource):
    result = fetch.get_stock(conn, request_body.symbol)

    if result is None:
        raise HTTPException(status_code=418, detail="Symbol not found") 

    return result


@app.get('/news')
def _news():
    result = news.general(redis_client)

    return result


@app.get('/top/{index}')
def _get_top_gainers(index: str):
    ALLOWED_INDICES = ['gainers', 'loosers']
    try:
        if index not in ALLOWED_INDICES:
            raise HTTPException(status_code=405, detail="Index not allowed")
    except Exception as e:
        logging.error(f"Error {e}")
        return {"Error": e}
           
    result = top_stocks.performance(index)
    return result
