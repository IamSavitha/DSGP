# Test Scripts

This directory contains all test scripts organized by functional area and test type.

## Structure

```
tests/
├── user_management/        # User registration, login, profile tests
├── search_browsing/         # Search and filtering tests
├── booking_functionality/  # Booking creation and management tests
├── flight_management/      # Flight-specific tests
├── hotel_management/       # Hotel and room tests
├── car_rental/             # Car rental tests
├── payment_billing/        # Payment processing tests
├── email_notifications/    # Email notification tests
├── admin_management/        # Admin functionality tests
├── ai_concierge/           # AI Concierge tests
├── kafka_events/           # Kafka event-driven tests
├── mongodb_analytics/       # MongoDB analytics tests
├── system_infrastructure/  # System health and infrastructure tests
├── scripts/                # General test scripts
├── integration/            # Integration tests (Python)
├── unit/                   # Unit tests (Python)
├── performance/            # Performance/load tests
└── README.md              # This file
```

## Test Scripts (Ordered by Test Plan)

### 01: User Management
- `01_user_management_testing.sh` - User registration, login, profile, and booking history
  - User registration with validation
  - JWT-based login
  - Profile management
  - View past/upcoming bookings

### 02: Search & Browsing
- `02_search_browsing_testing.sh` - Search functionality for flights, hotels, cars
  - Flight search with filters
  - Hotel search
  - Car search
  - Sort and filter results
  - Unified search service

### 03: Booking Functionality
- `03_booking_functionality_testing.sh` - Booking creation and management
  - Create flight/hotel/car bookings
  - Prevent double booking
  - Availability checking
  - Price calculation
  - Booking cancellation

### 04: Flight Management
- `04_flight_management_testing.sh` - Flight-specific operations
  - Flight search with filters
  - Flight details
  - Seat inventory management
  - Flight ratings
  - Admin flight operations

### 05: Hotel Management
- `05_hotel_management_testing.sh` - Hotel and room operations
  - Hotel search with filters
  - Room availability
  - Room pricing
  - Amenities management
  - Booking workflow

### 06: Car Rental
- `06_car_rental_testing.sh` - Car rental operations
  - Car search by location
  - Car details
  - Price calculation
  - Availability check
  - Booking confirmation

### 07: Payment & Billing
- `07_payment_billing_testing.sh` - Payment processing
  - Payment initiation
  - Tax calculation (8.75%)
  - Invoice generation
  - Secure card storage
  - Payment status tracking

### 08: Email Notifications
- `08_email_notifications_testing.sh` - Verify email notifications are sent via Kafka events
  - Booking confirmation emails
  - Payment confirmation emails
  - Email service consumer verification

### 09: Admin Management
- `09_admin_management_testing.sh` - Admin operations
  - Admin authentication
  - CRUD operations (flights, hotels, cars)
  - User management
  - Booking management
  - Admin audit logs

### 10: AI Concierge
- `10_ai_concierge_testing.sh` - AI-powered features
  - Get deals API
  - Trip bundles (Flight + Hotel + Car)
  - Chat with concierge
  - WebSocket real-time updates
  - MongoDB conversation storage

### 11: Kafka Event-Driven Testing
- `11_kafka_events_testing.sh` - Comprehensive Kafka event testing
  - User created events
  - Booking created events
  - Payment completed events
  - Consumer group verification
  - Event processing verification

### 12: MongoDB Analytics Testing
- `12_mongodb_analytics_testing.sh` - Comprehensive MongoDB analytics testing
  - Clickstream logging
  - User preferences tracking
  - Price history tracking
  - Reviews storage
  - Admin audit logs

### 13: System Infrastructure
- `13_system_infrastructure_testing.sh` - System health and infrastructure
  - Docker container health
  - Service communication
  - Database connections
  - CORS configuration
  - Network connectivity

### Performance Testing
- `performance_load_testing.sh` - Load and performance testing
  - Search response time
  - Concurrent users
  - Database query performance
  - Cache performance

## Running Tests

### Quick Test Execution
Run all tests in order:
```bash
# Test 01: User Management
cd tests/user_management && ./01_user_management_testing.sh

# Test 02: Search & Browsing
cd tests/search_browsing && ./02_search_browsing_testing.sh

# Test 03: Booking Functionality
cd tests/booking_functionality && ./03_booking_functionality_testing.sh

# Test 04: Flight Management
cd tests/flight_management && ./04_flight_management_testing.sh

# Test 05: Hotel Management
cd tests/hotel_management && ./05_hotel_management_testing.sh

# Test 06: Car Rental
cd tests/car_rental && ./06_car_rental_testing.sh

# Test 07: Payment & Billing
cd tests/payment_billing && ./07_payment_billing_testing.sh

# Test 08: Email Notifications
cd tests/email_notifications && ./08_email_notifications_testing.sh

# Test 09: Admin Management
cd tests/admin_management && ./09_admin_management_testing.sh

# Test 10: AI Concierge
cd tests/ai_concierge && ./10_ai_concierge_testing.sh

# Test 11: Kafka Events
cd tests/kafka_events && ./11_kafka_events_testing.sh

# Test 12: MongoDB Analytics
cd tests/mongodb_analytics && ./12_mongodb_analytics_testing.sh

# Test 13: System Infrastructure
cd tests/system_infrastructure && ./13_system_infrastructure_testing.sh

# Performance Testing
cd tests/performance && ./performance_load_testing.sh
```

### Run All Tests (Bash Script)
```bash
#!/bin/bash
# Run all tests sequentially
for dir in tests/*/; do
    if [ -f "$dir"*.sh ]; then
        echo "Running tests in $(basename "$dir")..."
        cd "$dir" && bash *.sh && cd - > /dev/null
    fi
done
```

## Python Tests

### Integration Tests
```bash
pytest tests/integration/
```

### Unit Tests
```bash
pytest tests/unit/
```

### Performance Tests
```bash
pytest tests/performance/
```

## Prerequisites

- Docker and Docker Compose running
- All services started: `docker-compose up -d`
- Kafka topics created
- Databases initialized

## Test Scripts Location

General utility scripts are in `scripts/`:
- Database verification
- Service verification
- Kafka event verification

