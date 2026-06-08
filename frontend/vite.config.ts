import react from "@vitejs/plugin-react";
import type { IndexHtmlTransformContext, Plugin } from "vite";
import { defineConfig, loadEnv } from "vite";
import { VitePWA } from "vite-plugin-pwa";

/** Preload Font Awesome woff2 — меньше сдвига иконок при первой отрисовке. */
function preloadFaFontPlugin(): Plugin {
  return {
    name: "preload-fa-font",
    apply: "build",
    transformIndexHtml: {
      order: "post",
      handler(html: string, ctx: IndexHtmlTransformContext) {
        const bundle = ctx.bundle;
        if (!bundle) {
          return html;
        }
        const asset = Object.keys(bundle).find(
          (name) => name.includes("fa-solid") && name.endsWith(".woff2"),
        );
        if (!asset) {
          return html;
        }
        const href = asset.startsWith("/") ? asset : `/${asset}`;
        const tag =
          `<link rel="preload" href="${href}" as="font" type="font/woff2" crossorigin>`;
        return html.replace("</head>", `    ${tag}\n  </head>`);
      },
    },
  };
}

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
      preloadFaFontPlugin(),
      VitePWA({
        registerType: "autoUpdate",
        includeAssets: ["favicon.svg", "og-default.svg", "pwa-192.png", "pwa-512.png", "theme-init.js", "feed-prefetch.js"],
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
          runtimeCaching: [],
        },
        devOptions: {
          enabled: false,
        },
      }),
    ],
    build: {
      rollupOptions: {
        output: {
          manualChunks: {
            "vendor-router": ["react-router-dom"],
          },
        },
      },
    },
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
    preview: {
      port: 4173,
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
