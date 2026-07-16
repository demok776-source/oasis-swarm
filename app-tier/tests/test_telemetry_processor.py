"""Unit tests for the per-topic anomaly-detection handlers in
src.workers.telemetry_processor. These don't need a live Kafka broker —
they exercise `_handle_aerospace` / `_handle_physical` directly against
representative payloads for each schema."""
import logging

from src.workers import telemetry_processor as tp


def test_aerospace_normal_flight(caplog):
    with caplog.at_level(logging.INFO):
        tp._handle_aerospace({"payload": {"altitude": 1200, "velocity": 30}})
    assert any("processed" in r.message for r in caplog.records)
    assert not any("ANOMALY" in r.message for r in caplog.records)


def test_aerospace_low_altitude_high_velocity_triggers_anomaly(caplog):
    with caplog.at_level(logging.WARNING):
        tp._handle_aerospace({"payload": {"altitude": 100, "velocity": 55}})
    assert any("ANOMALY DETECTED [aerospace]" in r.message for r in caplog.records)


def test_physical_normal_drone(caplog):
    with caplog.at_level(logging.INFO):
        tp._handle_physical({
            "agent_id": "DRN-01", "agent_type": "drone",
            "velocity": (1.0, 0.0, 0.5), "battery_health": 87.0,
        })
    assert any("processed" in r.message for r in caplog.records)
    assert not any("ANOMALY" in r.message for r in caplog.records)


def test_physical_low_battery_triggers_anomaly(caplog):
    with caplog.at_level(logging.WARNING):
        tp._handle_physical({
            "agent_id": "OPTI-3", "agent_type": "humanoid",
            "velocity": (0.1, 0.0, 0.0), "battery_health": 8.0,
        })
    assert any("battery critical" in r.message for r in caplog.records)


def test_physical_overspeed_triggers_anomaly(caplog):
    with caplog.at_level(logging.WARNING):
        tp._handle_physical({
            "agent_id": "DRN-07", "agent_type": "drone",
            "velocity": (10.0, 0.0, 0.0), "battery_health": 90.0,
        })
    assert any("exceeds safe threshold" in r.message for r in caplog.records)


def test_physical_missing_fields_does_not_crash(caplog):
    # Malformed/partial payload should degrade gracefully, not raise.
    with caplog.at_level(logging.INFO):
        tp._handle_physical({"agent_id": "X"})
    assert True  # no exception raised is the assertion
