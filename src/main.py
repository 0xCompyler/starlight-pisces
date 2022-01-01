from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import psycopg2

import logging
from configparser import ConfigParser



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
logging.log(msg="Connecting to database", level=logging.INFO)


def db_config(filename, section):
    parser = ConfigParser()
    parser.read(filename)

    if parser.has_section(section):
        params = parser.items(section)

    creds = {}

    for param in params:
        creds[param[0]] = param[1]

    return creds

logging.log(msg="Connecting to database", level=logging.INFO)

creds = db_config('./database.ini', 'development')
conn = psycopg2.connect(
        host=creds['host'],
        database=creds['database'],
        user=creds['user'],
        password=creds['password']
    )

