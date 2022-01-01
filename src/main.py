from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import psycopg2
import redis

import logging
from configparser import ConfigParser

from scripts import search

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
        password=creds['password']
    )
    logging.log(msg=f"Connection to {MODE} PG database established", level=logging.INFO)

except Exception as e:
    logging.critical("Error Connecting to PG database")


try:
    logging.log(msg="Connecting to Redis database", level=logging.INFO)
    redis_client = redis.Redis(host='localhost', port=6379, db=1)
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


