import { useEffect, useRef, type ReactNode } from "react";

const BLOCKED_KEYS = new Set(["c", "x", "a", "p", "s", "u"]);

interface PaidContentGuardProps {
  enabled: boolean;
  watermark?: string;
  children: ReactNode;
}

/** Ограничивает копирование и сохранение платного контента в браузере. */
export default function PaidContentGuard({ enabled, watermark, children }: PaidContentGuardProps) {
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!enabled) {
      return;
    }
    const root = rootRef.current;
    if (!root) {
      return;
    }

    const blockEvent = (event: Event) => {
      event.preventDefault();
    };

    const onKeyDown = (event: KeyboardEvent) => {
      if (!(event.ctrlKey || event.metaKey)) {
        return;
      }
      const target = event.target;
      if (target instanceof HTMLElement && target.closest('input, textarea, select, [contenteditable="true"]')) {
        return;
      }
      if (!root.contains(target as Node)) {
        return;
      }
      if (BLOCKED_KEYS.has(event.key.toLowerCase())) {
        event.preventDefault();
      }
    };

    root.addEventListener("copy", blockEvent);
    root.addEventListener("cut", blockEvent);
    root.addEventListener("contextmenu", blockEvent);
    root.addEventListener("dragstart", blockEvent);
    document.addEventListener("keydown", onKeyDown);

    return () => {
      root.removeEventListener("copy", blockEvent);
      root.removeEventListener("cut", blockEvent);
      root.removeEventListener("contextmenu", blockEvent);
      root.removeEventListener("dragstart", blockEvent);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [enabled]);

  if (!enabled) {
    return <>{children}</>;
  }

  return (
    <div
      ref={rootRef}
      className="paid-content-guard"
      data-watermark={watermark}
      onCopy={(event) => event.preventDefault()}
      onCut={(event) => event.preventDefault()}
      onContextMenu={(event) => event.preventDefault()}
    >
      {watermark && (
        <span className="paid-content-watermark" aria-hidden="true">
          {watermark}
        </span>
      )}
      <div className="paid-content-guard-body">{children}</div>
    </div>
  );
}
