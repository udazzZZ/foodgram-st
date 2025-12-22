from django.apps import AppConfig
import sys

sys.path.insert(0, '/app')

from services.redis import Redis

class ServicesConfig(AppConfig):
    name = "services"

    def ready(self):
        redis = Redis()
        redis.create_index()