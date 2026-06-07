#!/usr/bin/env bash
# Освобождение места на ВМ: Docker-кэш и старые образы (volumes БД/media не трогаем).
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.hub.yml}"
DEPLOY_PATH="${DEPLOY_PATH:-/opt/ob2-paid-content}"

echo "==> Disk before cleanup"
df -h /
docker system df 2>/dev/null || true

if [[ -d "${DEPLOY_PATH}" ]]; then
  cd "${DEPLOY_PATH}"
  docker compose -f "${COMPOSE_FILE}" stop web nginx 2>/dev/null || true
fi

docker container prune -f 2>/dev/null || true
docker builder prune -af 2>/dev/null || true
docker image prune -af 2>/dev/null || true
docker network prune -f 2>/dev/null || true
docker system prune -af 2>/dev/null || true

if command -v journalctl >/dev/null 2>&1; then
  sudo journalctl --vacuum-size=100M 2>/dev/null || true
fi

echo "==> Disk after cleanup"
df -h /
docker system df 2>/dev/null || true
