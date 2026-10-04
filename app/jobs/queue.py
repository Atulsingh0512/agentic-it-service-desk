import os

import redis
from dotenv import load_dotenv
from rq import Queue


load_dotenv()


REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379/0"
)


redis_connection = redis.from_url(
    REDIS_URL
)


agent_queue = Queue(
    "agent_tasks",
    connection=redis_connection,
    default_timeout=600
)


def check_redis_connection():
    return redis_connection.ping()