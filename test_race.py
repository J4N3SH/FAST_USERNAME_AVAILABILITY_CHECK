import requests
from concurrent.futures import ThreadPoolExecutor
import time

BASE = "http://localhost:8000"
username = "testrace"  # Free username

def register_user(user_id):
    try:
        resp = requests.post(
            f"{BASE}/register",
            json={"username": username},
            headers={"Content-Type": "application/json"},
            timeout=1  # 1s timeout for quick fail
        )
        print(f"User {user_id}: Status {resp.status_code}")
        print(f"User {user_id}: Response {resp.json() if resp.status_code == 200 else resp.text}")
    except Exception as e:
        print(f"User {user_id}: Error {e}")

# Simulate 2 concurrent users
with ThreadPoolExecutor(max_workers=2) as executor:
    start_time = time.time()
    futures = [executor.submit(register_user, i) for i in range(1, 3)]  # User 1 & 2
    for future in futures:
        future.result()  # Wait for completion
end_time = time.time()
print(f"Total time: {end_time - start_time:.3f}s")