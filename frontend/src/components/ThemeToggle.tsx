import { useTheme } from "../context/ThemeContext";
import type { ThemePreference } from "../theme/theme";

const LABELS: Record<ThemePreference, string> = {
  auto: "Авто: как в системе устройства",
  light: "Светлая тема",
  dark: "Тёмная тема",
};

const ICONS: Record<ThemePreference, string> = {
  auto: "fa-circle-half-stroke",
  light: "fa-sun",
  dark: "fa-moon",
};

export default function ThemeToggle() {
  const { preference, cyclePreference } = useTheme();

  return (
    <button
      type="button"
      className="theme-toggle btn-pill btn-sm-pill btn-pill-secondary"
      onClick={cyclePreference}
      aria-label={LABELS[preference]}
      title={LABELS[preference]}
    >
      <span className="theme-toggle-text">Тема:</span>
      <i className={`fa-solid ${ICONS[preference]}`} aria-hidden="true" />
    </button>
  );
}
