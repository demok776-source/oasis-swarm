import json
import time
from kafka import KafkaConsumer
from src.utils.logger import get_logger

logger = get_logger("telemetry_processor")

def run_processor():
    logger.info("Initializing Telemetry Stream Processor (SpaceX pattern)...")
    
    # Retry mechanism to wait for Kafka to be ready
    consumer = None
    for i in range(10):
        try:
            consumer = KafkaConsumer(
                'telemetry.aerospace',
                bootstrap_servers=['kafka:29092'],
                auto_offset_reset='latest',
                enable_auto_commit=True,
                group_id='aerospace-group',
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            logger.info("Successfully connected to Kafka broker.")
            break
        except Exception as e:
            logger.warning(f"Kafka broker not ready, retrying ({i+1}/10)... Error: {e}")
            time.sleep(5)
            
    if not consumer:
        logger.error("Failed to connect to Kafka. Processor exiting.")
        return

    logger.info("Listening for high-velocity aerospace telemetry streams...")
    
    for message in consumer:
        payload = message.value.get("payload", {})
        altitude = payload.get("altitude", 0)
        velocity = payload.get("velocity", 0)
        
        # Real-time anomaly detection pattern
        if altitude < 150 and velocity > 40:
            logger.warning(f"ANOMALY DETECTED! Low altitude ({altitude}m) with high velocity ({velocity}m/s). Triggering emergency protocols.")
            # Here we could publish an event back to Redis for JARVIS intervention
        else:
            logger.info(f"Telemetry processed - Alt: {altitude}m, Vel: {velocity}m/s")

if __name__ == "__main__":
    run_processor()
