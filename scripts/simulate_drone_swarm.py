import json
import time
import random
import threading
from kafka import KafkaProducer

# Configure Producer for maximum throughput
try:
    producer = KafkaProducer(
        bootstrap_servers=['kafka:29092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        linger_ms=10, 
        batch_size=32768
    )
    print("[SUCCESS] Connected to local Kafka broker at kafka:29092")
except Exception as e:
    print(f"[ERROR] Failed to connect to Kafka. Make sure docker-compose is running. Details: {e}")
    exit(1)

def simulate_drones(drone_count=1000, duration_seconds=10):
    print(f"🚀 Initiating Drone Swarm Simulation ({drone_count} active drones)")
    print(f"📡 Pumping telemetry to Kafka topic 'telemetry.aerospace' for {duration_seconds} seconds...")
    
    start_time = time.time()
    messages_sent = 0
    
    while time.time() - start_time < duration_seconds:
        # Simulate a burst of telemetry from multiple drones
        for _ in range(drone_count):
            # Normal operating parameters
            altitude = random.uniform(200.0, 500.0)
            velocity = random.uniform(10.0, 30.0)
            
            # Occasionally inject an anomaly (e.g. 1% chance)
            if random.random() < 0.01:
                altitude = random.uniform(50.0, 100.0) # Dangerously low
                velocity = random.uniform(50.0, 80.0)  # Dangerously fast
            
            payload = {
                "module": "OASIS_PRIME_DRONE_SWARM",
                "payload": {
                    "drone_id": f"DRN-{random.randint(1000, 9999)}",
                    "altitude": altitude,
                    "velocity": velocity,
                    "lat": random.uniform(-90.0, 90.0),
                    "lon": random.uniform(-180.0, 180.0)
                }
            }
            producer.send("telemetry.aerospace", value=payload)
            messages_sent += 1
            
        # Flush batches every iteration for high frequency
        producer.flush()
        
    print(f"✅ Simulation Complete. Successfully published {messages_sent} telemetry events to Kafka.")

if __name__ == "__main__":
    # Simulate 500 drones sending data for 5 seconds
    simulate_drones(drone_count=500, duration_seconds=5)
