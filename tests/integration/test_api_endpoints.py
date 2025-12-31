"""Integration tests for API endpoints"""

import pytest
import json
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client(seeded_client):
    """Create test client with seeded data and CSRF support"""
    return seeded_client


class TestHealthEndpoint:
    """Tests for health check endpoint"""
    
    def test_health_check_success(self, client):
        """Test health check endpoint returns OK"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_health_check_response_format(self, client):
        """Test health check response has correct format"""
        response = client.get("/api/v1/health")
        data = response.json()
        assert "status" in data
        assert isinstance(data["status"], str)


class TestWelcomeEndpoint:
    """Tests for welcome endpoint"""
    
    def test_welcome_returns_app_info(self, client):
        """Test welcome endpoint returns app information"""
        response = client.get("/api/v1/")
        assert response.status_code == 200
        data = response.json()
        assert "app_name" in data
        assert "app_version" in data
    
    def test_welcome_response_structure(self, client):
        """Test welcome response has correct structure"""
        response = client.get("/api/v1/")
        data = response.json()
        assert isinstance(data.get("app_name"), str)
        assert isinstance(data.get("app_version"), str)


class TestAuthEndpoint:
    """Tests for authentication endpoint"""
    
    def test_login_success_with_correct_credentials(self, client):
        """Test login with correct credentials"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "password"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_fails_with_wrong_password(self, client):
        """Test login with wrong password"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "wrongpassword"}
        )
        assert response.status_code == 401
    
    def test_login_fails_with_unknown_user(self, client):
        """Test login with unknown username"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "unknown", "password": "password"}
        )
        assert response.status_code == 401
    
    def test_login_response_structure(self, client):
        """Test login response has correct structure"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "password"}
        )
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert isinstance(data["access_token"], str)


class TestProtectedEndpoints:
    """Tests for endpoints requiring authentication"""
    
    def test_metrics_without_token_returns_401(self, client):
        """Test metrics endpoint without auth token"""
        response = client.get("/api/v1/metrics")
        assert response.status_code == 401
    
    def test_metrics_with_valid_token_success(self, client):
        """Test metrics endpoint with valid auth token"""
        # Get token first
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "password"}
        )
        token = login_response.json()["access_token"]
        
        # Call protected endpoint
        response = client.get(
            "/api/v1/metrics",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
    
    def test_predict_without_token_returns_403(self, client):
        """Test predict endpoint without auth token"""
        response = client.post(
            "/api/v1/predict",
            json={"text": "test"}
        )
        assert response.status_code == 401
    
    def test_predict_with_valid_token_success(self, client):
        """Test predict endpoint with valid auth token"""
        # Get token first
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "password"}
        )
        token = login_response.json()["access_token"]
        
        # Call protected endpoint
        response = client.post(
            "/api/v1/predict",
            json={"text": "test text"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200


class TestInvalidEndpoints:
    """Tests for invalid/non-existent endpoints"""
    
    def test_invalid_endpoint_returns_404(self, client):
        """Test accessing non-existent endpoint"""
        response = client.get("/api/v1/invalid")
        assert response.status_code == 404
    
    def test_invalid_http_method_returns_405(self, client):
        """Test using invalid HTTP method"""
        response = client.post("/api/v1/health")  # health only accepts GET
        # Note: FastAPI might return 405 or 422 depending on configuration
        assert response.status_code in [405, 422]


class TestErrorHandling:
    """Tests for error handling"""
    
    def test_malformed_json_request(self, client):
        """Test handling of malformed JSON"""
        response = client.post(
            "/api/v1/auth/login",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code >= 400
    
    def test_missing_required_fields(self, client):
        """Test handling of missing required fields"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin"}  # Missing password
        )
        assert response.status_code >= 400