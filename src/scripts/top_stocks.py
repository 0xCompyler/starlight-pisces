import requests
import json

from requests.exceptions import HTTPError
import logging

logging.basicConfig(level=logging.DEBUG)

def performance(index: str):
    URL = f"https://www.nseindia.com/api/live-analysis-variations?index={index}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    }
    try:
        res = requests.get(URL, headers=headers).json()
        
    except Exception as e:
        logging.error(f"Error while sending request: {e}")
        return {"error": e}

    stocks = res['NIFTY']['data']
    result_list = []

    for stock in stocks:
        temp_dict = {
            "symbol": stock['symbol'],
            "open": stock['open_price'],
            "high": stock['high_price'],
            "prev": stock['prev_price'],
            "prec": stock['perChange']
        }    

        result_list.append(temp_dict)


    # logging.info(f"{result_list}")
    logging.debug(f"{result_list=}")
    return result_list


if __name__ == '__main__':
    print(performance('gainers'))
