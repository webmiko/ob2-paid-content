# Сборка SPA для nginx (docker compose up).
FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

ARG VITE_API_URL=
ARG VITE_SITE_URL=http://localhost
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_SITE_URL=$VITE_SITE_URL

RUN npm run build

CMD ["sh", "-c", "mkdir -p /dist && rm -rf /dist/* && cp -a /app/dist/. /dist/"]
