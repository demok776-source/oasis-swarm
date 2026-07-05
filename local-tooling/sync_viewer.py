import os
import redis
import sys

def main():
    redis_host = os.getenv("REDIS_HOST", "127.0.0.1")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    
    print(f"=== Sync Layer Event Viewer ===")
    print(f"Connecting to Redis at {redis_host}:{redis_port}...")
    
    try:
        r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        r.ping()
        print("Connected. Listening for events on 'oasis:channel:*'...")
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)
        
    pubsub = r.pubsub()
    pubsub.psubscribe("oasis:channel:*")
    
    try:
        for message in pubsub.listen():
            if message['type'] == 'pmessage':
                channel = message['channel']
                data = message['data']
                print(f"[EVENT] Channel: {channel} | Message: {data}")
    except KeyboardInterrupt:
        print("\nExiting Event Viewer.")

if __name__ == "__main__":
    main()
