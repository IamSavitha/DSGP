# Utility Scripts

This directory contains utility scripts for database management, Kafka setup, and system verification.

## Structure

```
scripts/
├── database/               # Database initialization and seeding
├── kafka/                  # Kafka topic management
├── verification/          # System verification scripts
└── README.md              # This file
```

## Database Scripts

### `database/init_databases.py`
Initialize MySQL and MongoDB databases with schemas and indexes.

### `database/seed_travel_data.py`
Seed the database with sample travel data (flights, hotels, cars).

### `database/fix_hotel_rooms.py`
Fix hotel room availability issues.

## Kafka Scripts

### `kafka/create_kafka_topics.sh`
Create all required Kafka topics for the system.

## Verification Scripts

### `verification/verify_all_services.sh`
Verify all microservices are running and healthy.

### `verification/verify_database_state.sh`
Verify database state and data integrity.

### `verification/verify_kafka_events.sh`
Verify Kafka events are being published and consumed.

### `verification/check_redis_cache.sh`
Check Redis cache status and keys.

### `verification/test_flight_booking.sh`
Test flight booking flow end-to-end.

### `verification/test_unified_search.py`
Test unified search functionality.

## Usage

### Initialize Databases
```bash
cd scripts/database
python init_databases.py
python seed_travel_data.py
```

### Create Kafka Topics
```bash
cd scripts/kafka
./create_kafka_topics.sh
```

### Verify System
```bash
cd scripts/verification
./verify_all_services.sh
./verify_database_state.sh
./verify_kafka_events.sh
```

## Prerequisites

- Docker and Docker Compose running
- Python 3.8+ with required dependencies
- Access to MySQL, MongoDB, Kafka, and Redis
