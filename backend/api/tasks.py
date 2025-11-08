from celery import shared_task
import requests

@shared_task
def get_book(book):
    url = f"https://openlibrary.org/search/authors.json?q={book}"
    resp = requests.get(url)
    return resp.json()

@shared_task
def get_bible_verse():
    url = f"https://bible-api.com/data/web/random"
    resp = requests.get(url)
    return resp.json()