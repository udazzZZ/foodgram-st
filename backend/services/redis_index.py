from redis.commands.search.field import TextField, TagField
from redis.commands.search.index_definition import IndexDefinition, IndexType
import sys

sys.path.insert(0, '/app')

from backend.services.redis import get_redis_client

def create_redis_index():
    try:
        redis = get_redis_client()
        redis.ft("idx_docs").create_index(
            fields=[
                TextField("top_work"),
                TextField("author"),
                TextField("verse"),
                TagField("source"),
            ],
            definition=IndexDefinition(prefix=["library:", "bible:"], index_type=IndexType.HASH)
        )
    except Exception as e:
        print("Index may already exist:", e)