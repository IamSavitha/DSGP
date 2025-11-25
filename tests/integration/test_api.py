"""
Integration tests for API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestUserServiceAPI:
    """Integration tests for User Service API."""
    
    @pytest.fixture
    def client(self):
        from backend.services.user_service.main import app
        return TestClient(app)
    
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_create_user_invalid_id(self, client):
        """Test creating user with invalid ID format."""
        user_data = {
            "user_id": "invalid-id",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@test.com",
            "password": "password123"
        }
        response = client.post("/users", json=user_data)
        assert response.status_code == 422  # Validation error
    
    def test_create_user_invalid_state(self, client):
        """Test creating user with invalid state."""
        user_data = {
            "user_id": "123-45-6789",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@test.com",
            "password": "password123",
            "state": "XX"  # Invalid state
        }
        response = client.post("/users", json=user_data)
        assert response.status_code in [400, 422]


class TestFlightServiceAPI:
    """Integration tests for Flight Service API."""
    
    @pytest.fixture
    def client(self):
        from backend.services.flight_service.main import app
        return TestClient(app)
    
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_search_flights_empty(self, client):
        """Test flight search with no results."""
        response = client.get("/flights/search", params={
            "departure_airport": "XXX",
            "arrival_airport": "YYY"
        })
        assert response.status_code == 200
        data = response.json()
        assert "flights" in data
        assert "total_count" in data


class TestAIServiceAPI:
    """Integration tests for AI Recommendation Service API."""
    
    @pytest.fixture
    def client(self):
        from ai_service.main import app
        return TestClient(app)
    
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_get_deals(self, client):
        """Test getting deals."""
        response = client.get("/api/deals")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_chat_endpoint(self, client):
        """Test chat with concierge agent."""
        chat_data = {
            "message": "Find me flights to Miami",
            "user_id": "test-user"
        }
        response = client.post("/api/chat", json=chat_data)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data or "response" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

