"""
Pytest configuration and fixtures.
"""
import pytest
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def test_user_data():
    """Sample user data for tests."""
    return {
        "user_id": "123-45-6789",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@test.com",
        "password": "securepassword123",
        "phone_number": "555-123-4567",
        "address": "123 Main St",
        "city": "San Jose",
        "state": "CA",
        "zip_code": "95123"
    }


@pytest.fixture
def test_flight_data():
    """Sample flight data for tests."""
    return {
        "flight_id": "TST001",
        "airline_name": "Test Airlines",
        "departure_airport": "SFO",
        "arrival_airport": "JFK",
        "departure_datetime": "2025-12-01T08:00:00",
        "arrival_datetime": "2025-12-01T16:30:00",
        "flight_class": "economy",
        "base_price": 299.99,
        "total_seats": 180,
        "available_seats": 150
    }


@pytest.fixture
def test_hotel_data():
    """Sample hotel data for tests."""
    return {
        "hotel_id": "HTL001",
        "hotel_name": "Test Hotel",
        "city": "San Francisco",
        "state": "CA",
        "star_rating": 4,
        "room_type": "standard",
        "amenities": "wifi,pool,breakfast",
        "price_per_night": 199.99,
        "total_rooms": 100,
        "available_rooms": 50
    }


@pytest.fixture
def test_car_data():
    """Sample car data for tests."""
    return {
        "car_id": "CAR001",
        "rental_company_name": "Test Rentals",
        "car_type": "sedan",
        "make_model": "Toyota Camry",
        "city": "Los Angeles",
        "price_per_day": 75.00,
        "total_cars": 20,
        "available_cars": 15
    }


@pytest.fixture
def admin_user():
    """Admin user credentials for tests."""
    return {
        "admin_id": 1,
        "username": "admin",
        "email": "admin@kayak.com",
        "role": "super_admin"
    }

