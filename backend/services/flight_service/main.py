"""
Flight Service - FastAPI application for flight management.
"""
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from decimal import Decimal
import logging

from ...common.config import settings
from ...common.database import get_mysql_session, init_mysql_db
from ...common.exceptions import handle_not_found
from ...schemas.flight_schemas import (
    FlightCreate, FlightUpdate, FlightResponse,
    FlightSearchParams, FlightSearchResponse
)
from .service import FlightService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Kayak Flight Service",
    description="Flight search and booking microservice for Kayak simulation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Starting Flight Service...")
    init_mysql_db()
    logger.info("Flight Service started successfully")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "flight-service"}


# ==================== Flight CRUD Endpoints ====================

@app.post("/flights", response_model=FlightResponse, status_code=status.HTTP_201_CREATED)
async def create_flight(
    flight_data: FlightCreate,
    db: Session = Depends(get_mysql_session)
):
    """Create a new flight listing."""
    service = FlightService(db)
    return service.create_flight(flight_data)


@app.get("/flights/{flight_id}", response_model=FlightResponse)
async def get_flight(
    flight_id: str,
    db: Session = Depends(get_mysql_session)
):
    """Get flight by ID."""
    service = FlightService(db)
    flight = service.get_flight(flight_id)
    if not flight:
        handle_not_found("Flight", flight_id)
    return flight


@app.put("/flights/{flight_id}", response_model=FlightResponse)
async def update_flight(
    flight_id: str,
    flight_data: FlightUpdate,
    db: Session = Depends(get_mysql_session)
):
    """Update flight information."""
    service = FlightService(db)
    flight = service.update_flight(flight_id, flight_data)
    if not flight:
        handle_not_found("Flight", flight_id)
    return flight


@app.delete("/flights/{flight_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flight(
    flight_id: str,
    db: Session = Depends(get_mysql_session)
):
    """Delete a flight listing."""
    service = FlightService(db)
    success = service.delete_flight(flight_id)
    if not success:
        handle_not_found("Flight", flight_id)


# ==================== Flight Search Endpoints ====================

@app.get("/flights/search", response_model=FlightSearchResponse)
async def search_flights(
    departure_airport: Optional[str] = Query(None, min_length=3, max_length=5),
    arrival_airport: Optional[str] = Query(None, min_length=3, max_length=5),
    departure_date: Optional[date] = None,
    return_date: Optional[date] = None,
    flight_class: Optional[str] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    airline_name: Optional[str] = None,
    min_departure_time: Optional[str] = None,
    max_departure_time: Optional[str] = None,
    num_passengers: int = Query(default=1, ge=1, le=9),
    sort_by: str = Query(default="price"),
    sort_order: str = Query(default="asc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_mysql_session)
):
    """Search for flights with filters."""
    service = FlightService(db)
    
    search_params = FlightSearchParams(
        departure_airport=departure_airport,
        arrival_airport=arrival_airport,
        departure_date=departure_date,
        return_date=return_date,
        flight_class=flight_class,
        min_price=Decimal(str(min_price)) if min_price else None,
        max_price=Decimal(str(max_price)) if max_price else None,
        airline_name=airline_name,
        min_departure_time=min_departure_time,
        max_departure_time=max_departure_time,
        num_passengers=num_passengers,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size
    )
    
    return service.search_flights(search_params)


@app.get("/flights/routes")
async def get_popular_routes(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_mysql_session)
):
    """Get popular flight routes."""
    service = FlightService(db)
    return service.get_popular_routes(limit)


@app.get("/flights/airlines")
async def get_airlines(
    db: Session = Depends(get_mysql_session)
):
    """Get list of all airlines."""
    service = FlightService(db)
    return service.get_airlines()


@app.get("/flights/{flight_id}/reviews")
async def get_flight_reviews(
    flight_id: str,
    db: Session = Depends(get_mysql_session)
):
    """Get reviews for a flight."""
    service = FlightService(db)
    flight = service.get_flight(flight_id)
    if not flight:
        handle_not_found("Flight", flight_id)
    return await service.get_flight_reviews(flight_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

