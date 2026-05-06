#!/bin/bash
# ============================================================
# Campus Resource Platform — One-shot VPS Deployment
# Usage on VPS:
#   cd /opt/campus_resource_platform/backend
#   bash deploy.sh
# ============================================================
set -euo pipefail

cd "$(dirname "$0")"

echo "==> Step 1/6: Verifying Docker is installed..."
if ! command -v docker &> /dev/null; then
  echo "Docker not found. Installing via official script (auto-detects OS)..."
  curl -fsSL https://get.docker.com | sh
  systemctl enable --now docker
fi

if ! docker compose version &> /dev/null; then
  echo "Docker Compose v2 plugin missing. Installing..."
  if command -v dnf &> /dev/null; then
    dnf install -y docker-compose-plugin || \
      (curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
         -o /usr/local/lib/docker/cli-plugins/docker-compose && \
       chmod +x /usr/local/lib/docker/cli-plugins/docker-compose)
  elif command -v apt-get &> /dev/null; then
    apt-get update && apt-get install -y docker-compose-plugin
  fi
fi

echo "==> Step 2/6: Checking .env file..."
if [ ! -f .env ]; then
  echo "Creating .env from .env.example with random passwords..."
  cp .env.example .env
  sed -i "s|replace_me_with_strong_random_pw|$(openssl rand -hex 16)|g" .env
  sed -i "s|replace_me_with_64_random_hex_chars|$(openssl rand -hex 32)|g" .env
  echo ".env created. Review with: cat .env"
fi

echo "==> Step 3/6: Building API image (this takes ~2 minutes first time)..."
docker compose build

echo "==> Step 4/6: Starting services (db + api)..."
docker compose up -d
sleep 5

echo "==> Step 5/6: Waiting for DB to become healthy (max 60s)..."
for i in {1..30}; do
  if docker compose ps | grep -q "campus_db.*healthy"; then
    echo "Database is healthy."
    break
  fi
  echo "  Waiting for db... ($i/30)"
  sleep 2
done

echo "==> Step 6/6: Seeding initial data (idempotent)..."
docker compose exec api python -m app.seed

echo ""
echo "✅ DEPLOYMENT COMPLETE"
echo ""
echo "==== Verify ===="
echo "  docker compose ps"
echo "  docker compose logs api --tail=20"
echo "  curl http://localhost:8000/health"
echo ""
echo "==== API access ===="
echo "  Swagger UI:    http://YOUR_VPS_IP/docs   (after nginx setup)"
echo "  Health check:  http://YOUR_VPS_IP/health"
echo ""
echo "==== Login (seeded user) ===="
echo "  Student ID:    1230020693"
echo "  Password:      demo123"
echo "  This account is also Admin (for upload approval)."
echo ""
echo "==== Memory used ===="
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}"
