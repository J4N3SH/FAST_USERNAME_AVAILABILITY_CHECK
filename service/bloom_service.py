from redis import Redis
from redisbloom.client import Client as RedisBloomClient
from config import REDIS_HOST, REDIS_PORT, BLOOM_KEY, BLOOM_CAPACITY, BLOOM_ERROR_RATE

class BloomService:
    def __init__(self):
        self.redis = Redis(host=REDIS_HOST, port=REDIS_PORT)
        self.rb = RedisBloomClient(host=REDIS_HOST, port=REDIS_PORT)
        try:
            self.rb.bfCreate(BLOOM_KEY, BLOOM_ERROR_RATE, BLOOM_CAPACITY)
        except Exception:
            pass

    def is_definitely_absent(self, username: str) -> bool:
        exists = self.rb.bfExists(BLOOM_KEY, username)
        return (exists == 0)

    def add_username(self, username: str):
        self.rb.bfAdd(BLOOM_KEY, username)

    def info(self):
        return self.rb.bfInfo(BLOOM_KEY)