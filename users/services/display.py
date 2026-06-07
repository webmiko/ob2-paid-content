"""Публичное отображение авторов без раскрытия телефона."""

from users.models import User

DISPLAY_NAME_MAX_LENGTH = 80


def get_public_author_label(user: User) -> str:
    """Возвращает имя автора для ленты и карточек.

    Args:
        user: Автор публикации.

    Returns:
        display_name или маскированный идентификатор без полного телефона.
    """
    name = (user.display_name or "").strip()
    if name:
        return name[:DISPLAY_NAME_MAX_LENGTH]
    phone = user.phone
    if len(phone) >= 4:
        return f"Автор ·••{phone[-4:]}"
    return f"Автор #{user.pk}"
