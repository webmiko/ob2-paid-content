import { useEffect, useState } from "react";

const DESKTOP_QUERY = "(min-width: 681px)";
/** У верхней границы страницы меню всегда видно. */
const TOP_ALWAYS_VISIBLE_PX = 72;
/** Сколько прокрутить вниз, чтобы спрятать (защита от случайного дёргания). */
const HIDE_AFTER_SCROLL_DOWN_PX = 20;
/** Сколько прокрутить вверх, чтобы показать снова. */
const SHOW_AFTER_SCROLL_UP_PX = 14;

function isDesktopViewport(): boolean {
  return typeof window !== "undefined" && window.matchMedia(DESKTOP_QUERY).matches;
}

export function useScrollAwareHeader(enabled: boolean): boolean {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    setVisible(true);
  }, [enabled]);

  useEffect(() => {
    if (!enabled || !isDesktopViewport()) {
      setVisible(true);
      return;
    }

    let lastScrollY = window.scrollY;
    let accumulatedDelta = 0;
    let ticking = false;

    const update = () => {
      ticking = false;
      const currentScrollY = window.scrollY;

      if (currentScrollY <= TOP_ALWAYS_VISIBLE_PX) {
        setVisible(true);
        accumulatedDelta = 0;
        lastScrollY = currentScrollY;
        return;
      }

      const delta = currentScrollY - lastScrollY;
      lastScrollY = currentScrollY;

      if (delta === 0) {
        return;
      }

      if (delta > 0) {
        if (accumulatedDelta < 0) {
          accumulatedDelta = 0;
        }
        accumulatedDelta += delta;
        if (accumulatedDelta >= HIDE_AFTER_SCROLL_DOWN_PX) {
          setVisible(false);
          accumulatedDelta = 0;
        }
        return;
      }

      if (accumulatedDelta > 0) {
        accumulatedDelta = 0;
      }
      accumulatedDelta += delta;
      if (accumulatedDelta <= -SHOW_AFTER_SCROLL_UP_PX) {
        setVisible(true);
        accumulatedDelta = 0;
      }
    };

    const onScroll = () => {
      if (!ticking) {
        ticking = true;
        window.requestAnimationFrame(update);
      }
    };

    const media = window.matchMedia(DESKTOP_QUERY);
    const onMediaChange = () => {
      if (!media.matches) {
        setVisible(true);
      }
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    media.addEventListener("change", onMediaChange);

    return () => {
      window.removeEventListener("scroll", onScroll);
      media.removeEventListener("change", onMediaChange);
    };
  }, [enabled]);

  return visible;
}
