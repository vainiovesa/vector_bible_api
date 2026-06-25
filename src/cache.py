import os
import redis
from dotenv import load_dotenv


load_dotenv()


REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")


r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def store_embedding(key:str, embedding:list):
    r.set(key, str(embedding))


def get_embedding_from_cache(key:str):
    embedding_str = r.get(key)
    if embedding_str is not None:
        return eval(embedding_str)
