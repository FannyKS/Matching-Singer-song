"""Singer photos from Wikimedia (free-licensed images, with attribution to
Wikipedia/Wikimedia Commons).

Tries the Chinese Wikipedia first (most of our singers are Cantonese artists),
then English Wikipedia. Results are cached in memory so the game doesn't
re-hit the API for the same name.
"""

from __future__ import annotations

import urllib.parse

import httpx

_USER_AGENT = "Matching-Singer-song/0.4 (local matching game; python-httpx)"
_WIKIS = (
    "https://zh.wikipedia.org/w/api.php",
    "https://en.wikipedia.org/w/api.php",
)
_CACHE: dict[str, str | None] = {}


def _page_image(api_url: str, name: str) -> str | None:
    params = {
        "action": "query",
        "titles": name,
        "prop": "pageimages",
        "piprop": "original",
        "format": "json",
        "redirects": "1",
    }
    try:
        with httpx.Client(timeout=8.0, follow_redirects=True) as client:
            data = client.get(
                api_url, params=params, headers={"User-Agent": _USER_AGENT}
            ).json()
    except (httpx.HTTPError, ValueError):
        return None

    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        original = page.get("original") or {}
        source = original.get("source")
        if source:
            return source
    return None


def _strip_query(url: str) -> str:
    """Drop ?utm_* (and any other) query params Wikimedia appends."""
    return urllib.parse.urlunsplit(urllib.parse.urlsplit(url)._replace(query=""))


def singer_image(name: str) -> str | None:
    """Return a Wikimedia image URL for *name*, or ``None`` if none is found."""
    name = " ".join(name.split())
    if not name:
        return None
    if name in _CACHE:
        return _CACHE[name]

    for wiki in _WIKIS:
        try:
            url = _page_image(wiki, name)
        except (httpx.HTTPError, ValueError):
            url = None
        if url:
            _CACHE[name] = _strip_query(url)
            return _CACHE[name]

    _CACHE[name] = None
    return None