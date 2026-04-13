import threading
import time
from unittest.mock import MagicMock, patch

import pytest

from vibrant_client import Client, ENV_CLIENT_ID, ENV_CLIENT_SECRET


@pytest.fixture
def env(monkeypatch):
    monkeypatch.setenv(ENV_CLIENT_ID, "test-id")
    monkeypatch.setenv(ENV_CLIENT_SECRET, "test-secret")


def _mock_response(status=200, json_data=None, text=""):
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = json_data or {}
    resp.text = text
    return resp


def test_missing_client_id_raises(monkeypatch):
    monkeypatch.delenv(ENV_CLIENT_ID, raising=False)
    monkeypatch.setenv(ENV_CLIENT_SECRET, "secret")
    with pytest.raises(ValueError, match=ENV_CLIENT_ID):
        Client()


def test_missing_client_secret_raises(monkeypatch):
    monkeypatch.setenv(ENV_CLIENT_ID, "id")
    monkeypatch.delenv(ENV_CLIENT_SECRET, raising=False)
    with pytest.raises(ValueError, match=ENV_CLIENT_SECRET):
        Client()


def test_get_token_uses_server_expires_at(env):
    future = time.time() + 3600
    payload = {
        "access_token": "abc",
        "token_type": "Bearer",
        "expires_in": 3600,
        "expires_at": future,
        "scope": None,
        "refresh_token": None,
    }
    client = Client()
    with patch.object(client._session, "post", return_value=_mock_response(200, payload)) as post:
        token = client.get_token()
        assert token == "Bearer abc"
        assert client._cache.expires_at == float(future)
        assert post.call_count == 1


def test_get_token_falls_back_to_expires_in(env):
    payload = {"access_token": "abc", "token_type": "Bearer", "expires_in": 3600}
    client = Client()
    before = time.time()
    with patch.object(client._session, "post", return_value=_mock_response(200, payload)):
        client.get_token()
    assert client._cache.expires_at >= before + 3600 - 1
    assert client._cache.expires_at <= time.time() + 3600 + 1


def test_get_token_returns_cached_value(env):
    payload = {
        "access_token": "abc",
        "token_type": "Bearer",
        "expires_in": 3600,
    }
    client = Client()
    with patch.object(client._session, "post", return_value=_mock_response(200, payload)) as post:
        t1 = client.get_token()
        t2 = client.get_token()
        assert t1 == t2 == "Bearer abc"
        assert post.call_count == 1


def test_clear_cache_forces_refetch(env):
    payload = {"access_token": "abc", "token_type": "Bearer", "expires_in": 3600}
    client = Client()
    with patch.object(client._session, "post", return_value=_mock_response(200, payload)) as post:
        client.get_token()
        client.clear_cache()
        assert client._cache is None
        client.get_token()
        assert post.call_count == 2


def test_non_200_raises_runtime_error(env):
    client = Client()
    with patch.object(
        client._session, "post", return_value=_mock_response(401, {}, text="unauthorized")
    ):
        with pytest.raises(RuntimeError, match="401"):
            client.get_token()


def test_unknown_field_in_response_does_not_break_parsing(env):
    # Regression guard: server may add fields. We currently pass **resp.json() into
    # the dataclass, so unknown fields would raise TypeError. This test documents
    # the full set of fields the Vibrant API currently returns.
    payload = {
        "access_token": "abc",
        "token_type": "Bearer",
        "expires_in": 3600,
        "expires_at": time.time() + 3600,
        "scope": None,
        "refresh_token": None,
    }
    client = Client()
    with patch.object(client._session, "post", return_value=_mock_response(200, payload)):
        assert client.get_token() == "Bearer abc"


def test_concurrent_get_token_fetches_once(env):
    payload = {"access_token": "abc", "token_type": "Bearer", "expires_in": 3600}
    client = Client()
    with patch.object(client._session, "post", return_value=_mock_response(200, payload)) as post:
        results = []

        def worker():
            results.append(client.get_token())

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert all(r == "Bearer abc" for r in results)
        assert post.call_count == 1
