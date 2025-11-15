import requests

BASE = "http://localhost:8000"

present_usernames = [
    "john123", "maria99", "alex_007", "peter1985", "linda_s",
    "robert01", "susanX", "mike2020", "anna_b", "david007"
]
absent_usernames = [
    "zebra2025", "quantum_fox", "mysticSky", "orbit99x",
    "nova_alpha", "xylon77", "echo_bravo", "phantom42", "aurora_9", "delta_star"
]

def test_present_usernames_unavailable():
    for u in present_usernames:
        resp = requests.get(f"{BASE}/username_available", params={"username": u})
        j = resp.json()
        assert j.get("available") is False, f"{u} should be unavailable"

def test_absent_usernames_available():
    for u in absent_usernames:
        resp = requests.get(f"{BASE}/username_available", params={"username": u})
        j = resp.json()
        assert j.get("available") is True, f"{u} should be available"

def test_register_and_then_check():
    testname = "someNewUserX123"
    resp = requests.get(f"{BASE}/username_available", params={"username": testname})
    assert resp.json().get("available") is True

    resp2 = requests.post(f"{BASE}/register", json={"username": testname})
    assert resp2.status_code == 200

    resp3 = requests.get(f"{BASE}/username_available", params={"username": testname})
    assert resp3.json().get("available") is False

def test_register_existing_fails():
    u = present_usernames[0]
    resp = requests.post(f"{BASE}/register", json={"username": u})
    assert resp.status_code != 200