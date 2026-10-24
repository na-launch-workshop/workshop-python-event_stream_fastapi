from __future__ import annotations

import json
import random
import time
import uuid
from datetime import datetime, timezone

from confluent_kafka import Producer

from .config import load_config

ZONES = [
    "North Grid", "South Grid", "East Grid", "West Grid",
    "City Centre", "Industrial Park", "Suburbs North", "Suburbs South",
]

METER_TYPES = [
    ("residential",  0.5,  3.0),
    ("commercial",   2.0, 15.0),
    ("industrial",  10.0, 50.0),
]


def main() -> None:
    cfg = load_config()
    producer = Producer({"bootstrap.servers": cfg.bootstrap_servers})

    print(f"Publishing meter readings to '{cfg.topic}' on {cfg.bootstrap_servers}")
    print("Press Ctrl+C to stop.\n")

    while True:
        meter_type, min_kwh, max_kwh = random.choice(METER_TYPES)
        reading = {
            "meter_id": f"MTR-{random.randint(1000, 9999)}",
            "zone": random.choice(ZONES),
            "type": meter_type,
            "kwh": round(random.uniform(min_kwh, max_kwh), 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        producer.produce(cfg.topic, json.dumps(reading).encode("utf-8"))
        producer.poll(0)
        print(f"  → {reading['meter_id']}  {reading['zone']:16s}  {reading['type']:12s}  {reading['kwh']} kWh")
        time.sleep(2)


if __name__ == "__main__":
    main()
