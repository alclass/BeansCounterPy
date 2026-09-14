"""

"""
import redis


def test_localhost_redis():
  try:
    # Connect to localhost on the default Redis port (6379)
    # decode_responses=True ensures we get back standard Python strings instead of bytes
    r = redis.Redis(host='localhost', port=6379, decode_responses=True, socket_connect_timeout=2)

    # 1. Ping the server to test connectivity
    print("Testing connection...")
    if r.ping():
      print("✅ Successfully connected to local Redis!")

    # 2. Test setting and getting a string value
    print("\nTesting read/write operations...")
    r.set('test_key', 'Hello Redis!')

    # Retrieve the value
    value = r.get('test_key')
    print(f"🔑 Key stored. Retrieved value: '{value}'")

    # 3. Clean up the test key (optional)
    r.delete('test_key')
    print("🧹 Cleaned up test key.")

  except redis.ConnectionError:
    print("❌ Failed to connect to Redis on localhost:6379.")
    print("Please ensure your local Redis server is running.")
  except Exception as e:
    print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
  test_localhost_redis()
