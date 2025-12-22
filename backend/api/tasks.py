from celery import shared_task
import requests
from services.redis import Redis
import uuid
from datetime import datetime

redis_client = Redis()

@shared_task
def get_book(book):
    cache_key = redis_client.make_cache_key("book_author", book=book)
    cached = redis_client.cache_get(cache_key)
    if cached:
        return cached

    url = f"https://openlibrary.org/search/authors.json?q={book}"
    resp = requests.get(url).json()

    pipe = redis_client.redis.pipeline()

    for item in resp["docs"]:
        key = f"library:{uuid.uuid4()}"
        pipe.hset(
            key,
            mapping={
                "source": "library",
                "author": item["name"],
                "top_work": item["top_work"],
                "timestamp": datetime.now().isoformat()
            }
        )

    pipe.execute()
    redis_client.cache_set(cache_key, resp)
    return resp

@shared_task
def get_bible_verse():
    cache_key = redis_client.make_cache_key("bible_verse")
    cached = redis_client.cache_get(cache_key)
    if cached:
        return cached

    url = "https://bible-api.com/data/web/random"
    resp = requests.get(url).json()

    pipe = redis_client.redis.pipeline()

    key = f"bible:{uuid.uuid4()}"
    pipe.hset(
        key,
        mapping={
            "source": "bible",
            "quote": resp["random_verse"]["text"],
            "timestamp": datetime.now().isoformat()
        }
    )

    pipe.execute()
    redis_client.cache_set(cache_key, resp)
    return resp
