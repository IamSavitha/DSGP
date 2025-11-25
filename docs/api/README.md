# Kayak Simulation API Documentation

## Overview

The Kayak Simulation system exposes REST APIs through multiple microservices. Each service handles specific domain functionality.

## Base URLs

| Service | Port | Base URL |
|---------|------|----------|
| User Service | 8001 | `http://localhost:8001` |
| Flight Service | 8002 | `http://localhost:8002` |
| Hotel Service | 8003 | `http://localhost:8003` |
| Car Service | 8004 | `http://localhost:8004` |
| Billing Service | 8005 | `http://localhost:8005` |
| Admin Service | 8006 | `http://localhost:8006` |
| Search Service | 8007 | `http://localhost:8007` |
| AI Service | 8008 | `http://localhost:8008` |

## Authentication

All protected endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

Obtain a token via the login endpoint:

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

---

## User Service API

### Create User

```http
POST /users
Content-Type: application/json

{
  "user_id": "123-45-6789",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "phone_number": "555-123-4567",
  "address": "123 Main St",
  "city": "San Jose",
  "state": "CA",
  "zip_code": "95123"
}
```

**Response:** `201 Created`

### Get User

```http
GET /users/{user_id}
```

**Response:** `200 OK`

### Update User

```http
PUT /users/{user_id}
Content-Type: application/json

{
  "first_name": "John",
  "phone_number": "555-999-8888"
}
```

### Delete User

```http
DELETE /users/{user_id}
```

**Response:** `204 No Content`

---

## Flight Service API

### Search Flights

```http
GET /flights/search?departure_airport=SFO&arrival_airport=JFK&departure_date=2025-12-01&flight_class=economy&min_price=100&max_price=500&page=1&page_size=20
```

**Query Parameters:**
- `departure_airport` - IATA code (e.g., SFO)
- `arrival_airport` - IATA code (e.g., JFK)
- `departure_date` - Date (YYYY-MM-DD)
- `flight_class` - economy, business, first
- `min_price` / `max_price` - Price range
- `airline_name` - Filter by airline
- `page` / `page_size` - Pagination

**Response:**
```json
{
  "flights": [...],
  "total_count": 45,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

### Get Flight

```http
GET /flights/{flight_id}
```

### Create Flight (Admin)

```http
POST /flights
Content-Type: application/json

{
  "flight_id": "AA123",
  "airline_name": "American Airlines",
  "departure_airport": "SFO",
  "arrival_airport": "JFK",
  "departure_datetime": "2025-12-01T08:00:00",
  "arrival_datetime": "2025-12-01T16:30:00",
  "flight_class": "economy",
  "base_price": 299.99,
  "total_seats": 180
}
```

---

## Hotel Service API

### Search Hotels

```http
GET /hotels/search?city=San%20Francisco&min_star_rating=3&max_price=300&amenities=wifi,breakfast&page=1
```

### Get Hotel

```http
GET /hotels/{hotel_id}
```

---

## Car Service API

### Search Cars

```http
GET /cars/search?city=Los%20Angeles&car_type=suv&min_price=50&max_price=150
```

---

## Billing Service API

### Process Payment

```http
POST /payments
Content-Type: application/json

{
  "booking_id": "BK-001",
  "payment_method": "credit_card",
  "card_number": "4111111111111111",
  "card_expiry": "12/26",
  "card_cvv": "123",
  "cardholder_name": "John Doe"
}
```

### Get Billing Record

```http
GET /billings/{billing_id}
```

### Search Billings

```http
GET /billings?user_id=123-45-6789&start_date=2025-01-01&payment_status=completed
```

---

## Admin Service API

### Revenue Analytics

```http
GET /analytics/revenue?period=monthly&year=2025
```

### Top Properties

```http
GET /analytics/top-properties?limit=10&year=2025
```

### City-wise Revenue

```http
GET /analytics/city-revenue?year=2025
```

---

## AI Recommendation Service API

### Get Deals

```http
GET /api/deals?listing_type=flight&min_score=50&limit=20
```

### Find Bundles

```http
POST /api/bundles
Content-Type: application/json

{
  "destination": "Miami",
  "departure_date": "2025-12-01",
  "return_date": "2025-12-05",
  "budget": 1000,
  "num_travelers": 2
}
```

### Chat with Concierge

```http
POST /api/chat
Content-Type: application/json

{
  "message": "Find me a trip to Miami under $1000",
  "user_id": "123-45-6789"
}
```

### WebSocket Events

Connect to `ws://localhost:8008/ws/events` for real-time deal updates.

---

## Error Responses

All errors follow this format:

```json
{
  "detail": {
    "message": "Error description",
    "error_code": "ERROR_CODE",
    "details": {}
  }
}
```

Common error codes:
- `DUPLICATE_USER` - User already exists
- `INVALID_STATE` - Invalid state abbreviation
- `INVALID_ZIP_CODE` - Invalid ZIP code format
- `INVALID_USER_ID` - Invalid SSN format
- `NOT_FOUND` - Resource not found

