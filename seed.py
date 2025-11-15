import random
import string
from redisbloom.client import Client as RedisBloomClient
from config import REDIS_HOST, REDIS_PORT, BLOOM_KEY, BLOOM_CAPACITY, BLOOM_ERROR_RATE

def gen_random_username(min_len=3, max_len=12):
    length = random.randint(min_len, max_len)
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def gen_common_name_variants(base_names, count_per_base=1000):
    variants = []
    for name in base_names:
        for i in range(count_per_base):
            suffix = ''.join(random.choice(string.digits) for _ in range(random.randint(1,4)))
            variants.append(name + suffix)
            variants.append(name + "_" + suffix)
            variants.append(name.capitalize() + suffix)
    return variants

def seed_usernames(total: int):
    # Define usernames to exclude (absent test usernames) to guarantee they remain absent
    absent_usernames = {
        "zebra2025", "quantum_fox", "mysticSky", "orbit99x",
        "nova_alpha", "xylon77", "echo_bravo", "phantom42", "aurora_9", "delta_star"
    }

    rb = RedisBloomClient(host=REDIS_HOST, port=REDIS_PORT)
    try:
        rb.bfCreate(BLOOM_KEY, BLOOM_ERROR_RATE, BLOOM_CAPACITY)
    except Exception:
        pass

    all_usernames = []

    common_bases = ["john", "alex", "maria", "peter", "linda", "robert", "susan", "mike", "anna", "david"]
    common_variants = gen_common_name_variants(common_bases, count_per_base=5000)
    num_common = 0
    for uname in common_variants:
        if uname in absent_usernames:
            continue
        all_usernames.append(uname)
        num_common += 1

    # Explicitly add test usernames to guarantee presence
    explicit_presents = ["john123", "maria99", "alex_007", "peter1985", "linda_s",
                         "robert01", "susanX", "mike2020", "anna_b", "david007"]
    num_explicit = 0
    for uname in explicit_presents:
        if uname in absent_usernames:
            continue
        if uname not in all_usernames:  # Avoid dups
            all_usernames.append(uname)
            num_explicit += 1
    print(f"Prepared {num_explicit} new test usernames (total present: {len(explicit_presents)})")

    remain = total - num_common - num_explicit
    if remain > 0:
        batch = 100000  # Large gen batches
        for start in range(0, remain, batch):
            end = min(remain, start + batch)
            for _ in range(end - start):
                uname = gen_random_username()
                if uname in absent_usernames:
                    continue
                all_usernames.append(uname)
            print(f"Generated random batch up to {len(all_usernames)}")

    # Bulk add via pipeline in chunks
    num_total = len(all_usernames)
    print(f"Adding {num_total} usernames to Bloom via pipeline chunks...")
    chunk_size = 50000  # Balance memory/network
    added = 0
    for i in range(0, num_total, chunk_size):
        chunk = all_usernames[i:i + chunk_size]
        pipe = rb.pipeline()
        for uname in chunk:
            pipe.bfAdd(BLOOM_KEY, uname)
        pipe.execute()
        added += len(chunk)
        print(f"Added chunk: {added}/{num_total}")
    print(f"Bulk added {num_total} to Bloom! (common: {num_common} + explicit: {num_explicit} + random: {num_total - num_common - num_explicit})")

if __name__ == "__main__":
    TOTAL = 2_000_000
    seed_usernames(TOTAL)