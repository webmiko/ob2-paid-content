# Подготовка ВМ

Целевая среда — Linux ВМ с Docker и Docker Compose v2.

## 1. Пакеты

```bash
sudo apt update
sudo apt install -y ca-certificates curl git ufw
# Docker Engine + Compose plugin — по официальной инструкции Docker
```

## 2. Пользователь deploy

```bash
sudo adduser deploy
sudo usermod -aG docker deploy
```

Скопируйте публичный SSH-ключ в `~deploy/.ssh/authorized_keys`.

## 3. Firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 4. Каталог проекта

```bash
sudo mkdir -p /opt/ob2-paid-content
sudo chown deploy:deploy /opt/ob2-paid-content
```

В GitHub Secret `DEPLOY_PATH` укажите `/opt/ob2-paid-content`.

## 5. Production `.env`

На сервере **один раз** (CI не перезаписывает):

```bash
cd /opt/ob2-paid-content
cp .env.production.example .env
nano .env
```

Обязательно заполните:

- `SECRET_KEY` — случайная строка ≥ 50 символов
- `ALLOWED_HOSTS` — IP/домен ВМ
- `SITE_URL`, `CORS_ALLOWED_ORIGINS`, Stripe URLs — ваш origin
- `DB_PASSWORD` — надёжный пароль
- `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`

При HTTP на :80 можно `USE_HTTPS=false`; за TLS-прокси — `USE_HTTPS=true`.

## 6. Системный nginx

Скрипт деплоя останавливает `systemd nginx`, если он занимает :80. Для prod используется контейнер `nginx` из Compose.

## 7. Первый запуск

После настройки Secrets запушьте в `main` или `develop` — CI выполнит deploy.

Или вручную на ВМ (если образ уже в Hub):

```bash
cd /opt/ob2-paid-content
export DOCKER_IMAGE=username/ob2-paid-content:latest
docker compose -f docker-compose.hub.yml pull web
docker compose -f docker-compose.hub.yml up -d db web nginx
curl -fsS http://127.0.0.1/api/health/
```

## 8. Диск

При нехватке места deploy выполняет `docker system prune -f` перед pull. Периодически проверяйте:

```bash
docker system df
df -h /
```

## 9. Логи и отладка

```bash
cd /opt/ob2-paid-content
docker compose -f docker-compose.hub.yml ps
docker compose -f docker-compose.hub.yml logs -f web
docker compose -f docker-compose.hub.yml logs -f nginx
```

502 после деплоя — дождитесь migrate в entrypoint и healthcheck `web`.
