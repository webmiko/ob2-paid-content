/** Аватар и отображение имени пользователя в интерфейсе. */

/** Инициалы для аватара: из никнейма или последние цифры телефона. */
export function userAvatarLabel(displayName: string, phone: string): string {
  const nickname = displayName.trim();
  if (nickname) {
    const parts = nickname.split(/\s+/).filter(Boolean);
    if (parts.length >= 2) {
      return `${parts[0]![0]}${parts[1]![0]}`.toUpperCase();
    }
    return nickname.slice(0, 2).toUpperCase();
  }
  const digits = phone.replace(/\D/g, "");
  return digits.slice(-2) || "?";
}

/** Никнейм для шапки и профиля; телефон не показываем. */
export function userNickname(displayName: string): string {
  const nickname = displayName.trim();
  return nickname || "Участник";
}

/** Короткая дата для карточек постов. */
export function formatPostDate(iso: string): string {
  return new Date(iso).toLocaleDateString("ru-RU", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}
