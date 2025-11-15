import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

BLOOM_KEY = "usernames_bloom_filter"
BLOOM_CAPACITY = 28_755_279  # Optimal: ~3.6 MB RAM for 2M items, 0.1% error
BLOOM_ERROR_RATE = 0.001     # 0.1% false positives (1 in 1,000)

DB_URL = os.getenv("DB_URL", "sqlite:///users.db")