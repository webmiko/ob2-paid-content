"""Разбор ссылок на видео (YouTube, Vimeo, Rutube, VK, Дзен) для embed в публикациях."""

import re
from urllib.parse import parse_qs, urlparse

VideoProvider = str

PROVIDER_YOUTUBE: VideoProvider = "youtube"
PROVIDER_VIMEO: VideoProvider = "vimeo"
PROVIDER_RUTUBE: VideoProvider = "rutube"
PROVIDER_VK: VideoProvider = "vk"
PROVIDER_DZEN: VideoProvider = "dzen"

SUPPORTED_VIDEO_PROVIDERS: frozenset[str] = frozenset(
    {
        PROVIDER_YOUTUBE,
        PROVIDER_VIMEO,
        PROVIDER_RUTUBE,
        PROVIDER_VK,
        PROVIDER_DZEN,
    },
)

YOUTUBE_HOSTS = frozenset(
    {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "youtu.be",
        "www.youtu.be",
    },
)

VIMEO_HOSTS = frozenset({"vimeo.com", "www.vimeo.com", "player.vimeo.com"})
RUTUBE_HOSTS = frozenset({"rutube.ru", "www.rutube.ru"})
VK_HOSTS = frozenset({"vk.com", "www.vk.com", "vk.ru", "www.vk.ru", "vkvideo.ru", "www.vkvideo.ru"})
DZEN_HOSTS = frozenset(
    {
        "dzen.ru",
        "www.dzen.ru",
        "zen.yandex.ru",
        "www.zen.yandex.ru",
    },
)

VK_VIDEO_RE = re.compile(r"^video(-?\d+)_(\d+)$")


def _parse_url(url: str) -> tuple[str, str, str, str] | None:
    """Возвращает (scheme_ok, host, path, query) или None."""
    cleaned = url.strip()
    if not cleaned:
        return None
    parsed = urlparse(cleaned)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return None
    return parsed.scheme, parsed.netloc.lower(), parsed.path, parsed.query


def detect_video_provider(url: str) -> VideoProvider | None:
    """Определяет провайдера по URL публикации."""
    parsed = _parse_url(url)
    if parsed is None:
        return None
    _, host, path, _query = parsed
    if host in YOUTUBE_HOSTS:
        return PROVIDER_YOUTUBE
    if host in VIMEO_HOSTS:
        return PROVIDER_VIMEO
    if host in RUTUBE_HOSTS:
        return PROVIDER_RUTUBE
    if host in VK_HOSTS:
        return PROVIDER_VK
    if host in DZEN_HOSTS and ("/video/watch/" in path or path.startswith("/embed/")):
        return PROVIDER_DZEN
    return None


def _youtube_embed_url(url: str) -> str | None:
    parsed = _parse_url(url)
    if parsed is None:
        return None
    _scheme, host, path, query = parsed
    if host not in YOUTUBE_HOSTS:
        return None

    if host.endswith("youtu.be"):
        video_id = path.lstrip("/").split("/")[0]
        return f"https://www.youtube.com/embed/{video_id}" if video_id else None

    if path.startswith("/embed/"):
        video_id = path.removeprefix("/embed/").split("/")[0]
        return f"https://www.youtube.com/embed/{video_id}" if video_id else None

    if path == "/watch":
        video_ids = parse_qs(query).get("v", [])
        if video_ids and video_ids[0]:
            return f"https://www.youtube.com/embed/{video_ids[0]}"
    return None


def _vimeo_embed_url(url: str) -> str | None:
    parsed = _parse_url(url)
    if parsed is None:
        return None
    _scheme, host, path, _query = parsed
    if host not in VIMEO_HOSTS:
        return None

    if path.startswith("/video/"):
        video_id = path.removeprefix("/video/").split("/")[0]
        return f"https://player.vimeo.com/video/{video_id}" if video_id.isdigit() else None

    parts = [part for part in path.split("/") if part]
    if len(parts) == 1 and parts[0].isdigit():
        return f"https://player.vimeo.com/video/{parts[0]}"
    return None


def _rutube_embed_url(url: str) -> str | None:
    parsed = _parse_url(url)
    if parsed is None:
        return None
    _scheme, host, path, _query = parsed
    if host not in RUTUBE_HOSTS:
        return None

    if "/play/embed/" in path:
        video_id = path.split("/play/embed/")[-1].split("/")[0]
        return f"https://rutube.ru/play/embed/{video_id}" if video_id else None

    if "/video/" in path:
        video_id = path.split("/video/")[-1].split("/")[0]
        return f"https://rutube.ru/play/embed/{video_id}" if video_id else None
    return None


def _vk_embed_url(url: str) -> str | None:
    parsed = _parse_url(url)
    if parsed is None:
        return None
    _scheme, host, path, _query = parsed
    if host not in VK_HOSTS:
        return None

    slug = path.strip("/").split("/")[-1]
    match = VK_VIDEO_RE.match(slug)
    if not match:
        return None
    oid, video_id = match.group(1), match.group(2)
    return f"https://vk.com/video_ext.php?oid={oid}&id={video_id}&hd=2"


def _dzen_embed_url(url: str) -> str | None:
    parsed = _parse_url(url)
    if parsed is None:
        return None
    _scheme, host, path, _query = parsed
    if host not in DZEN_HOSTS:
        return None

    if path.startswith("/embed/"):
        video_id = path.removeprefix("/embed/").split("/")[0]
        return f"https://dzen.ru/embed/{video_id}" if video_id else None

    marker = "/video/watch/"
    if marker in path:
        video_id = path.split(marker, 1)[1].split("/")[0]
        return f"https://dzen.ru/embed/{video_id}" if video_id else None
    return None


def _append_query_params(url: str, *params: str) -> str:
    """Добавляет query-параметры к URL embed."""
    if not params:
        return url
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}{'&'.join(params)}"


def _harden_embed_url(embed: str, provider: VideoProvider | None) -> str:
    """Ужесточает embed для платного контента (меньше утечек и UI скачивания)."""
    if provider == PROVIDER_YOUTUBE:
        hardened = embed.replace("www.youtube.com/embed", "www.youtube-nocookie.com/embed")
        return _append_query_params(
            hardened,
            "modestbranding=1",
            "rel=0",
            "disablekb=1",
            "iv_load_policy=3",
        )
    if provider == PROVIDER_VIMEO:
        return _append_query_params(embed, "dnt=1", "title=0", "byline=0")
    if provider == PROVIDER_RUTUBE:
        return _append_query_params(embed, "t=0")
    return embed


def video_embed_url(url: str, *, protected_mode: bool = False) -> str | None:
    """Преобразует поддерживаемую ссылку в URL для iframe embed."""
    provider = detect_video_provider(url)
    embed: str | None = None
    if provider == PROVIDER_YOUTUBE:
        embed = _youtube_embed_url(url)
    elif provider == PROVIDER_VIMEO:
        embed = _vimeo_embed_url(url)
    elif provider == PROVIDER_RUTUBE:
        embed = _rutube_embed_url(url)
    elif provider == PROVIDER_VK:
        embed = _vk_embed_url(url)
    elif provider == PROVIDER_DZEN:
        embed = _dzen_embed_url(url)
    if embed and protected_mode:
        return _harden_embed_url(embed, provider)
    return embed


def is_valid_video_url(url: str) -> bool:
    """Проверяет, что строка — поддерживаемая ссылка на видео."""
    return video_embed_url(url) is not None


def youtube_embed_url(url: str) -> str | None:
    """Обратная совместимость: embed только для YouTube."""
    if detect_video_provider(url) != PROVIDER_YOUTUBE:
        return None
    return _youtube_embed_url(url)


def is_valid_youtube_url(url: str) -> bool:
    """Обратная совместимость: проверка только YouTube."""
    return youtube_embed_url(url) is not None
