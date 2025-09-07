import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint returns HTML"""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Infotainment Accessibility Evaluator" in response.text

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "llm_provider" in data
    assert "environment" in data

def test_api_status():
    """Test the API status endpoint"""
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["api_version"] == "1.0.0"
    assert data["status"] == "operational"
    assert "features" in data
    assert "limits" in data

def test_docs_endpoint():
    """Test that API documentation is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_redoc_endpoint():
    """Test that ReDoc documentation is accessible"""
    response = client.get("/redoc")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
