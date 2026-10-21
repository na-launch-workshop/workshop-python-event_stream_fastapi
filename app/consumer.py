from __future__ import annotations

import json
import logging
import threading
import time
from collections import deque

from confluent_kafka import Consumer, KafkaException

logger = logging.getLogger(__name__)

events: deque[dict] = deque(maxlen=50)


def start_consumer(bootstrap_servers: str, topic: str, group_id: str) -> None:
    thread = threading.Thread(
        target=_consume_loop,
        args=(bootstrap_servers, topic, group_id),
        daemon=True,
    )
    thread.start()


def _consume_loop(bootstrap_servers: str, topic: str, group_id: str) -> None:
    while True:
        consumer = None
        try:
            consumer = Consumer({
                "bootstrap.servers": bootstrap_servers,
                "group.id": group_id,
                "auto.offset.reset": "earliest",
                "socket.timeout.ms": 3000,
            })
            consumer.subscribe([topic])
            logger.info("Consumer connected — listening on topic '%s'", topic)
            while True:
                msg = consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    logger.debug("Poll error: %s", msg.error())
                    continue
                try:
                    data = json.loads(msg.value().decode("utf-8"))
                    events.appendleft(data)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    logger.warning("Skipped undecodable message")
        except (KafkaException, Exception) as exc:
            logger.debug("Kafka unavailable (%s) — retrying in 5s", exc)
        finally:
            if consumer:
                try:
                    consumer.close()
                except Exception:
                    pass
        time.sleep(5)
