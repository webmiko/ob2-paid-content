# Frontend (React SPA)

Каталог: [`frontend/`](../frontend/).

## Dev

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

- UI: http://localhost:5173  
- `/api/*` проксируется на Django (см. `vite.config.ts`)

## Production build

```bash
cd frontend
VITE_API_URL= VITE_SITE_URL=https://your-domain npm run build
```

- `VITE_API_URL=""` — относительные запросы `/api/` через nginx  
- `VITE_SITE_URL` — canonical и Open Graph (задаётся при сборке, не в runtime)

Артефакт: `frontend/dist/` → nginx `root`.

## Docker Compose (локально)

Сервис `frontend` собирает dist в volume `./frontend/dist`, затем `nginx` отдаёт static.

```bash
docker compose up --build frontend nginx
```

## CI

Job **build** выполняет `npm ci && npm run build`, загружает artifact `frontend-dist`.  
Job **deploy** rsync dist на ВМ в `frontend/dist/`.

На production ВМ сервис `frontend` **не** запускается — используется `docker-compose.hub.yml` только с `db`, `web`, `nginx`.

## SEO

Meta-теги обновляются в SPA через `PageMeta` / `usePageMeta`.  
`sitemap.xml` и `robots.txt` — Django (`/sitemap.xml`, `/robots.txt`), прокси через nginx.

Подробнее — [ci-cd.md](ci-cd.md).
