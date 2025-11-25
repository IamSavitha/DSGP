# Kayak Simulation Project Index

This document provides a comprehensive index of all files and directories in the Kayak Travel Simulation System project.

## Table of Contents
- [Root Files](#root-files)
- [Backend Services](#backend-services)
- [AI Service](#ai-service)
- [Frontend](#frontend)
- [Infrastructure & Configuration](#infrastructure--configuration)
- [Tests](#tests)
- [Documentation](#documentation)
- [Scripts](#scripts)

---

## Root Files

| File | Description |
|------|-------------|
| `README.md` | Main project documentation with architecture overview, setup instructions, and API documentation |
| `requirements.txt` | Python dependencies for all backend services |
| `docker-compose.yml` | Multi-container orchestration configuration for all services |
| `INDEX.md` | This file - comprehensive project index |
| `Group Project- Kayak.pdf` | Project specification document |

---

## Backend Services

### Common Utilities (`backend/common/`)

| File | Description |
|------|-------------|
| `__init__.py` | Package initialization |
| `config.py` | Configuration management using Pydantic settings (database URLs, Redis, Kafka, etc.) |
| `database.py` | Database connection management for MySQL and MongoDB |
| `cache.py` | Redis caching utilities and connection management |
| `validators.py` | Input validation functions (SSN format, ZIP code, State abbreviations) |
| `exceptions.py` | Custom exception classes for error handling |

### Models (`backend/models/`)

| File | Description |
|------|-------------|
| `__init__.py` | Package initialization |
| `mysql_models.py` | SQLModel ORM entities for MySQL (Users, Flights, Hotels, Cars, Bookings, Billing) |
| `mongodb_models.py` | MongoDB document schemas (Reviews, Images, User Behavior, Analytics) |

### Schemas (`backend/schemas/`)

| File | Description |
|------|-------------|
| `__init__.py` | Package initialization |
| `user_schemas.py` | Pydantic schemas for user operations (create, update, response) |
| `flight_schemas.py` | Pydantic schemas for flight operations (search, create, update, response) |
| `hotel_schemas.py` | Pydantic schemas for hotel operations (search, create, update, response) |
| `car_schemas.py` | Pydantic schemas for car rental operations (search, create, update, response) |
| `booking_schemas.py` | Pydantic schemas for booking operations (create, update, response) |
| `billing_schemas.py` | Pydantic schemas for billing and payment operations |

### Kafka (`backend/kafka/`)

| File | Description |
|------|-------------|
| `__init__.py` | Package initialization |
| `topics.py` | Kafka topic definitions and constants |
| `producer.py` | Kafka message producer implementation |
| `consumer.py` | Kafka message consumer implementation |

### Database Initialization (`backend/database/`)

| Directory/File | Description |
|----------------|-------------|
| `mysql/init/01_schema.sql` | MySQL database schema initialization script |
| `mongodb/init/01_init.js` | MongoDB database initialization script |

### Microservices (`backend/services/`)

#### User Service (`user_service/`)
| File | Description |
|------|-------------|
| `__init__.py` | Package initialization |
| `main.py` | FastAPI application entry point (port 8001) |
| `service.py` | Business logic for user CRUD operations |
| `auth.py` | Authentication and authorization utilities |

#### Flight Service (`flight_service/`)
| File | Description |
|------|-------------|
| `__init__.py` | Package initialization |
| `main.py` | FastAPI application entry point (port 8002) |
| `service.py` | Business logic for flight search and management |

#### Hotel Service (`hotel_service/`)
| File | Description |
|------|-------------|
| `__init__.py` | Package initialization |
| `main.py` | FastAPI application entry point (port 8003) |
| `service.py` | Business logic for hotel search and management |

#### Car Service (`car_service/`)
| File | Description |
|------|-------------|
| `__init__.py` | Package initialization |
| `main.py` | FastAPI application entry point (port 8004) |
| `service.py` | Business logic for car rental search and management |

#### Billing Service (`billing_service/`)
| File | Description |
|------|-------------|
| `__init__.py` | Package initialization |
| `main.py` | FastAPI application entry point (port 8005) |
| `service.py` | Business logic for payment processing and billing records |

#### Admin Service (`admin_service/`)
| File | Description |
|------|-------------|
| `__init__.py` | Package initialization |
| `main.py` | FastAPI application entry point (port 8006) |
| `service.py` | Business logic for admin analytics and reporting |

#### Search Service (`search_service/`)
| File | Description |
|------|-------------|
| `__init__.py` | Package initialization (port 8007) |

---

## AI Service (`ai_service/`)

| File/Directory | Description |
|----------------|-------------|
| `__init__.py` | Package initialization |
| `main.py` | FastAPI application entry point (port 8008) with lifespan management |
| `agents/` | AI agent implementations |
| `agents/__init__.py` | Package initialization |
| `agents/deals_agent.py` | Deal detection and scoring agent |
| `agents/concierge_agent.py` | AI trip assistant/concierge agent |
| `api/` | API layer |
| `api/__init__.py` | Package initialization |
| `api/routes.py` | HTTP REST endpoints for deals, bundles, and chat |
| `api/websocket.py` | WebSocket implementation for real-time deal updates |
| `schemas/` | Pydantic schemas for AI service |
| `services/` | Business logic services |
| `data/` | Data files and resources |

---

## Frontend (`frontend/`)

### Configuration Files
| File | Description |
|------|-------------|
| `package.json` | Node.js dependencies and scripts |
| `tsconfig.json` | TypeScript configuration |
| `tsconfig.node.json` | TypeScript configuration for Node.js tools |
| `vite.config.ts` | Vite build tool configuration |
| `tailwind.config.js` | Tailwind CSS configuration |
| `Dockerfile` | Docker image for frontend service |
| `index.html` | HTML entry point |

### Source Code (`src/`)
| File/Directory | Description |
|----------------|-------------|
| `main.tsx` | React application entry point |
| `App.tsx` | Main React application component with routing |
| `index.css` | Global CSS styles |
| `components/` | Reusable React components |
| `components/Navbar.tsx` | Navigation bar component |
| `components/Footer.tsx` | Footer component |
| `pages/` | Page components |
| `pages/HomePage.tsx` | Home page component |
| `pages/LoginPage.tsx` | User login page |
| `pages/FlightsPage.tsx` | Flight search and booking page |
| `pages/HotelsPage.tsx` | Hotel search and booking page |
| `pages/CarsPage.tsx` | Car rental search and booking page |
| `pages/BookingsPage.tsx` | User bookings management page |
| `pages/ProfilePage.tsx` | User profile page |
| `pages/AdminDashboard.tsx` | Admin analytics dashboard |
| `services/` | API service clients |
| `assets/` | Static assets (images, icons, etc.) |
| `public/` | Public static files |

---

## Infrastructure & Configuration

### Docker (`docker/`)
| File | Description |
|------|-------------|
| `Dockerfile.service` | Docker image for backend microservices |
| `Dockerfile.ai` | Docker image for AI service |

### Docker Compose
| File | Description |
|------|-------------|
| `docker-compose.yml` | Complete orchestration of all services including: |
| | - Infrastructure: MySQL, MongoDB, Redis, Zookeeper, Kafka, Kafka UI |
| | - Backend Services: user, flight, hotel, car, billing, admin, search |
| | - AI Service |
| | - Frontend |

---

## Tests (`tests/`)

| File/Directory | Description |
|----------------|-------------|
| `__init__.py` | Package initialization |
| `conftest.py` | Pytest configuration and fixtures |
| `unit/` | Unit tests |
| `unit/test_validators.py` | Unit tests for validation functions |
| `integration/` | Integration tests |
| `integration/test_api.py` | API integration tests |
| `performance/` | Performance/load tests |
| `performance/load_test.py` | Locust load testing script |

---

## Documentation (`docs/`)

| File/Directory | Description |
|----------------|-------------|
| `api/README.md` | API documentation |
| `schemas/` | Schema documentation |

---

## Scripts (`scripts/`)

| File | Description |
|------|-------------|
| `init_databases.py` | Database initialization script for MySQL and MongoDB |

---

## Service Ports Reference

| Service | Port | Container Name |
|---------|------|----------------|
| User Service | 8001 | kayak_user_service |
| Flight Service | 8002 | kayak_flight_service |
| Hotel Service | 8003 | kayak_hotel_service |
| Car Service | 8004 | kayak_car_service |
| Billing Service | 8005 | kayak_billing_service |
| Admin Service | 8006 | kayak_admin_service |
| Search Service | 8007 | kayak_search_service |
| AI Service | 8008 | kayak_ai_service |
| Frontend | 3000 | kayak_frontend |
| MySQL | 3306 | kayak_mysql |
| MongoDB | 27017 | kayak_mongodb |
| Redis | 6379 | kayak_redis |
| Kafka | 9092, 29092 | kayak_kafka |
| Kafka UI | 8080 | kayak_kafka_ui |
| Zookeeper | 2181 | kayak_zookeeper |

---

## Technology Stack Summary

### Backend
- **Framework**: FastAPI
- **ORM**: SQLModel (MySQL), Motor (MongoDB)
- **Validation**: Pydantic v2
- **Messaging**: Apache Kafka (aiokafka)
- **Caching**: Redis (redis-py, aioredis)
- **Testing**: pytest, pytest-asyncio, locust

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Data Fetching**: Axios, React Query
- **Routing**: React Router DOM
- **Charts**: Recharts

### Infrastructure
- **Containerization**: Docker, Docker Compose
- **Databases**: MySQL 8, MongoDB 6, Redis 7
- **Message Broker**: Apache Kafka 7.5.0
- **Monitoring**: Kafka UI

### AI/ML
- **Framework**: LangChain
- **APIs**: OpenAI/Anthropic integration

---

## Quick Navigation

### To find specific functionality:
- **User Management**: `backend/services/user_service/`
- **Flight Operations**: `backend/services/flight_service/`
- **Hotel Operations**: `backend/services/hotel_service/`
- **Car Rentals**: `backend/services/car_service/`
- **Payment Processing**: `backend/services/billing_service/`
- **Admin Analytics**: `backend/services/admin_service/`
- **AI Features**: `ai_service/`
- **Frontend Pages**: `frontend/src/pages/`
- **Database Models**: `backend/models/`
- **API Schemas**: `backend/schemas/`
- **Kafka Configuration**: `backend/kafka/`
- **Shared Utilities**: `backend/common/`

---

*Last Updated: Generated automatically*
*Project: Kayak Travel Simulation System*
*Type: Distributed Systems Group Project*

