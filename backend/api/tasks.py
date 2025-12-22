from celery import shared_task
import requests
from backend.services.redis import get_redis_client
import uuid
from datetime import datetime

@shared_task
def get_book(book):
    url = f"https://openlibrary.org/search/authors.json?q={book}"
    resp = requests.get(url).json()

    redis = get_redis_client()
    pipe = redis.pipeline()

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
    return resp

@shared_task
def get_bible_verse():
    url = "https://bible-api.com/data/web/random"
    resp = requests.get(url).json()

    redis = get_redis_client()
    pipe = redis.pipeline()

    for verse in resp["random_verse"]["text"]:
        key = f"bible:{uuid.uuid4()}"
        pipe.hset(
            key,
            mapping={
                "source": "bible",
                "quote": verse,
                "timestamp": datetime.now().isoformat()
            }
        )

    pipe.execute()
    return resp
