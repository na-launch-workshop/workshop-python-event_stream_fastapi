from app.consumer import events


def test_dashboard_returns_html(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "HomeGrid" in response.text


def test_events_endpoint_empty(client):
    events.clear()
    response = client.get("/api/events")
    assert response.status_code == 200
    assert response.json() == []


def test_events_endpoint_returns_data(client):
    events.clear()
    events.appendleft({
        "meter_id": "MTR-1234",
        "zone": "North Grid",
        "type": "residential",
        "kwh": 1.5,
        "timestamp": "2024-01-01T00:00:00+00:00",
    })
    response = client.get("/api/events")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["meter_id"] == "MTR-1234"


def test_appliances_endpoint_empty(client):
    response = client.get("/api/appliances")
    assert response.status_code == 200


def test_price_endpoint_no_sidecar(client):
    response = client.get("/api/price")
    assert response.status_code == 200
