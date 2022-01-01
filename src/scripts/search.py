import psycopg2
from psycopg2.extensions import connection


def search_stocks(conn: connection, query: str):
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
    
    return results

