from __future__ import annotations

from confluent_kafka.admin import AdminClient, NewTopic

from .config import load_config


def main() -> None:
    cfg = load_config()
    admin = AdminClient({"bootstrap.servers": cfg.bootstrap_servers})
    futures = admin.create_topics([NewTopic(cfg.topic, num_partitions=1, replication_factor=1)])
    for topic, future in futures.items():
        future.result()
        print(f"Topic '{topic}' created on {cfg.bootstrap_servers}")


if __name__ == "__main__":
    main()
