import time

from vibrant_client.types import CachedToken, TokenResponse


def test_token_response_parses_full_vibrant_payload():
    payload = {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.xxx",
        "token_type": "Bearer",
        "expires_in": 3600,
        "expires_at": 1776125503,
        "scope": None,
        "refresh_token": None,
    }
    tr = TokenResponse(**payload)
    assert tr.access_token.startswith("eyJ")
    assert tr.token_type == "Bearer"
    assert tr.expires_in == 3600
    assert tr.expires_at == 1776125503
    assert tr.scope is None
    assert tr.refresh_token is None


def test_token_response_parses_minimal_payload():
    tr = TokenResponse(access_token="x", token_type="Bearer", expires_in=60)
    assert tr.expires_at is None
    assert tr.scope is None
    assert tr.refresh_token is None


def test_cached_token_not_expired_when_deadline_is_far():
    ct = CachedToken(access_token="Bearer x", expires_at=time.time() + 3600)
    assert ct.is_expired() is False


def test_cached_token_expired_when_past_deadline():
    ct = CachedToken(access_token="Bearer x", expires_at=time.time() - 1)
    assert ct.is_expired() is True


def test_cached_token_expired_within_60s_buffer():
    ct = CachedToken(access_token="Bearer x", expires_at=time.time() + 30)
    assert ct.is_expired() is True
