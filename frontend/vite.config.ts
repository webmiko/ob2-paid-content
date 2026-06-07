import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";
import { VitePWA } from "vite-plugin-pwa";

const PWA_NAME = "Creavity";
const PWA_DESCRIPTION =
  "Creavity — публикации авторов: бесплатные материалы для всех, " +
  "платный контент по одной подписке на платформу.";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const apiTarget = env.VITE_DEV_API || "http://127.0.0.1:8000";
  const siteUrl = (env.VITE_SITE_URL || "http://localhost").replace(/\/+$/, "");

  return {
    plugins: [
      react(),
      VitePWA({
        registerType: "autoUpdate",
        includeAssets: ["favicon.svg", "og-default.svg", "pwa-192.png", "pwa-512.png"],
        manifest: {
          id: `${siteUrl}/`,
          name: PWA_NAME,
          short_name: PWA_NAME,
          description: PWA_DESCRIPTION,
          lang: "ru",
          dir: "ltr",
          start_url: "/",
          scope: "/",
          display: "standalone",
          orientation: "portrait-primary",
          theme_color: "#2563eb",
          background_color: "#ffffff",
          categories: ["education", "entertainment"],
          icons: [
            {
              src: "pwa-192.png",
              sizes: "192x192",
              type: "image/png",
            },
            {
              src: "pwa-512.png",
              sizes: "512x512",
              type: "image/png",
            },
            {
              src: "pwa-512.png",
              sizes: "512x512",
              type: "image/png",
              purpose: "maskable",
            },
          ],
        },
        workbox: {
          globPatterns: ["**/*.{js,css,html,ico,png,svg,woff2,webmanifest}"],
          navigateFallback: "/index.html",
          navigateFallbackDenylist: [
            /^\/api\//,
            /^\/admin\//,
            /^\/payments\//,
            /^\/media\//,
            /^\/robots\.txt$/,
            /^\/sitemap\.xml$/,
          ],
          runtimeCaching: [
            {
              urlPattern: /^https:\/\/cdnjs\.cloudflare\.com\/.*/i,
              handler: "CacheFirst",
              options: {
                cacheName: "cdn-fontawesome",
                expiration: {
                  maxEntries: 10,
                  maxAgeSeconds: 60 * 60 * 24 * 365,
                },
              },
            },
          ],
        },
        devOptions: {
          enabled: false,
        },
      }),
    ],
    server: {
      port: 5173,
      proxy: {
        "/api": { target: apiTarget, changeOrigin: true },
        "/admin": { target: apiTarget, changeOrigin: true },
        "/payments": { target: apiTarget, changeOrigin: true },
        "/robots.txt": { target: apiTarget, changeOrigin: true },
        "/sitemap.xml": { target: apiTarget, changeOrigin: true },
      },
    },
  };
});
