#!/usr/bin/env bash
set -e

echo "=== Bootstrap script for FAST_USERNAME_AVAILABILITY_CHECK (macOS Apple Silicon) ==="

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker not found. Install Docker Desktop first."
  exit 1
fi
echo "Docker version: $(docker --version)"

osascript -e 'tell application "Docker" to activate' || true
echo "Waiting for Docker daemon..."
while ! docker info >/dev/null 2>&1; do
  sleep 2
done
echo "Docker is running."

docker compose up --build -d
echo "Services starting..."
sleep 20  # Bumped for stability

echo "Running seed..."
docker exec -it fast-username-service /bin/sh -c "python seed.py"

echo "Verifying sample present usernames..."
docker exec -it fast-username-service /bin/sh -c "python - << 'EOF'
from service.bloom_service import BloomService
present = [\"john123\", \"maria99\", \"alex_007\", \"peter1985\", \"linda_s\", \
\"robert01\", \"susanX\", \"mike2020\", \"anna_b\", \"david007\"]
b = BloomService()
for u in present:
    if b.is_definitely_absent(u):
        print('[ERROR] Bloom says absent for', u)
    else:
        print('OK for', u)
EOF
"

echo "Bootstrap complete. Open http://localhost:8000 in browser."