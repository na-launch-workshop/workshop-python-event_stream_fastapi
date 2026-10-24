# Module: GridWatch — Grid Operations Dashboard

**Technology Stack:** Python · FastAPI · Apache Kafka (AMQ Streams) · datasette · SQLite · Electricity Price API

---

## Scenario

You've been given a live grid operations dashboard for an electricity company. It's running, but all three panels are empty — no meter readings, no appliance data, no pricing.

Your job: add three sidecars to the workspace, one at a time. Each one wires up a data source. When all three are running, the dashboard tells a complete story.

---

## Prerequisites

- OpenShift Dev Spaces workspace open with this repository
- Run **"1. Install dependencies"** from the Dev Spaces command palette before starting
- After any workspace restart, re-run **"1. Install dependencies"** before continuing

---

## How the app works

| File | Role |
|------|------|
| `app/main.py` | FastAPI app — serves the dashboard, `/api/events`, `/api/appliances`, `/api/price` |
| `app/consumer.py` | Background thread — polls Kafka for meter readings |
| `app/producer.py` | Standalone script — generates fake meter readings |
| `data/seed.py` | Seeds `appliances.db` with reference data |
| `sidecar/` | Source for the electricity price API container image |
| `devfile.yaml` | Workspace definition — **you edit this in Tasks 1, 4, and 6** |

---

## Task 1 — Add the Kafka sidecar

Open `devfile.yaml` and paste in the following component under the first `TODO` comment:

```yaml
  - name: kafka
    container:
      image: apache/kafka:3.9.0
      endpoints:
        - name: kafka-broker
          exposure: internal
          targetPort: 9092
      env:
        - name: KAFKA_NODE_ID
          value: "1"
        - name: KAFKA_PROCESS_ROLES
          value: broker,controller
        - name: KAFKA_LISTENERS
          value: PLAINTEXT://:9092,CONTROLLER://:9093
        - name: KAFKA_ADVERTISED_LISTENERS
          value: PLAINTEXT://localhost:9092
        - name: KAFKA_CONTROLLER_QUORUM_VOTERS
          value: 1@localhost:9093
        - name: KAFKA_CONTROLLER_LISTENER_NAMES
          value: CONTROLLER
        - name: KAFKA_LISTENER_SECURITY_PROTOCOL_MAP
          value: PLAINTEXT:PLAINTEXT,CONTROLLER:PLAINTEXT
        - name: KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR
          value: "1"
        - name: KAFKA_AUTO_CREATE_TOPICS_ENABLE
          value: "false"
      cpuLimit: '1'
      memoryLimit: '1Gi'
```

**Save, commit, push, restart the workspace.** Re-run **"1. Install dependencies"**.

---

## Task 2 — Create the Kafka topic

Run **"2. Create meter-readings topic"** from the command palette.

```
Topic 'meter-readings' created on localhost:9092
```

---

## Task 3 — Start the producer and watch meter readings flow

Run **"5. Start grid dashboard"** and open the `grid-dashboard` endpoint.

Run **"6. Start meter reading producer"** — the Live Readings panel fills with live data.

---

## Task 4 — Add the datasette sidecar

Open `devfile.yaml` and paste in the following component under the second `TODO` comment:

```yaml
  - name: datasette
    container:
      image: datasetteproject/datasette
      endpoints:
        - name: datasette
          exposure: internal
          targetPort: 8001
      command: ["datasette", "serve", "/projects/workshop-python-kafka/data/", "--host", "0.0.0.0", "--port", "8001"]
      cpuLimit: '500m'
      memoryLimit: '512Mi'
      mountSources: true
```

> `mountSources: true` gives datasette access to the project volume. The dashboard reads directly from SQLite — datasette is your browser-based DB explorer.

**Save, commit, push, restart the workspace.** Re-run **"1. Install dependencies"**.

---

## Task 5 — Seed and explore the appliance database

Open a terminal and run:

```bash
python3.11 data/seed.py
```

This creates `data/appliances.db` with 10 appliances. Open the `datasette` endpoint in a browser tab to explore the data.

Add your own appliances using the SQLite Explorer extension (`zknpr.sqlite-explorer`):
- Open `data/appliances.db` in the editor
- Add rows for any appliances you want to track
- The Appliance Reference panel updates within 2 seconds

---

## Task 6 — Add the electricity price sidecar

Open `sidecar/price_api.py` and take a look — this is the API powering the price ticker. It returns the current electricity rate based on time of day (off-peak / mid-peak / peak).

Open `devfile.yaml` and paste the following under the third `TODO` comment:

```yaml
  - name: price-api
    container:
      image: image-registry.openshift-image-registry.svc:5000/workspace-images/electricity-price-api:latest
      endpoints:
        - name: price-api
          exposure: internal
          targetPort: 5000
      cpuLimit: '250m'
      memoryLimit: '256Mi'
```

**Save, commit, push, restart the workspace.** Re-run **"1. Install dependencies"**.

The price ticker in the header shows the current rate. Appliance daily costs and meter reading costs update automatically.

---

## Stretch goal

Stop the producer. Check consumer lag:

```bash
/opt/kafka/bin/kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --group grid-dashboard
```

Notice the **LAG** column. Restart the producer — watch it drop to zero.

> In the next session we'll use KEDA to automatically scale the consumer based on this lag.
