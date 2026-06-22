import { registerSW } from "virtual:pwa-register";

/** Регистрация service worker (prod build). */
export function setupPwa(): void {
  const updateSW = registerSW({
    immediate: true,
    onOfflineReady() {
      console.info("[PWA] offline shell ready");
    },
    onNeedRefresh() {
      void updateSW(true);
    },
  });
}
