import { useEffect, useState } from "react";

const DESKTOP_QUERY = "(min-width: 681px)";
/** После этой прокрутки появляется плавающее меню (статичное остаётся на месте). */
export const FLOATING_NAV_ACTIVATE_PX = 300;
const HIDE_AFTER_SCROLL_DOWN_PX = 20;
const SHOW_AFTER_SCROLL_UP_PX = 14;

function isDesktopViewport(): boolean {
  return typeof window !== "undefined" && window.matchMedia(DESKTOP_QUERY).matches;
}

export interface FloatingNavState {
  /** Прокрутка прошла порог — плавающее меню может показываться. */
  active: boolean;
  /** В зоне активности: видимо или спрятано по направлению прокрутки. */
  visible: boolean;
}

export function useFloatingNav(enabled: boolean): FloatingNavState {
  const [active, setActive] = useState(false);
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    setActive(false);
    setVisible(true);
  }, [enabled]);

  useEffect(() => {
    if (!enabled || !isDesktopViewport()) {
      setActive(false);
      setVisible(true);
      return;
    }

    let lastScrollY = window.scrollY;
    let accumulatedDelta = 0;
    let ticking = false;

    const update = () => {
      ticking = false;
      const currentScrollY = window.scrollY;

      if (currentScrollY <= FLOATING_NAV_ACTIVATE_PX) {
        setActive(false);
        setVisible(true);
        accumulatedDelta = 0;
        lastScrollY = currentScrollY;
        return;
      }

      setActive(true);

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
        setActive(false);
        setVisible(true);
      }
    };

    update();
    window.addEventListener("scroll", onScroll, { passive: true });
    media.addEventListener("change", onMediaChange);

    return () => {
      window.removeEventListener("scroll", onScroll);
      media.removeEventListener("change", onMediaChange);
    };
  }, [enabled]);

  return { active, visible };
}
