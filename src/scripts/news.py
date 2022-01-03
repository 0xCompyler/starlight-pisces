import requests
from bs4 import BeautifulSoup

import spacy
from spacytextblob.spacytextblob import SpacyTextBlob

import redis
from redis.client import Redis
import datetime
import json



def general(redis_client: Redis):
    cached_data = redis_client.get("news")
    if cached_data is not None:
        # print("[REDIS] Cache Hit")
        news_data = json.loads(cached_data)
        return news_data

    else:
        # print("[REDIS] Cache Miss")
        URL = "https://economictimes.indiatimes.com/markets/stocks/news"
        res = requests.get(URL)
        
        soup = BeautifulSoup(res.content, 'lxml')

        news_class = soup.find_all("div", {"class": "eachStory"})
        result_list = []
        
        nlp = spacy.load('en_core_web_sm')
        nlp.add_pipe('spacytextblob')

        for item in news_class:
            headline = item.find("h3").find("a").text
            link = item.find("h3").find("a", href=True)['href']
            link = URL + link
            para = item.find('p').text
            
            sentiment = nlp(para)._.polarity

            res_dict = {
                "headline": headline,
                "paragraph": para,
                "sentiment": sentiment,
                "link": link
            }
            
            result_list.append(res_dict)
        redis_client.setex("news", datetime.timedelta(seconds=10), json.dumps(result_list))
        return result_list


if __name__ == "__main__":
    print(general())

