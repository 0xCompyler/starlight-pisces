import psycopg2
from psycopg2.extensions import connection

import json
import datetime
import redis
from redis.client import Redis

def search_stocks(redis_client: Redis, conn: connection, query: str):
    cached_data = redis_client.get(query)

    if cached_data is not None:
        json_data = json.loads(cached_data)
        return json_data

    else:
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT st.isin_number, st.symbol, st.name FROM stocks st
                INNER JOIN search sch 
                ON st.isin_number = sch.isin_number
                ORDER BY SIMILARITY(search_col, %s) DESC
                LIMIT 10;
                """,
            (query, ))

        except Exception as e:
            return {'error': e}

        query_results = cur.fetchall()
        results = []

        for item in query_results:
            temp_dict = {
                "isin_number": item[0],
                "symbol": item[1],
                "name": item[2]
            }

            results.append(temp_dict)

        redis_client.setex(query, datetime.timedelta(hours=24), json.dumps(results))
        return results

