"""Tests for the Wikimedia singer-photo lookup."""

import pytest

from app.services import avatars


@pytest.fixture(autouse=True)
def _clear_cache():
    avatars._CACHE.clear()
    yield
    avatars._CACHE.clear()


def test_singer_image_uses_first_wiki_hit(monkeypatch):
    hits = []

    def fake_page_image(api_url, name):
        hits.append(api_url)
        return "https://upload.wikimedia.org/example.jpg?utm_source=zh.wikipedia.org&utm_campaign=api"

    monkeypatch.setattr(avatars, "_page_image", fake_page_image)
    url = avatars.singer_image("sam hui")
    assert url == "https://upload.wikimedia.org/example.jpg"
    assert hits == [avatars._WIKIS[0]]  # zh.wikipedia tried first


def test_singer_image_falls_back_to_next_wiki(monkeypatch):
    def fake_page_image(api_url, name):
        return None if api_url.startswith("https://zh") else "https://upload.wikimedia.org/en.jpg"

    monkeypatch.setattr(avatars, "_page_image", fake_page_image)
    assert avatars.singer_image("Elvis Presley") == "https://upload.wikimedia.org/en.jpg"


def test_singer_image_returns_none_when_nobody_has_it(monkeypatch):
    monkeypatch.setattr(avatars, "_page_image", lambda api, name: None)
    assert avatars.singer_image("Nobody Famous") is None


def test_singer_image_caches_negative_results(monkeypatch):
    calls = []

    def fake_page_image(api_url, name):
        calls.append(name)
        return None

    monkeypatch.setattr(avatars, "_page_image", fake_page_image)
    assert avatars.singer_image("Ghost") is None
    assert avatars.singer_image("Ghost") is None
    assert len(calls) == 2  # two wikis for the first lookup, none after


def test_singer_image_rejects_blank_names():
    assert avatars.singer_image("   ") is None


def test_singer_image_translates_network_failures_to_none(monkeypatch):
    def boom(api_url, name):
        raise ValueError("connection reset")

    monkeypatch.setattr(avatars, "_page_image", boom)
    assert avatars.singer_image("Elvis Presley") is None


# --- HTTP endpoint ---------------------------------------------------------

def _client():
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)


def test_endpoint_redirects_to_wikimedia_image(monkeypatch):
    monkeypatch.setattr(
        "app.routers.images.singer_image",
        lambda name: "https://upload.wikimedia.org/x.jpg?utm_source=x",
    )
    resp = _client().get("/singer-image/Elvis%20Presley", follow_redirects=False)
    assert resp.status_code in (302, 307)
    assert resp.headers["location"] == "https://upload.wikimedia.org/x.jpg?utm_source=x"


def test_endpoint_404_when_no_photo(monkeypatch):
    monkeypatch.setattr("app.routers.images.singer_image", lambda name: None)
    resp = _client().get("/singer-image/Nobody%20Famous")
    assert resp.status_code == 404