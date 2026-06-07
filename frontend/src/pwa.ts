import { registerSW } from "virtual:pwa-register";

/** Регистрация service worker (prod build). */
export function setupPwa(): void {
  registerSW({
    immediate: true,
    onOfflineReady() {
      console.info("[PWA] offline shell ready");
    },
    onNeedRefresh() {
      console.info("[PWA] new version available — reload to update");
    },
  });
}
