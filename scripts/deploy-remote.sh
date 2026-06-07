#!/usr/bin/env bash
# Деплой на ВМ: rsync кода + frontend/dist, pull образа web из Docker Hub, compose up.
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.hub.yml}"
FRONTEND_DIST_SOURCE="${FRONTEND_DIST_SOURCE:-frontend-dist}"
SSH_OPTS=(-o StrictHostKeyChecking=accept-new -o BatchMode=yes)

require_var() {
  if [[ -z "${!1:-}" ]]; then
    echo "Missing required env: $1" >&2
    exit 1
  fi
}

require_var SSH_PRIVATE_KEY
require_var SSH_USER
require_var SERVER_HOST
require_var DEPLOY_PATH
require_var DOCKER_IMAGE
require_var DOCKER_HUB_USERNAME
require_var DOCKER_HUB_TOKEN

REMOTE="${SSH_USER}@${SERVER_HOST}"
REMOTE_PATH="${DEPLOY_PATH}"

if [[ ! -d "${FRONTEND_DIST_SOURCE}" ]]; then
  echo "Frontend artifact not found: ${FRONTEND_DIST_SOURCE}" >&2
  exit 1
fi

SSH_KEY_FILE="$(mktemp)"
trap 'rm -f "${SSH_KEY_FILE}"' EXIT
printf '%s\n' "${SSH_PRIVATE_KEY}" > "${SSH_KEY_FILE}"
chmod 600 "${SSH_KEY_FILE}"

RSYNC_RSH="ssh -i ${SSH_KEY_FILE} -o StrictHostKeyChecking=accept-new -o BatchMode=yes"
SSH_CMD=(ssh -i "${SSH_KEY_FILE}" -o StrictHostKeyChecking=accept-new -o BatchMode=yes)

echo "==> Rsync project to ${REMOTE}:${REMOTE_PATH}"
rsync -az --delete \
  --exclude '.git/' \
  --exclude '.env' \
  --exclude '.venv/' \
  --exclude 'media/' \
  --exclude 'frontend/node_modules/' \
  --exclude 'frontend/dist/' \
  -e "${RSYNC_RSH}" \
  ./ "${REMOTE}:${REMOTE_PATH}/"

echo "==> Rsync frontend dist"
"${SSH_CMD[@]}" "${REMOTE}" "mkdir -p '${REMOTE_PATH}/frontend/dist'"
rsync -az --delete \
  -e "${RSYNC_RSH}" \
  "${FRONTEND_DIST_SOURCE}/" "${REMOTE}:${REMOTE_PATH}/frontend/dist/"

echo "==> Remote deploy (prune, pull, up, health)"
"${SSH_CMD[@]}" "${REMOTE}" bash -s <<EOF
set -euo pipefail
cd '${REMOTE_PATH}'

if systemctl is-active --quiet nginx 2>/dev/null; then
  sudo systemctl stop nginx || true
  sudo systemctl disable nginx || true
fi

docker system prune -f || true

printf '%s' '${DOCKER_HUB_TOKEN}' | docker login -u '${DOCKER_HUB_USERNAME}' --password-stdin

export DOCKER_IMAGE='${DOCKER_IMAGE}'
docker compose -f '${COMPOSE_FILE}' pull web
docker compose -f '${COMPOSE_FILE}' up -d db web

for attempt in \$(seq 1 40); do
  if docker compose -f '${COMPOSE_FILE}' ps web 2>/dev/null | grep -q '(healthy)'; then
    echo "Web container healthy"
    break
  fi
  sleep 3
done

docker compose -f '${COMPOSE_FILE}' up -d --force-recreate nginx

for attempt in \$(seq 1 40); do
  if curl -fsS http://127.0.0.1/api/health/ >/dev/null; then
    echo "Health OK"
    curl -fsS http://127.0.0.1/api/health/
    exit 0
  fi
  sleep 3
done

echo "Health check failed after deploy" >&2
docker compose -f '${COMPOSE_FILE}' logs --tail=80 web nginx
exit 1
EOF

echo "==> Deploy finished"
