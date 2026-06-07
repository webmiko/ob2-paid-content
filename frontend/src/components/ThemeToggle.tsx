import { useTheme } from "../context/ThemeContext";
import type { ThemePreference } from "../theme/solar";

const LABELS: Record<ThemePreference, string> = {
  auto: "Авто: день и ночь по рассвету и закату",
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
      <i className={`fa-solid ${ICONS[preference]}`} aria-hidden="true" />
      <span className="theme-toggle-label">{preference === "auto" ? "Авто" : null}</span>
    </button>
  );
}
