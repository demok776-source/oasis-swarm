"""
Telemetry Stream Processor.

Consumes BOTH physical-swarm telemetry (drones/humanoids, produced by
`rust-gateway` -> topic `telemetry.physical`) and simulated aerospace
telemetry (produced by `POST /sync/publish` -> topic `telemetry.aerospace`).

These two topics carry genuinely different payload shapes, so each gets its
own anomaly-detection routine rather than one generic check bolted onto both:

  telemetry.aerospace (simulated flight telemetry):
    { "module": str, "payload": {"altitude": float, "velocity": float} }

  telemetry.physical (rust-gateway SwarmTelemetry, real/simulated hardware):
    {
      "agent_id": str, "agent_type": "drone"|"humanoid"|"quadruped",
      "velocity": [vx, vy, vz], "gps_coord": [lat, lon],
      "battery_health": float, "quantum_state_hash": str
    }

Previously this worker only subscribed to `telemetry.aerospace` and was
never actually started by anything (no docker-compose service, no CI job,
no reference outside this file) -- `rust-gateway`'s entire telemetry stream
had no consumer at all. Both gaps are fixed here + in docker-compose.yml.
"""
import json
import time

from kafka import KafkaConsumer

from src.utils.logger import get_logger

logger = get_logger("telemetry_processor")

AEROSPACE_TOPIC = "telemetry.aerospace"
PHYSICAL_TOPIC = "telemetry.physical"

# Physical-swarm safety thresholds
LOW_BATTERY_PCT = 15.0
MAX_SAFE_VELOCITY_MPS = 8.0  # humanoid/drone ground-speed anomaly threshold


def _handle_aerospace(payload: dict) -> None:
    inner = payload.get("payload", {})
    altitude = inner.get("altitude", 0)
    velocity = inner.get("velocity", 0)

    if altitude < 150 and velocity > 40:
        logger.warning(
            f"ANOMALY DETECTED [aerospace] Low altitude ({altitude}m) with high "
            f"velocity ({velocity}m/s). Triggering emergency protocols."
        )
    else:
        logger.info(f"Aerospace telemetry processed - Alt: {altitude}m, Vel: {velocity}m/s")


def _handle_physical(payload: dict) -> None:
    agent_id = payload.get("agent_id", "unknown")
    agent_type = payload.get("agent_type", "unknown")
    battery = payload.get("battery_health", 100.0)
    velocity_vec = payload.get("velocity", (0.0, 0.0, 0.0))

    try:
        speed = (velocity_vec[0] ** 2 + velocity_vec[1] ** 2 + velocity_vec[2] ** 2) ** 0.5
    except (TypeError, IndexError):
        speed = 0.0

    if battery <= LOW_BATTERY_PCT:
        logger.warning(
            f"ANOMALY DETECTED [physical] {agent_type} '{agent_id}' battery critical "
            f"({battery:.1f}%). Recommend return-to-base."
        )
    elif speed > MAX_SAFE_VELOCITY_MPS:
        logger.warning(
            f"ANOMALY DETECTED [physical] {agent_type} '{agent_id}' speed {speed:.2f} m/s "
            f"exceeds safe threshold ({MAX_SAFE_VELOCITY_MPS} m/s)."
        )
    else:
        logger.info(
            f"Physical telemetry processed - {agent_type} '{agent_id}' "
            f"speed: {speed:.2f}m/s, battery: {battery:.1f}%"
        )


_TOPIC_HANDLERS = {
    AEROSPACE_TOPIC: _handle_aerospace,
    PHYSICAL_TOPIC: _handle_physical,
}


def run_processor(bootstrap_servers=None, max_retries=10, retry_delay_s=5):
    logger.info("Initializing Telemetry Stream Processor (SpaceX pattern)...")
    bootstrap_servers = bootstrap_servers or ["kafka:29092"]

    consumer = None
    for i in range(max_retries):
        try:
            consumer = KafkaConsumer(
                AEROSPACE_TOPIC,
                PHYSICAL_TOPIC,
                bootstrap_servers=bootstrap_servers,
                auto_offset_reset="latest",
                enable_auto_commit=True,
                group_id="telemetry-swarm-group",
                value_deserializer=lambda x: json.loads(x.decode("utf-8")),
            )
            logger.info(
                f"Successfully connected to Kafka broker. Subscribed to: "
                f"{AEROSPACE_TOPIC}, {PHYSICAL_TOPIC}"
            )
            break
        except Exception as e:
            logger.warning(f"Kafka broker not ready, retrying ({i + 1}/{max_retries})... Error: {e}")
            time.sleep(retry_delay_s)

    if not consumer:
        logger.error("Failed to connect to Kafka. Processor exiting.")
        return

    logger.info("Listening for high-velocity swarm telemetry streams (aerospace + physical)...")

    for message in consumer:
        handler = _TOPIC_HANDLERS.get(message.topic)
        if handler is None:
            logger.warning(f"No handler registered for topic '{message.topic}', skipping.")
            continue
        try:
            handler(message.value)
        except Exception as e:
            logger.error(f"Error processing message on '{message.topic}': {e}")


if __name__ == "__main__":
    run_processor()
