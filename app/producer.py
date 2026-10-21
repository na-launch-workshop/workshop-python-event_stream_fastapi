from __future__ import annotations

import json
import random
import time
import uuid
from datetime import datetime, timezone

from confluent_kafka import Producer

from .config import load_config

ITEMS = ["Laptop", "Monitor", "Keyboard", "Mouse", "Headset", "Webcam", "Desk Chair", "USB Hub"]
CUSTOMERS = ["Alice", "Bob", "Carlos", "Dana", "Eve", "Frank", "Grace", "Hiro"]


def main() -> None:
    cfg = load_config()
    producer = Producer({"bootstrap.servers": cfg.bootstrap_servers})

    print(f"Publishing orders to '{cfg.topic}' on {cfg.bootstrap_servers}")
    print("Press Ctrl+C to stop.\n")

    while True:
        order = {
            "id": str(uuid.uuid4())[:8].upper(),
            "customer": random.choice(CUSTOMERS),
            "item": random.choice(ITEMS),
            "quantity": random.randint(1, 5),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        producer.produce(cfg.topic, json.dumps(order).encode("utf-8"))
        producer.poll(0)
        print(f"  → {order['id']}  {order['customer']:8s}  {order['item']:14s}  qty:{order['quantity']}")
        time.sleep(2)


if __name__ == "__main__":
    main()
