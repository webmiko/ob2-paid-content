#!/usr/bin/env bash
# Запуск server-disk-cleanup.sh на ВМ по SSH (те же secrets, что у deploy).
set -euo pipefail

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

REMOTE="${SSH_USER}@${SERVER_HOST}"
SSH_KEY_FILE="$(mktemp)"
trap 'rm -f "${SSH_KEY_FILE}"' EXIT
printf '%s\n' "${SSH_PRIVATE_KEY}" > "${SSH_KEY_FILE}"
chmod 600 "${SSH_KEY_FILE}"

RSYNC_RSH="ssh -i ${SSH_KEY_FILE} -o StrictHostKeyChecking=accept-new -o BatchMode=yes"

echo "==> Rsync cleanup script to ${REMOTE}"
rsync -az -e "${RSYNC_RSH}" scripts/server-disk-cleanup.sh "${REMOTE}:${DEPLOY_PATH}/scripts/"

echo "==> Run cleanup on ${REMOTE}"
ssh -i "${SSH_KEY_FILE}" -o StrictHostKeyChecking=accept-new -o BatchMode=yes "${REMOTE}" bash -s <<EOF
set -euo pipefail
chmod +x '${DEPLOY_PATH}/scripts/server-disk-cleanup.sh'
DEPLOY_PATH='${DEPLOY_PATH}' '${DEPLOY_PATH}/scripts/server-disk-cleanup.sh'
EOF

echo "==> Cleanup finished"
