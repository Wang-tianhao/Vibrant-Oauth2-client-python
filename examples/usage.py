import sys
import time
import threading

sys.path.insert(0, "../src")

from vibrant_client import Client


def main():
    # Create a new Vibrant OAuth2 client
    # It will read VIBRANT_CLIENT_ID and VIBRANT_CLIENT_SECRET from environment
    try:
        client = Client()
    except ValueError as e:
        print(f"Failed to create client: {e}")
        return

    print("Vibrant OAuth2 Client Example")
    print("==============================")

    # First call - will fetch a new token
    print("\n1. Fetching first token...")
    try:
        token1 = client.get_token()
    except Exception as e:
        print(f"Failed to get token: {e}")
        return
    print(f"   Token obtained: {token1[:20]}...")

    # Second call - should return cached token
    print("\n2. Getting token again (should be cached)...")
    try:
        token2 = client.get_token()
    except Exception as e:
        print(f"Failed to get token: {e}")
        return
    print(f"   Token obtained: {token2[:20]}...")

    if token1 == token2:
        print("   * Token was returned from cache")

    # Demonstrate concurrent access
    print("\n3. Testing concurrent access...")
    results = []

    def fetch_token(thread_id):
        try:
            token = client.get_token()
            results.append((thread_id, token[:20]))
            print(f"   Thread {thread_id} got token: {token[:20]}...")
        except Exception as e:
            print(f"Thread {thread_id} failed: {e}")

    threads = []
    for i in range(5):
        t = threading.Thread(target=fetch_token, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Clear cache to force refresh
    print("\n4. Clearing cache and fetching new token...")
    client.clear_cache()
    try:
        token3 = client.get_token()
    except Exception as e:
        print(f"Failed to get token: {e}")
        return
    print(f"   New token obtained: {token3[:20]}...")

    print("\n* Example completed successfully!")


if __name__ == "__main__":
    main()
