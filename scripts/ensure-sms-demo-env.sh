#!/usr/bin/env bash
# Включает демо-код SMS в production .env (без внешнего SMS-провайдера).
set -euo pipefail

ENV_FILE="${1:-.env}"
VAR_NAME="SMS_SHOW_CODE_IN_RESPONSE"
VAR_VALUE="true"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Skip ${VAR_NAME}: ${ENV_FILE} not found" >&2
  exit 0
fi

if grep -q "^${VAR_NAME}=" "${ENV_FILE}"; then
  sed -i "s/^${VAR_NAME}=.*/${VAR_NAME}=${VAR_VALUE}/" "${ENV_FILE}"
  echo "Updated ${VAR_NAME}=${VAR_VALUE} in ${ENV_FILE}"
else
  {
    echo ""
    echo "# Имитация SMS без провайдера: код в ответе API и на экране регистрации"
    echo "${VAR_NAME}=${VAR_VALUE}"
  } >> "${ENV_FILE}"
  echo "Appended ${VAR_NAME}=${VAR_VALUE} to ${ENV_FILE}"
fi
