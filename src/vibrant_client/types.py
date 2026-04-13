from dataclasses import dataclass
from typing import Optional
import time


@dataclass
class TokenResponse:
    """Represents the OAuth2 token response from Vibrant."""
    access_token: str
    token_type: str
    expires_in: int
    scope: Optional[str] = None


@dataclass
class CachedToken:
    """Represents a cached access token with expiration tracking."""
    access_token: str
    expires_at: float

    def is_expired(self) -> bool:
        """
        Check if the cached token has expired or will expire soon.
        Adds a 60-second buffer to avoid using tokens that are about to expire.
        """
        return time.time() + 60 > self.expires_at
