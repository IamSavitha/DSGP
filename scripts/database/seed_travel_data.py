#!/usr/bin/env python3
"""
Travel Data Seeding Script
Seeds flights, hotels, and cars with realistic data.
Supports:
- Kaggle dataset integration (optional)
- Realistic sample data generation
- Web scraping (optional, commented out)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from datetime import datetime, timedelta
from decimal import Decimal
import random
from typing import List, Optional

# Database imports
from backend.common.database import SessionLocal
from backend.models.mysql_models import (
    Flight, Hotel, HotelRoom, Car,
    FlightClass, RoomType, CarType, TransmissionType
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== Realistic Data Sources ====================

# Real airline codes and names
AIRLINES = {
    'AA': 'American Airlines',
    'UA': 'United Airlines',
    'DL': 'Delta Air Lines',
    'SW': 'Southwest Airlines',
    'JB': 'JetBlue Airways',
    'AS': 'Alaska Airlines',
    'B6': 'JetBlue Airways',
    'WN': 'Southwest Airlines',
    'NK': 'Spirit Airlines',
    'F9': 'Frontier Airlines'
}

# Major US airports with realistic routes
AIRPORTS = {
    'SFO': {'city': 'San Francisco', 'state': 'CA'},
    'JFK': {'city': 'New York', 'state': 'NY'},
    'LAX': {'city': 'Los Angeles', 'state': 'CA'},
    'ORD': {'city': 'Chicago', 'state': 'IL'},
    'DFW': {'city': 'Dallas', 'state': 'TX'},
    'SEA': {'city': 'Seattle', 'state': 'WA'},
    'BOS': {'city': 'Boston', 'state': 'MA'},
    'MIA': {'city': 'Miami', 'state': 'FL'},
    'ATL': {'city': 'Atlanta', 'state': 'GA'},
    'DEN': {'city': 'Denver', 'state': 'CO'},
    'LAS': {'city': 'Las Vegas', 'state': 'NV'},
    'PHX': {'city': 'Phoenix', 'state': 'AZ'},
    'IAH': {'city': 'Houston', 'state': 'TX'},
    'CLT': {'city': 'Charlotte', 'state': 'NC'},
    'MSP': {'city': 'Minneapolis', 'state': 'MN'}
}

# Popular hotel chains
HOTEL_CHAINS = [
    'Marriott', 'Hilton', 'Hyatt', 'Holiday Inn', 'Best Western',
    'Sheraton', 'Westin', 'Four Seasons', 'Ritz Carlton', 'InterContinental',
    'Radisson', 'DoubleTree', 'Embassy Suites', 'Courtyard', 'Residence Inn'
]

# Popular car rental companies
CAR_PROVIDERS = [
    'Enterprise', 'Hertz', 'Avis', 'Budget', 'National',
    'Alamo', 'Thrifty', 'Dollar', 'Sixt', 'Europcar'
]

# Real car makes and models
CAR_MAKES_MODELS = {
    'Toyota': ['Camry', 'Corolla', 'RAV4', 'Highlander', 'Prius'],
    'Honda': ['Civic', 'Accord', 'CR-V', 'Pilot', 'Odyssey'],
    'Ford': ['Fusion', 'Escape', 'Explorer', 'F-150', 'Edge'],
    'Chevrolet': ['Malibu', 'Equinox', 'Tahoe', 'Silverado', 'Traverse'],
    'Nissan': ['Altima', 'Sentra', 'Rogue', 'Pathfinder', 'Murano'],
    'BMW': ['3 Series', '5 Series', 'X3', 'X5', 'X1'],
    'Mercedes-Benz': ['C-Class', 'E-Class', 'GLC', 'GLE', 'A-Class'],
    'Audi': ['A4', 'A6', 'Q5', 'Q7', 'A3']
}


# ==================== Flight Seeding ====================

def generate_flight_id(airline_code: str) -> str:
    """Generate realistic flight ID."""
    return f"{airline_code}{random.randint(100, 9999)}"


def calculate_flight_duration(dep_airport: str, arr_airport: str) -> int:
    """Calculate realistic flight duration in minutes based on route."""
    # Approximate flight times between major airports (in minutes)
    route_durations = {
        ('SFO', 'JFK'): 330, ('JFK', 'SFO'): 330,
        ('LAX', 'JFK'): 320, ('JFK', 'LAX'): 320,
        ('SFO', 'LAX'): 90, ('LAX', 'SFO'): 90,
        ('ORD', 'JFK'): 135, ('JFK', 'ORD'): 135,
        ('DFW', 'JFK'): 195, ('JFK', 'DFW'): 195,
        ('SEA', 'JFK'): 300, ('JFK', 'SEA'): 300,
        ('BOS', 'JFK'): 75, ('JFK', 'BOS'): 75,
        ('MIA', 'JFK'): 180, ('JFK', 'MIA'): 180,
    }
    
    route = (dep_airport, arr_airport)
    if route in route_durations:
        base_duration = route_durations[route]
    else:
        # Default: estimate based on distance (rough approximation)
        base_duration = random.randint(120, 480)
    
    # Add some variance
    return base_duration + random.randint(-30, 30)


def calculate_flight_price(dep_airport: str, arr_airport: str, duration: int, flight_class: str) -> Decimal:
    """Calculate realistic flight price."""
    # Base price per minute
    base_price_per_minute = {
        'ECONOMY': 1.5,
        'BUSINESS': 3.0,
        'FIRST': 5.0
    }
    
    base = duration * base_price_per_minute.get(flight_class, 1.5)
    
    # Popular routes are more expensive
    popular_routes = [('SFO', 'JFK'), ('LAX', 'JFK'), ('ORD', 'JFK')]
    if (dep_airport, arr_airport) in popular_routes:
        base *= 1.3
    
    # Add randomness
    price = base * random.uniform(0.8, 1.5)
    
    return Decimal(round(price, 2))


def seed_flights(db, count: int = 100):
    """Seed flights with realistic data."""
    logger.info(f"Seeding {count} flights...")
    
    airports = list(AIRPORTS.keys())
    airlines = list(AIRLINES.keys())
    flight_classes = [FlightClass.ECONOMY, FlightClass.BUSINESS, FlightClass.FIRST]
    
    created = 0
    for i in range(count):
        try:
            dep_airport = random.choice(airports)
            arr_airport = random.choice([a for a in airports if a != dep_airport])
            airline_code = random.choice(airlines)
            flight_class = random.choice(flight_classes)
            
            # Generate departure time (1-90 days from now)
            dep_time = datetime.now() + timedelta(
                days=random.randint(1, 90),
                hours=random.randint(6, 22),
                minutes=random.choice([0, 15, 30, 45])
            )
            
            # Calculate duration
            duration = calculate_flight_duration(dep_airport, arr_airport)
            arr_time = dep_time + timedelta(minutes=duration)
            
            # Calculate price
            price = calculate_flight_price(dep_airport, arr_airport, duration, flight_class.value)
            
            # Generate flight ID
            flight_id = generate_flight_id(airline_code)
            
            # Check if exists
            existing = db.query(Flight).filter(Flight.flight_id == flight_id).first()
            if existing:
                continue
            
            flight = Flight(
                flight_id=flight_id,
                airline_name=AIRLINES[airline_code],
                operator_name=AIRLINES[airline_code],
                departure_airport=dep_airport,
                arrival_airport=arr_airport,
                departure_datetime=dep_time,
                arrival_datetime=arr_time,
                duration_minutes=duration,
                flight_class=flight_class,
                base_price=price,
                total_seats=random.choice([150, 180, 200, 250, 300]),
                available_seats=random.randint(10, 150),
                rating=round(random.uniform(3.5, 5.0), 1),
                is_active=True
            )
            
            db.add(flight)
            created += 1
            
            if (i + 1) % 20 == 0:
                db.commit()
                logger.info(f"  Created {created} flights so far...")
        
        except Exception as e:
            logger.error(f"Error creating flight {i}: {e}")
            continue
    
    db.commit()
    logger.info(f"✅ Created {created} flights successfully!")


# ==================== Hotel Seeding ====================

def seed_hotels(db, count: int = 50):
    """Seed hotels with realistic data."""
    logger.info(f"Seeding {count} hotels...")
    
    cities = [
        ('San Francisco', 'CA', '94102'),
        ('New York', 'NY', '10001'),
        ('Los Angeles', 'CA', '90001'),
        ('Chicago', 'IL', '60601'),
        ('Miami', 'FL', '33101'),
        ('Seattle', 'WA', '98101'),
        ('Boston', 'MA', '02101'),
        ('Dallas', 'TX', '75201'),
        ('Denver', 'CO', '80201'),
        ('Las Vegas', 'NV', '89101'),
        ('Atlanta', 'GA', '30301'),
        ('Phoenix', 'AZ', '85001'),
        ('Houston', 'TX', '77001'),
        ('San Diego', 'CA', '92101'),
        ('Portland', 'OR', '97201')
    ]
    
    amenities_combos = [
        'wifi,parking,pool,gym,breakfast',
        'wifi,parking,pool,spa,restaurant',
        'wifi,breakfast,concierge,room-service',
        'wifi,parking,gym,business-center',
        'wifi,pool,beach-access,restaurant,bar'
    ]
    
    created = 0
    for i in range(count):
        try:
            city, state, zip_code = random.choice(cities)
            hotel_name = f"{random.choice(HOTEL_CHAINS)} {city}"
            
            hotel_id = f"HTL-{i+1:04d}"
            
            # Check if exists
            existing = db.query(Hotel).filter(Hotel.hotel_id == hotel_id).first()
            if existing:
                continue
            
            hotel = Hotel(
                hotel_id=hotel_id,
                hotel_name=hotel_name,
                description=f"Luxurious {hotel_name} located in the heart of {city}",
                address=f"{random.randint(100, 9999)} {random.choice(['Main St', 'Broadway', 'Park Ave', 'Market St', 'Ocean Dr'])}",
                city=city,
                state=state,
                zip_code=zip_code,
                star_rating=random.randint(3, 5),
                rating=round(random.uniform(3.5, 5.0), 1),
                total_reviews=random.randint(50, 2000),
                amenities=random.choice(amenities_combos),
                phone_number=f"{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}",
                email=f"info@{hotel_name.lower().replace(' ', '')}.com",
                website=f"www.{hotel_name.lower().replace(' ', '')}.com",
                is_active=True
            )
            
            db.add(hotel)
            
            # Create rooms for this hotel
            num_room_types = random.randint(2, 4)
            # Use only valid RoomType enum values: SINGLE, DOUBLE, SUITE, DELUXE
            all_room_types = [RoomType.SINGLE, RoomType.DOUBLE, RoomType.SUITE, RoomType.DELUXE]
            room_types = random.sample(all_room_types, min(num_room_types, len(all_room_types)))
            
            for room_type in room_types:
                price_multiplier = {
                    RoomType.SINGLE: 0.8,
                    RoomType.DOUBLE: 1.0,
                    RoomType.DELUXE: 1.5,
                    RoomType.SUITE: 2.0
                }
                
                base_price = Decimal(random.randint(80, 200)) * Decimal(price_multiplier[room_type])
                
                room = HotelRoom(
                    room_id=f"{hotel_id}-{room_type.value}-{random.randint(1, 999)}",
                    hotel_id=hotel_id,
                    room_type=room_type,
                    room_number=f"{random.randint(100, 999)}",
                    price_per_night=base_price,
                    max_occupancy=random.choice([2, 4, 6]),
                    total_rooms=random.randint(5, 20),
                    available_rooms=random.randint(1, 10),
                    is_active=True
                )
                
                db.add(room)
            
            created += 1
            
            if (i + 1) % 10 == 0:
                db.commit()
                logger.info(f"  Created {created} hotels so far...")
        
        except Exception as e:
            logger.error(f"Error creating hotel {i}: {e}")
            continue
    
    db.commit()
    logger.info(f"✅ Created {created} hotels with rooms successfully!")


# ==================== Car Seeding ====================

def seed_cars(db, count: int = 75):
    """Seed cars with realistic data."""
    logger.info(f"Seeding {count} cars...")
    
    cities = [
        ('San Francisco', 'CA', 'SFO Airport'),
        ('New York', 'NY', 'JFK Airport'),
        ('Los Angeles', 'CA', 'LAX Airport'),
        ('Chicago', 'IL', 'ORD Airport'),
        ('Miami', 'FL', 'MIA Airport'),
        ('Seattle', 'WA', 'SEA Airport'),
        ('Boston', 'MA', 'BOS Airport'),
        ('Dallas', 'TX', 'DFW Airport'),
        ('Denver', 'CO', 'DEN Airport'),
        ('Las Vegas', 'NV', 'LAS Airport')
    ]
    
    car_type_mapping = {
        CarType.COMPACT: {'price_range': (30, 60), 'seats': 4},
        CarType.SEDAN: {'price_range': (40, 80), 'seats': 5},
        CarType.SUV: {'price_range': (60, 120), 'seats': 7},
        CarType.LUXURY: {'price_range': (100, 200), 'seats': 5},
        CarType.VAN: {'price_range': (80, 150), 'seats': 8}
    }
    
    created = 0
    for i in range(count):
        try:
            city, state, pickup_location = random.choice(cities)
            provider = random.choice(CAR_PROVIDERS)
            make = random.choice(list(CAR_MAKES_MODELS.keys()))
            model = random.choice(CAR_MAKES_MODELS[make])
            car_type = random.choice(list(CarType))
            
            car_id = f"CAR-{i+1:04d}"
            
            # Check if exists
            existing = db.query(Car).filter(Car.car_id == car_id).first()
            if existing:
                continue
            
            type_info = car_type_mapping[car_type]
            daily_price = Decimal(random.randint(*type_info['price_range']))
            
            car = Car(
                car_id=car_id,
                car_type=car_type,
                make=make,
                model=model,
                year=random.randint(2020, 2025),
                provider_name=provider,
                transmission_type=random.choice([TransmissionType.AUTOMATIC, TransmissionType.MANUAL]),
                seats=type_info['seats'],
                doors=random.choice([2, 4]),
                daily_rental_price=daily_price,
                pickup_location=pickup_location,
                city=city,
                state=state,
                rating=round(random.uniform(3.5, 5.0), 1),
                total_reviews=random.randint(10, 500),
                is_available=random.choice([True, True, True, False]),  # 75% available
                is_active=True
            )
            
            db.add(car)
            created += 1
            
            if (i + 1) % 15 == 0:
                db.commit()
                logger.info(f"  Created {created} cars so far...")
        
        except Exception as e:
            logger.error(f"Error creating car {i}: {e}")
            continue
    
    db.commit()
    logger.info(f"✅ Created {created} cars successfully!")


# ==================== Kaggle Dataset Support (Optional) ====================

def load_kaggle_dataset(dataset_name: str, file_name: str) -> Optional[List[dict]]:
    """
    Load data from Kaggle dataset (OPTIONAL - not required for seeding).
    
    To use this function:
    1. Install: pip install kaggle pandas
    2. Get API token from https://www.kaggle.com/account
    3. Create ~/.kaggle/kaggle.json with your credentials:
       {"username":"your-username","key":"your-api-key"}
    4. Set permissions: chmod 600 ~/.kaggle/kaggle.json
    
    Usage:
        kaggle datasets download -d <dataset-name>
        # Then process the CSV file
    """
    try:
        import pandas as pd
        import kaggle
        
        # Download dataset
        kaggle.api.dataset_download_files(dataset_name, path='./data', unzip=True)
        
        # Load CSV
        df = pd.read_csv(f'./data/{file_name}')
        
        logger.info(f"Loaded {len(df)} records from Kaggle dataset")
        return df.to_dict('records')
    
    except ImportError:
        logger.warning("Kaggle library not installed. Skipping Kaggle dataset loading.")
        logger.info("Note: The script works fine without Kaggle - it generates realistic data automatically!")
        return None
    except FileNotFoundError:
        logger.warning("Kaggle credentials not found at ~/.kaggle/kaggle.json")
        logger.info("Note: The script works fine without Kaggle - it generates realistic data automatically!")
        logger.info("See scripts/KAGGLE_SETUP.md for setup instructions (optional)")
        return None
    except Exception as e:
        logger.warning(f"Error loading Kaggle dataset: {e}")
        logger.info("Note: The script works fine without Kaggle - it generates realistic data automatically!")
        return None


# ==================== Main Function ====================

def main():
    """Main seeding function."""
    logger.info("=" * 60)
    logger.info("Travel Data Seeding Script")
    logger.info("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Clear existing data (optional - comment out if you want to keep existing)
        # logger.info("Clearing existing data...")
        # db.query(Flight).delete()
        # db.query(HotelRoom).delete()
        # db.query(Hotel).delete()
        # db.query(Car).delete()
        # db.commit()
        
        # Seed data
        seed_flights(db, count=100)
        seed_hotels(db, count=50)
        seed_cars(db, count=75)
        
        # Verify counts
        flight_count = db.query(Flight).filter(Flight.is_active == True).count()
        hotel_count = db.query(Hotel).filter(Hotel.is_active == True).count()
        car_count = db.query(Car).filter(Car.is_active == True).count()
        
        logger.info("=" * 60)
        logger.info("Seeding Complete!")
        logger.info(f"  Flights: {flight_count}")
        logger.info(f"  Hotels: {hotel_count}")
        logger.info(f"  Cars: {car_count}")
        logger.info("=" * 60)
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

