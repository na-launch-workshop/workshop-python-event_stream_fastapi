from app.consumer import events


def test_dashboard_returns_html(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Order Event Stream" in response.text


def test_events_endpoint_empty(client):
    events.clear()
    response = client.get("/api/events")
    assert response.status_code == 200
    assert response.json() == []


def test_events_endpoint_returns_data(client):
    events.clear()
    events.appendleft({"id": "ABCD1234", "customer": "Alice", "item": "Laptop", "quantity": 1, "timestamp": "2024-01-01T00:00:00+00:00"})
    response = client.get("/api/events")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "ABCD1234"
