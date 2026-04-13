import os
import time
import threading
import requests
from typing import Optional

from .types import CachedToken, TokenResponse

VIBRANT_TOKEN_ENDPOINT = "https://api.vibrant-wellness.com/v1/oauth2/token"

ENV_CLIENT_ID = "VIBRANT_CLIENT_ID"
ENV_CLIENT_SECRET = "VIBRANT_CLIENT_SECRET"


class Client:
    """Vibrant OAuth2 client."""

    def __init__(self) -> None:
        """
        Create a new Vibrant OAuth2 client.
        Reads credentials from environment variables:
        - VIBRANT_CLIENT_ID
        - VIBRANT_CLIENT_SECRET
        """
        self._client_id = os.getenv(ENV_CLIENT_ID)
        if not self._client_id:
            raise ValueError(f"environment variable {ENV_CLIENT_ID} is not set")

        self._client_secret = os.getenv(ENV_CLIENT_SECRET)
        if not self._client_secret:
            raise ValueError(f"environment variable {ENV_CLIENT_SECRET} is not set")

        self._cache: Optional[CachedToken] = None
        self._lock = threading.Lock()
        self._session = requests.Session()
        self._session.timeout = 30

    def get_token(self) -> str:
        """
        Return a valid access token, either from cache or by fetching a new one.
        This is the main function that developers should use.
        """
        cache = self._cache
        if cache is not None and not cache.is_expired():
            return cache.access_token

        with self._lock:
            cache = self._cache
            if cache is not None and not cache.is_expired():
                return cache.access_token

            return self._fetch_token()

    def _fetch_token(self) -> str:
        """
        Fetch a new access token from Vibrant OAuth endpoint.
        This method should be called while holding the lock.
        """
        data = {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }

        resp = self._session.post(
            VIBRANT_TOKEN_ENDPOINT,
            data=data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
        )

        if resp.status_code != 200:
            raise RuntimeError(f"unexpected status code {resp.status_code}: {resp.text}")

        token_resp = TokenResponse(**resp.json())

        self._cache = CachedToken(
            access_token=f"{token_resp.token_type} {token_resp.access_token}",
            expires_at=time.time() + token_resp.expires_in,
        )

        return self._cache.access_token

    def clear_cache(self) -> None:
        """Clear the cached token, forcing a new token fetch on next get_token call."""
        with self._lock:
            self._cache = None
