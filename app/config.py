from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class AppConfig:
    bootstrap_servers: str
    topic: str
    group_id: str
    port: int


def load_config() -> AppConfig:
    return AppConfig(
        bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        topic=os.environ.get("KAFKA_TOPIC", "meter-readings"),
        group_id=os.environ.get("KAFKA_GROUP_ID", "grid-dashboard"),
        port=int(os.environ.get("PORT", "8080")),
    )
