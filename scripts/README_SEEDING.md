# Travel Data Seeding Guide

This guide explains how to seed flights, hotels, and cars data for the Kayak Simulation project.

## Quick Start

### Option 1: Use the Enhanced Seeding Script (Recommended - No Kaggle Required!)

**The script works perfectly without Kaggle!** It generates realistic data automatically.

```bash
# Run inside Docker container
docker-compose exec user-service python3 -c "
import sys
sys.path.insert(0, '/app')
exec(open('/app/scripts/seed_travel_data.py').read())
"

# Or run locally (requires Python dependencies)
python3 scripts/seed_travel_data.py
```

**Note**: You don't need Kaggle credentials! The script generates all data automatically.

### Option 2: Use Original Script

```bash
docker-compose exec user-service python3 /app/scripts/init_databases.py
```

## Features

### Enhanced Seeding Script (`seed_travel_data.py`)

✅ **Realistic Data Generation**
- Real airline codes and names (AA, UA, DL, SW, etc.)
- Major US airports with realistic routes
- Popular hotel chains (Marriott, Hilton, Hyatt, etc.)
- Real car makes and models (Toyota, Honda, BMW, etc.)
- Realistic pricing based on routes and types
- Proper enum values (ECONOMY, BUSINESS, FIRST)

✅ **Smart Calculations**
- Flight duration based on actual route distances
- Flight prices based on route popularity and class
- Hotel room prices based on room type
- Car prices based on car type

✅ **Kaggle Dataset Support** (Optional)
- Can integrate with Kaggle datasets
- Requires `kaggle` and `pandas` packages
- See `load_kaggle_dataset()` function

✅ **Comprehensive Coverage**
- 100 flights with realistic routes
- 50 hotels with multiple room types each
- 75 cars from various providers

## Data Generated

### Flights (100)
- **Airlines**: American, United, Delta, Southwest, JetBlue, etc.
- **Routes**: Major US airport pairs (SFO↔JFK, LAX↔ORD, etc.)
- **Classes**: Economy, Business, First
- **Dates**: 1-90 days from now
- **Prices**: $150-$800 (based on route and class)

### Hotels (50)
- **Chains**: Marriott, Hilton, Hyatt, Holiday Inn, etc.
- **Cities**: 15 major US cities
- **Room Types**: Standard, Deluxe, Suite, Presidential
- **Amenities**: WiFi, Parking, Pool, Gym, Breakfast, etc.
- **Ratings**: 3-5 stars

### Cars (75)
- **Providers**: Enterprise, Hertz, Avis, Budget, National, etc.
- **Makes**: Toyota, Honda, Ford, BMW, Mercedes, etc.
- **Types**: Compact, Sedan, SUV, Luxury, Van
- **Locations**: Major airport locations
- **Prices**: $30-$200/day

## Kaggle Dataset Integration

### Recommended Datasets

1. **Hotel Booking Demand**
   - Dataset: `jessemostipak/hotel-booking-demand`
   - Contains: Hotel bookings, cancellations, customer data

2. **Flight Prices**
   - Dataset: `shubhambathwal/flight-price-prediction`
   - Contains: Flight prices, routes, airlines

3. **Car Rental Data**
   - Search Kaggle for "car rental" or "vehicle rental"

### Using Kaggle Datasets

1. **Install Kaggle API**:
   ```bash
   pip install kaggle pandas
   ```

2. **Set up Kaggle credentials**:
   - Go to https://www.kaggle.com/account
   - Create API token
   - Place `kaggle.json` in `~/.kaggle/`

3. **Modify the script** to use Kaggle data:
   ```python
   # In seed_travel_data.py
   kaggle_data = load_kaggle_dataset('dataset-name', 'file.csv')
   if kaggle_data:
       # Process and seed from Kaggle data
   ```

## Web Scraping (Advanced)

⚠️ **Note**: Web scraping may violate terms of service. Use responsibly.

### Example Scraping Function (Commented Out)

```python
def scrape_flight_data():
    """Example: Scrape flight data from travel websites."""
    import requests
    from bs4 import BeautifulSoup
    
    # This is just an example - actual implementation depends on target site
    url = "https://example-travel-site.com/flights"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract flight data
    # ... parsing logic ...
    
    return flight_data
```

### Legal Considerations

- ✅ Check `robots.txt` before scraping
- ✅ Respect rate limits
- ✅ Don't overload servers
- ✅ Consider using APIs instead
- ❌ Don't scrape without permission

## Customization

### Adjust Counts

Edit `seed_travel_data.py`:

```python
def main():
    seed_flights(db, count=200)  # More flights
    seed_hotels(db, count=100)   # More hotels
    seed_cars(db, count=150)     # More cars
```

### Add Custom Data

```python
# Add custom airports
AIRPORTS['PDX'] = {'city': 'Portland', 'state': 'OR'}

# Add custom airlines
AIRLINES['AS'] = 'Alaska Airlines'

# Add custom hotel chains
HOTEL_CHAINS.append('Your Hotel Chain')
```

## Verification

After seeding, verify the data:

```bash
# Check flight count
docker-compose exec flight-service python3 -c "
from backend.common.database import SessionLocal
from backend.models.mysql_models import Flight, Hotel, Car
db = SessionLocal()
print(f'Flights: {db.query(Flight).count()}')
print(f'Hotels: {db.query(Hotel).count()}')
print(f'Cars: {db.query(Car).count()}')
db.close()
"

# Test API
curl "http://localhost:8002/flights/search?page=1&page_size=10"
```

## Troubleshooting

### Issue: Enum Value Error
**Solution**: The script uses proper enum values (ECONOMY, not economy)

### Issue: Duplicate IDs
**Solution**: The script checks for existing records before creating

### Issue: Database Connection Error
**Solution**: Ensure Docker containers are running:
```bash
docker-compose up -d
```

### Issue: No Data Appearing
**Solution**: 
1. Clear Redis cache: `docker-compose exec redis redis-cli FLUSHDB`
2. Check database: Verify records exist
3. Check API: Test endpoints directly

## Next Steps

1. ✅ Run seeding script
2. ✅ Verify data in database
3. ✅ Test search functionality
4. ✅ Check frontend displays data correctly

---

**Created**: Enhanced seeding script with realistic data generation
**Updated**: Support for Kaggle datasets and web scraping (optional)

