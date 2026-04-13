# Vibrant OAuth2 Client for Python

A Python client library for Vibrant OAuth2 authentication. This library handles token fetching, caching, and automatic refresh with thread-safe operations.

## Installation

### Using uv (recommended)

```bash
uv add vibrant-oauth2-client
```

### Using pip

```bash
pip install vibrant-oauth2-client
```

## Configuration

Set the following environment variables:

```bash
export VIBRANT_CLIENT_ID="your_client_id"
export VIBRANT_CLIENT_SECRET="your_client_secret"
```

## Quick Start

```python
from vibrant_client import Client

# Create a new client (reads credentials from environment)
client = Client()

# Get an access token (automatically cached and refreshed)
token = client.get_token()

# Use the token in your API requests
headers = {"Authorization": token}
```

## Examples

### Basic Usage

```python
from vibrant_client import Client

client = Client()

# First call fetches a new token from the API
token = client.get_token()
print(f"Token: {token[:20]}...")

# Subsequent calls return the cached token (until it expires)
token_again = client.get_token()
assert token == token_again  # Same token from cache
```

### Making API Requests

```python
import requests
from vibrant_client import Client

client = Client()

# Get token and use it in API calls
token = client.get_token()

response = requests.get(
    "https://api.vibrant-wellness.com/v1/some-endpoint",
    headers={"Authorization": token}
)
print(response.json())
```

### Force Token Refresh

```python
from vibrant_client import Client

client = Client()

# Get initial token
token1 = client.get_token()

# Clear cache to force a fresh token on next call
client.clear_cache()

# This will fetch a new token from the API
token2 = client.get_token()
```

### Thread-Safe Concurrent Access

```python
import threading
from vibrant_client import Client

client = Client()

def worker(thread_id):
    # Safe to call from multiple threads
    token = client.get_token()
    print(f"Thread {thread_id}: {token[:20]}...")

threads = []
for i in range(10):
    t = threading.Thread(target=worker, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
```

### Error Handling

```python
from vibrant_client import Client

try:
    client = Client()
except ValueError as e:
    print(f"Configuration error: {e}")
    # Handle missing environment variables

try:
    token = client.get_token()
except RuntimeError as e:
    print(f"Token fetch failed: {e}")
    # Handle API errors
```

## Features

- Automatic token caching with expiration tracking
- Thread-safe token management using double-checked locking
- 60-second buffer before token expiration to avoid using near-expired tokens
- Simple environment-based configuration

## Development

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
# Clone and setup
git clone https://github.com/Wang-tianhao/Vibrant-Oauth2-client-python.git
cd Vibrant-Oauth2-client-python

# Install dependencies
uv sync

# Run tests
uv run pytest

# Build package
uv build
```

## API Reference

### `Client`

#### `__init__()`
Creates a new Vibrant OAuth2 client. Reads credentials from environment variables `VIBRANT_CLIENT_ID` and `VIBRANT_CLIENT_SECRET`.

**Raises:** `ValueError` if environment variables are not set.

#### `get_token() -> str`
Returns a valid access token, either from cache or by fetching a new one. The token includes the token type prefix (e.g., "Bearer xxx").

**Raises:** `RuntimeError` if the API request fails.

#### `clear_cache() -> None`
Clears the cached token, forcing a new token fetch on the next `get_token()` call.

### Types

#### `TokenResponse`
Represents the OAuth2 token response from Vibrant.
- `access_token: str`
- `token_type: str`
- `expires_in: int`
- `scope: Optional[str]`

#### `CachedToken`
Represents a cached access token with expiration tracking.
- `access_token: str`
- `expires_at: float`
- `is_expired() -> bool`

## License

MIT
