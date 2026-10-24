from __future__ import annotations

import json
import random
import time
from datetime import datetime, timezone

from confluent_kafka import Producer

from .config import load_config

ROOMS = [
    "Kitchen", "Living Room", "Master Bedroom", "Bedroom 2",
    "Home Office", "Garage", "Basement", "Garden",
]

CIRCUITS = [
    ("kitchen",       0.5,  4.0),
    ("hvac",          1.5,  6.0),
    ("entertainment", 0.1,  1.5),
]


def main() -> None:
    cfg = load_config()
    producer = Producer({"bootstrap.servers": cfg.bootstrap_servers})

    print(f"Publishing home readings to '{cfg.topic}' on {cfg.bootstrap_servers}")
    print("Press Ctrl+C to stop.\n")

    while True:
        circuit_type, min_kwh, max_kwh = random.choice(CIRCUITS)
        reading = {
            "circuit_id": f"CB-{random.randint(1, 20):02d}",
            "room": random.choice(ROOMS),
            "type": circuit_type,
            "kwh": round(random.uniform(min_kwh, max_kwh), 3),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        producer.produce(cfg.topic, json.dumps(reading).encode("utf-8"))
        producer.poll(0)
        print(f"  → {reading['circuit_id']}  {reading['room']:15s}  {reading['type']:14s}  {reading['kwh']} kWh")
        time.sleep(2)


if __name__ == "__main__":
    main()
