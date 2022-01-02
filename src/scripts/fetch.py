import psycopg2
from psycopg2.extensions import connection


def get_stock(conn: connection, symbol: str):
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT * FROM stocks WHERE symbol = %s
            """,
        (symbol.upper(), ))

    except Exception as e:
        return {'error': e}

    query_results = cur.fetchone()

    if query_results is None:
        return None

    result_dict = {
        "isin_number": query_results[0],
        "symbol": query_results[1],
        "name": query_results[2],
        "face_value": query_results[3],
        "market_cap": query_results[4],
        "eps": query_results[5],
        "ptbr": query_results[6],
        "per": query_results[7],
        "dividend_yield": query_results[8],
        "roe": query_results[9],
        "roce": query_results[10],
        "ev": query_results[11],
        "ipe": query_results[12],
        "pros": query_results[13].split('\n'),
        "cons": query_results[14].split('\n')
    }

    return result_dict