# CI/CD

Pipeline: **test → lint → build → deploy** (файл [`.github/workflows/ci-cd.yml`](../.github/workflows/ci-cd.yml)).

## Jobs

| Job | Когда | Действия |
|-----|-------|----------|
| **test** | push, PR | Postgres 16, `poetry install`, migrate, `pytest` (coverage ≥ 85 %) |
| **lint** | после test | `ruff check`, `ruff format --check`, `mypy config users posts` |
| **build** | после lint | `npm ci && npm run build` → artifact `frontend-dist`; push образа `web` в Docker Hub |
| **deploy** | push `main` / `develop` | rsync + dist, `docker compose -f docker-compose.hub.yml up` |

## GitHub Secrets

| Secret | Назначение |
|--------|------------|
| `DOCKER_HUB_USERNAME` | Логин Docker Hub |
| `DOCKER_HUB_TOKEN` | Access token Hub |
| `SSH_PRIVATE_KEY` | Приватный ключ для деплоя (PEM, без passphrase) |
| `SSH_USER` | Пользователь на ВМ (например `deploy`) |
| `SERVER_HOST` | IP или домен ВМ |
| `DEPLOY_PATH` | Каталог проекта на сервере (например `/opt/ob2-paid-content`) |

## GitHub Variables (опционально)

| Variable | Назначение |
|----------|------------|
| `SITE_URL` | Публичный URL для `VITE_SITE_URL` при сборке SPA в CI |

## Проверка после деплоя

```bash
curl -fsS http://<SERVER_HOST>/api/health/
docker compose -f docker-compose.hub.yml logs --tail=50 web nginx
```

## Локальная проверка команд CI

```bash
poetry install
poetry run ruff check .
poetry run ruff format --check .
poetry run mypy config users posts
DB_NAME=ob2_paid_content DB_HOST=localhost DB_PORT=5433 DB_USER=postgres DB_PASSWORD=postgres \
  poetry run pytest
cd frontend && npm ci && npm run build
```

## Безопасность

- Секреты не печатаются в логах workflow.
- `.env` на сервере **не** перезаписывается rsync (exclude).
- Deploy только с protected branches `main` и `develop`.
- SSH: `StrictHostKeyChecking=accept-new`.

## Ручной деплой с runner

Скачайте artifact `frontend-dist`, затем:

```bash
export FRONTEND_DIST_SOURCE=./frontend-dist
export DOCKER_IMAGE=user/ob2-paid-content:tag
# + SSH_* , DEPLOY_PATH, DOCKER_HUB_*
./scripts/deploy-remote.sh
```

Подробнее о подготовке ВМ — [servers.md](servers.md).
