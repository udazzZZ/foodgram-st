import sys
import redis
import json
import os

sys.path.insert(0, '/app')

from redis.commands.search.field import TextField, TagField
from redis.commands.search.index_definition import IndexDefinition, IndexType


class Redis:
    _client = None

    def __init__(self):
        if Redis._client is None:
            Redis._client = self._create_client()

        self.redis = Redis._client

    def _create_client(self):
        return redis.Redis(
            host=os.getenv("APP_REDIS_HOST"),
            port=int(os.getenv("APP_REDIS_PORT")),
            decode_responses=True
        )

    def create_index(self):
        try:
            self.redis.ft("idx_docs").create_index(
                fields=[
                    TextField("top_work"),
                    TextField("author"),
                    TextField("verse"),
                    TagField("source"),
                ],
                definition=IndexDefinition(
                    prefix=["library:", "bible:"],
                    index_type=IndexType.HASH
                )
            )
            print("Redis index created")
        except Exception as e:
            print("Index create skipped:", e)

    def make_cache_key(self, prefix, **params):
        parts = [prefix] + [f"{k}:{v}" for k, v in sorted(params.items())]
        return "|".join(parts)

    def cache_get(self, key):
        data = self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    def cache_set(self, key, value, ttl=86400):
        self.redis.set(key, json.dumps(value), ex=ttl)