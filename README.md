# FAST_USERNAME_AVAILABILITY_CHECK

[![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)](https://www.docker.com/) [![FastAPI](https://img.shields.io/badge/FastAPI-Modern%20API-yellow?logo=fastapi)](https://fastapi.tiangolo.com/) [![Redis](https://img.shields.io/badge/Redis-Bloom%20Filter-red?logo=redis)](https://redis.io/docs/stack/bloom/) [![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen)](https://pytest.org/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A lightning-fast username checker and registrar using a probabilistic Bloom filter in Redis to skip database lookups—checks in microseconds, scales to billions. UI for easy testing, API for apps, Docker for one-click setup. Tests pass, seeded with 2M fakes for realism.


## 🎯 Quick Overview
- **Problem Solved**: Traditional apps query the full DB for every username check—slow, costly at scale (e.g., Twitter's 500M users).
- **Your Hack**: Bloom filter acts as a "quick no" gatekeeper: Hashes names to say "probably taken" without DB touch. False alarms? DB confirms on register.
- **Why Fast?** 99% checks = <20ms (Bloom only). Registers = safe DB write. Seed 2M in 30s via pipelined adds.
- **Demo Flow**: Check "john123" (taken via Bloom), register "newbie42" (succeeds, adds to DB/Bloom).

Clone, bootstrap, play—see the speed yourself!

## 📦 Features
- **UI/API Dual**: Simple HTML forms + JSON endpoints (GET /username_available, POST /register).
- **Probabilistic Power**: RedisBloom for "definitely absent" guarantees—no false frees, 0.1% false takens.
- **Persistence**: SQLite for claims (unique constraint blocks dups); swap for Postgres easily.
- **Docker-Ready**: One script spins Redis + web, auto-seeds/tests.
- **Tested**: 4 pytest cases (presents/absents/register flows)—100% green.
- **Scale-Ready**: Bloom tuned for 28.8M bits (optimal for 2M+ items); add Redis cluster for prod.
- **Race Condition Safe**: Atomic Redis locks prevent concurrent registrations for the same username (1 retry for resilience).

## 🚀 Getting Started (5 Mins)
### Prerequisites
- **macOS Apple Silicon**: Docker Desktop (enable Rosetta for x86 emulation if needed).
- Optional: Python 3.9+ for local edits.

### Installation
1. Clone the repo:
   ```
   git clone https://github.com/J4N3SH/FAST_USERNAME_AVAILABILITY_CHECK.git
   cd FAST_USERNAME_AVAILABILITY_CHECK
   ```

2. Bootstrap (builds, starts, seeds 2M usernames):
   ```
   chmod +x bootstrap_mac.sh
   ./bootstrap_mac.sh
   ```
   - Wait ~30s for seed. Outputs "Bootstrap complete."

3. Open UI: [http://localhost:8000](http://localhost:8000)  
   - Check "john123" → ❌ Taken. Register "testuser99" → 🎉 Yours!

### API Examples
```bash
# Check availability
curl "http://localhost:8000/username_available?username=test"

# Register (JSON)
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser99"}'
```

### Run Tests
```
docker exec -it fast-username-service pytest tests/test_username_checks.py -v
```
All 4 pass? You're good.

### Inspect/Stop
- Bloom stats: `docker exec -it redis-stack redis-cli BF.INFO usernames_bloom_filter`
- Shutdown: `docker compose down` (keeps Redis data).

## 🔧 Architecture (The Speed Secret)
1. **User Request**: UI/API hits FastAPI route.
2. **Bloom Check** (<20ms): RedisBloom hashes username → "Absent?" (math guarantee: No false frees).
3. **Register (If Free)**: Atomic Redis lock (1 retry) → DB insert (SQLite) + Bloom add. Dup? 400 error.
4. **No DB on Checks**: 99% traffic skips it—Bloom's probabilistic sketch (tiny memory) handles the load.

**Analogy**: Party bouncer (Bloom) scans IDs at door—no full guest list (DB) unless you enter. Lock = "reserved sign" for claims.

## 📊 Performance Highlights
- **Checks**: <20ms (Bloom hash vs. 100-500ms DB query).
- **Seed**: 2M in 30s 
- **Memory**: Bloom ~3.6MB for 28.8M bits (optimal for 2M items, vs. GBs for full list).
- **Load Test**: 1M checks/day? Pennies in Redis RAM.

## 🤝 Contributing
1. Fork the repo.
2. Create branch: `git checkout -b feat/your-feature`.
3. Commit: `git commit -m "Add your feature"`.
4. Push: `git push origin feat/your-feature`.
5. Open PR—I'll review!

Issues? Open one. Ideas? Ping me.

## 📄 License
MIT License—see [LICENSE](LICENSE) for details. Free to fork, modify, deploy.

## 🙏 Acknowledgments
- **Tech**: FastAPI (tiangolo), RedisBloom (Redis Labs), Docker.
- **Inspo**: Probabilistic structures for scale (e.g., Google's early tricks).
- **Built By**: Janesh

