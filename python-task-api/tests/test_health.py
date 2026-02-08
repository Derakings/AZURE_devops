"""Basic health check tests for the Task API."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test the /health endpoint returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"
    assert "timestamp" in data


def test_docs():
    """Test the /docs endpoint returns 200 OK."""
    response = client.get("/docs")
    assert response.status_code == 200