from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_read_root():
    """Testuje główny endpoint /"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Travel Agent Planner API"}

def test_get_health_status():
    """Testuje endpoint /api/v1/health"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
