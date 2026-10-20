import pytest
from fastapi.testclient import TestClient
import main

@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "test.db")
    with TestClient(main.app) as test_client:
        yield test_client

def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}

def test_classifies_billing_and_requires_approval(client):
    response = client.post("/tickets", json={
        "ticket_id": "T-001", "message": "I was charged twice for my subscription"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["category"] == "Billing"
    assert data["assigned_team"] == "Billing Support"
    assert data["status"] in {"pending_approval", "pending_review"}
    assert "review" in data["draft_response"].lower() or "billing" in data["draft_response"].lower()

def test_urgent_ticket_gets_high_priority(client):
    response = client.post("/tickets", json={
        "ticket_id": "T-002", "message": "URGENT production down, all users cannot work"
    })
    assert response.status_code == 201
    assert response.json()["priority"] == "High"

def test_duplicate_id_rejected(client):
    payload = {"ticket_id": "T-003", "message": "Please help with my invoice"}
    assert client.post("/tickets", json=payload).status_code == 201
    response = client.post("/tickets", json=payload)
    assert response.status_code == 409

def test_invalid_input_rejected(client):
    response = client.post("/tickets", json={"ticket_id": "", "message": "hi"})
    assert response.status_code == 422

def test_approval_workflow(client):
    created = client.post("/tickets", json={
        "ticket_id": "T-004", "message": "I cannot log in to my account"
    })
    assert created.status_code == 201
    approved = client.post("/tickets/T-004/approve")
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"
    assert "no email was sent" in approved.json()["message"].lower()

def test_ambiguous_ticket_routes_to_review(client):
    response = client.post("/tickets", json={
        "ticket_id": "T-005", "message": "I have a question about something"
    })
    assert response.status_code == 201
    assert response.json()["category"] == "General"
    assert response.json()["status"] == "pending_review"

def test_not_found(client):
    assert client.get("/tickets/does-not-exist").status_code == 404
