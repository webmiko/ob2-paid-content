/** Скрытие приветственного экрана из index.html после монтирования React. */

const SPLASH_ID = "app-splash";
const WELCOME_SEEN_KEY = "creavity-welcome-seen";
const HIDE_MS = 420;

/** Убирает overlay-заставку с короткой анимацией. */
export function dismissAppSplash(): void {
  const splash = document.getElementById(SPLASH_ID);
  if (!splash) {
    return;
  }

  if (!localStorage.getItem(WELCOME_SEEN_KEY)) {
    localStorage.setItem(WELCOME_SEEN_KEY, "1");
  }

  splash.classList.add("app-splash--hidden");
  const remove = () => splash.remove();
  splash.addEventListener("transitionend", remove, { once: true });
  window.setTimeout(remove, HIDE_MS);
}

/** Даёт браузеру отрисовать заставку, затем скрывает после первого кадра приложения. */
export function scheduleSplashDismiss(): void {
  requestAnimationFrame(() => {
    requestAnimationFrame(dismissAppSplash);
  });
}
