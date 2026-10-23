# Module: Event Stream Dashboard with AMQ Streams

**Technology Stack:** Python · FastAPI · Apache Kafka (AMQ Streams) · datasette · SQLite

---

## Scenario

You've been handed a live order dashboard. Open it now — it's running, but completely empty. No data flows in because the app has no Kafka broker to connect to.

Your job: wire up the broker, create the topic, and start the producer. If you do it right, the dashboard fills itself.

---

## Prerequisites

- OpenShift Dev Spaces workspace open with this repository
- Run **"1. Install dependencies"** from the Dev Spaces command palette before starting
- After any workspace restart (e.g. after Task 1), re-run **"1. Install dependencies"** before continuing

---

## How the app works

| File | Role |
|------|------|
| `app/main.py` | FastAPI app — serves the dashboard, `/api/events`, and `/api/customers` |
| `app/consumer.py` | Background thread — polls Kafka and feeds events into the dashboard |
| `app/producer.py` | Standalone script — generates fake orders and publishes them |
| `data/customers.db` | SQLite database — customer profiles served via datasette |
| `devfile.yaml` | Workspace definition — **you'll edit this in Tasks 1 and 4** |

The consumer is already running. It retries every 5 seconds until it can reach a broker. As soon as the broker and topic exist, it connects automatically.

---

## Task 1 — Add the Kafka sidecar to `devfile.yaml`

Open `devfile.yaml`. Find the `TODO` comment under the `components:` section and paste in the following component:

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

**Save the file, then restart your Dev Spaces workspace** so the new container starts.

---

## Task 2 — Create the Kafka topic

Once the workspace restarts, run command **"2. Create orders topic"** from the Dev Spaces command palette.

You should see:

```
Topic 'orders' created on localhost:9092
```

---

## Task 3 — Start the producer and watch the dashboard

Run command **"5. Start order producer"** from the Dev Spaces command palette, or run directly:

```bash
python -m app.producer
```

Open the **`event-dashboard`** endpoint from the Dev Spaces Endpoints view.

The dashboard should immediately start filling with incoming orders.

---

## Stretch goal

Stop the producer (`Ctrl+C`). Open a second terminal in the `kafka` container and run a consumer group check:

```bash
/opt/kafka/bin/kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --group event-stream-app
```

Notice the **LAG** column. Restart the producer and watch the lag drop to zero as the consumer catches up.

> In the next session we'll use KEDA to automatically scale a consumer deployment based on this lag.

---

## Task 4 — Add the datasette sidecar to `devfile.yaml`

The dashboard has a **Customers** panel that enriches order events with profile data. It polls `localhost:8001` — but datasette isn't running yet.

Open `devfile.yaml` and paste in the following component alongside the kafka sidecar:

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

> `mountSources: true` gives datasette access to the project volume so it can read `data/customers.db`.

**Save and restart the workspace**, then re-run **"1. Install dependencies"**.

---

## Task 5 — Add customer data

The SQLite database is at `data/customers.db`. The SQLite extension is already installed in your editor.

1. In the VS Code Explorer, right-click `data/customers.db` and select **Open Database**
2. Expand the **SQLITE EXPLORER** panel in the sidebar
3. Click the ▶ icon next to `customers` to open a query window
4. Insert some rows:

```sql
INSERT INTO customers (name, department, role, location) VALUES
  ('Alice', 'Engineering', 'Backend Developer', 'New York'),
  ('Bob', 'Product', 'Product Manager', 'Chicago'),
  ('Carlos', 'Engineering', 'DevOps Engineer', 'Austin'),
  ('Dana', 'Design', 'UX Designer', 'Seattle'),
  ('Eve', 'Engineering', 'Frontend Developer', 'Boston'),
  ('Frank', 'Sales', 'Account Executive', 'Denver'),
  ('Grace', 'Engineering', 'Data Engineer', 'San Francisco'),
  ('Hiro', 'Product', 'Product Analyst', 'Los Angeles');
```

5. Run the query — the Customers panel on the dashboard will populate on the next poll.
