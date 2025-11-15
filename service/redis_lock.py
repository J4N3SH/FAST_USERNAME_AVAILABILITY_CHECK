from redis import Redis
from config import REDIS_HOST, REDIS_PORT

class RedisLock:
    def __init__(self):
        self.r = Redis(host=REDIS_HOST, port=REDIS_PORT)
    
    def atomic_register(self, username: str, ttl=0.1):  # TTL in seconds
        key = f"lock:{username}"
        ttl_ms = int(ttl * 1000)  # Convert to milliseconds for PX
        script = """
        if redis.call('EXISTS', KEYS[1]) == 0 then
            redis.call('SET', KEYS[1], ARGV[1], 'PX', ARGV[2])  -- Set lock if free (PX for ms)
            return 1  -- Success - proceed to DB/Bloom
        else
            return 0  -- Locked - retry or fail
        end
        """
        lua = self.r.register_script(script)
        return lua(keys=[key], args=[1, ttl_ms])  # 1 = lock value, ttl_ms = int