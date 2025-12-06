#!/usr/bin/env python3
"""
Database initialization script for Kayak Simulation.
Creates tables, collections, and seeds initial data.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from sqlalchemy import create_engine, text
from pymongo import MongoClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_mysql():
    """Initialize MySQL database."""
    from backend.common.config import settings
    from backend.common.database import engine, Base
    from backend.models import mysql_models  # Import to register models
    
    logger.info("Initializing MySQL database...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    logger.info("MySQL tables created successfully!")


def init_mongodb():
    """Initialize MongoDB collections."""
    from backend.common.config import settings
    
    logger.info("Initializing MongoDB collections...")
    
    client = MongoClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DATABASE]
    
    # Create collections with indexes
    collections = {
        'reviews': [
            ('user_id', 1),
            ('listing_id', 1),
            ('listing_type', 1),
            ('created_at', -1)
        ],
        'images': [
            ('listing_id', 1),
            ('listing_type', 1)
        ],
        'logs': [
            ('timestamp', -1),
            ('user_id', 1),
            ('action', 1)
        ],
        'user_logs': [
            ('user_id', 1),
            ('session_id', 1),
            ('timestamp', -1)
        ],
        'search_logs': [
            ('user_id', 1),
            ('search_type', 1),
            ('timestamp', -1)
        ],
        'analytics': [
            ('metric_type', 1),
            ('timestamp', -1)
        ]
    }
    
    for collection_name, indexes in collections.items():
        collection = db[collection_name]
        for index_field, direction in indexes:
            collection.create_index([(index_field, direction)])
        logger.info(f"Created collection: {collection_name}")
    
    client.close()
    logger.info("MongoDB collections created successfully!")


def seed_sample_data():
    """Seed sample data for testing."""
    from backend.common.config import settings
    from backend.common.database import SessionLocal
    from backend.models.mysql_models import User, Flight, Hotel, Car, Admin
    from passlib.context import CryptContext
    from datetime import datetime, timedelta
    import random
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    logger.info("Seeding sample data...")
    
    db = SessionLocal()
    
    try:
        # Sample Users
        users = [
            User(
                user_id=f"{random.randint(100,999)}-{random.randint(10,99)}-{random.randint(1000,9999)}",
                first_name=f"User{i}",
                last_name=f"Test{i}",
                email=f"user{i}@test.com",
                phone_number=f"555-{random.randint(100,999)}-{random.randint(1000,9999)}",
                city=random.choice(["San Francisco", "New York", "Los Angeles", "Chicago"]),
                state=random.choice(["CA", "NY", "IL", "TX"]),
                zip_code=f"{random.randint(10000, 99999)}",
                password_hash=pwd_context.hash("password123")
            )
            for i in range(10)
        ]
        
        for user in users:
            existing = db.query(User).filter(User.email == user.email).first()
            if not existing:
                db.add(user)
        
        # Sample Flights
        airlines = ["American Airlines", "United Airlines", "Delta", "Southwest", "JetBlue"]
        airports = ["SFO", "JFK", "LAX", "ORD", "DFW", "SEA", "BOS", "MIA"]
        
        for i in range(50):
            dep_airport = random.choice(airports)
            arr_airport = random.choice([a for a in airports if a != dep_airport])
            dep_time = datetime.now() + timedelta(days=random.randint(1, 60))
            
            flight = Flight(
                flight_id=f"{random.choice(['AA', 'UA', 'DL', 'SW', 'JB'])}{random.randint(100, 999)}",
                airline_name=random.choice(airlines),
                departure_airport=dep_airport,
                arrival_airport=arr_airport,
                departure_datetime=dep_time,
                arrival_datetime=dep_time + timedelta(hours=random.randint(2, 8)),
                duration_minutes=random.randint(120, 480),
                flight_class="economy",
                base_price=random.randint(150, 800),
                total_seats=random.randint(100, 300),
                available_seats=random.randint(10, 100),
                rating=round(random.uniform(3.5, 5.0), 1)
            )
            
            existing = db.query(Flight).filter(Flight.flight_id == flight.flight_id).first()
            if not existing:
                db.add(flight)
        
        # Sample Hotels
        hotel_names = ["Grand Plaza", "Marriott", "Hilton", "Hyatt", "Holiday Inn", 
                       "Best Western", "Sheraton", "Westin", "Four Seasons", "Ritz Carlton"]
        cities = ["San Francisco", "New York", "Los Angeles", "Chicago", "Miami",
                  "Seattle", "Boston", "Denver", "Austin", "San Diego"]
        
        for i in range(30):
            city = random.choice(cities)
            hotel = Hotel(
                hotel_id=f"HTL-{i+1:03d}",
                hotel_name=f"{random.choice(hotel_names)} {city}",
                address=f"{random.randint(100, 9999)} Main St",
                city=city,
                state=random.choice(["CA", "NY", "FL", "TX", "WA", "IL"]),
                zip_code=f"{random.randint(10000, 99999)}",
                star_rating=random.randint(3, 5),
                amenities="wifi,parking,pool,gym,breakfast",
                rating=round(random.uniform(3.5, 5.0), 1)
            )
            
            existing = db.query(Hotel).filter(Hotel.hotel_id == hotel.hotel_id).first()
            if not existing:
                db.add(hotel)
        
        # Sample Cars
        car_types = ["sedan", "suv", "compact", "luxury", "van"]
        providers = ["Enterprise", "Hertz", "Avis", "Budget", "National"]
        makes = ["Toyota", "Honda", "Ford", "Chevrolet", "BMW", "Mercedes"]
        
        for i in range(40):
            car = Car(
                car_id=f"CAR-{i+1:03d}",
                car_type=random.choice(car_types),
                make=random.choice(makes),
                model=f"Model-{random.randint(1, 10)}",
                year=random.randint(2020, 2025),
                provider_name=random.choice(providers),
                transmission_type=random.choice(["automatic", "manual"]),
                seats=random.choice([4, 5, 7, 8]),
                daily_rental_price=random.randint(40, 200),
                pickup_location=f"{random.choice(cities)} Airport",
                city=random.choice(cities),
                rating=round(random.uniform(3.5, 5.0), 1)
            )
            
            existing = db.query(Car).filter(Car.car_id == car.car_id).first()
            if not existing:
                db.add(car)
        
        db.commit()
        logger.info("Sample data seeded successfully!")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding data: {e}")
        raise
    finally:
        db.close()


def main():
    """Run database initialization."""
    logger.info("Starting database initialization...")
    
    # Initialize MySQL
    init_mysql()
    
    # Initialize MongoDB
    init_mongodb()
    
    # Seed sample data
    seed_sample_data()
    
    logger.info("Database initialization complete!")


if __name__ == "__main__":
    main()

