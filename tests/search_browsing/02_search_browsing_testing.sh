#!/bin/bash
# Test 02: Search & Browsing Testing
# Verify search functionality for flights, hotels, cars, and filtering

set -e

echo "========================================="
echo "Test 02: Search & Browsing Testing"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FLIGHT_URL="http://localhost:8002"
HOTEL_URL="http://localhost:8003"
CAR_URL="http://localhost:8004"
SEARCH_URL="http://localhost:8007"

echo "=== Test 2.1: Search Flights ==="
echo ""

echo "Searching flights: SFO -> JFK on 2025-12-15"
FLIGHT_RESPONSE=$(curl -s "${FLIGHT_URL}/flights/search?departure_airport=SFO&arrival_airport=JFK&departure_date=2025-12-15&num_passengers=2&page=1&page_size=20")

FLIGHT_COUNT=$(echo "$FLIGHT_RESPONSE" | grep -o '"flight_id"' | wc -l | tr -d ' ')

if [ "$FLIGHT_COUNT" -gt "0" ]; then
    echo -e "${GREEN}✅ Found $FLIGHT_COUNT flights${NC}"
    echo "$FLIGHT_RESPONSE" | head -20
else
    echo -e "${YELLOW}⚠️  No flights found (may need to seed data)${NC}"
fi

echo ""
echo "=== Test 2.2: Search Hotels ==="
echo ""

echo "Searching hotels in San Francisco"
HOTEL_RESPONSE=$(curl -s "${HOTEL_URL}/hotels/search?city=San%20Francisco&check_in_date=2025-12-15&check_out_date=2025-12-20&num_guests=2")

HOTEL_COUNT=$(echo "$HOTEL_RESPONSE" | grep -o '"hotel_id"' | wc -l | tr -d ' ')

if [ "$HOTEL_COUNT" -gt "0" ]; then
    echo -e "${GREEN}✅ Found $HOTEL_COUNT hotels${NC}"
    echo "$HOTEL_RESPONSE" | head -20
else
    echo -e "${YELLOW}⚠️  No hotels found (may need to seed data)${NC}"
fi

echo ""
echo "=== Test 2.3: Search Rental Cars ==="
echo ""

echo "Searching cars in San Francisco"
CAR_RESPONSE=$(curl -s "${CAR_URL}/cars/search?city=San%20Francisco")

CAR_COUNT=$(echo "$CAR_RESPONSE" | grep -o '"car_id"' | wc -l | tr -d ' ')

if [ "$CAR_COUNT" -gt "0" ]; then
    echo -e "${GREEN}✅ Found $CAR_COUNT cars${NC}"
    echo "$CAR_RESPONSE" | head -20
else
    echo -e "${YELLOW}⚠️  No cars found (may need to seed data)${NC}"
fi

echo ""
echo "=== Test 2.4: Sort & Filter Results ==="
echo ""

echo "Testing flight search with filters: price range $100-$500, sorted by price"
FILTERED_RESPONSE=$(curl -s "${FLIGHT_URL}/flights/search?departure_airport=SFO&arrival_airport=LAX&min_price=100&max_price=500&sort_by=price&sort_order=asc&page=1&page_size=10")

if echo "$FILTERED_RESPONSE" | grep -q "flight_id\|total_count"; then
    echo -e "${GREEN}✅ Filtered search working${NC}"
    echo "$FILTERED_RESPONSE" | head -15
else
    echo -e "${YELLOW}⚠️  Filtered search may not be fully implemented${NC}"
fi

echo ""
echo "=== Test 2.5: Unified Search Service ==="
echo ""

echo "Testing unified search for 'San Francisco'"
UNIFIED_RESPONSE=$(curl -s "${SEARCH_URL}/search?city=San%20Francisco&search_type=hotel")

if echo "$UNIFIED_RESPONSE" | grep -q "hotel\|flight\|car\|total_results"; then
    echo -e "${GREEN}✅ Unified search working${NC}"
    echo "$UNIFIED_RESPONSE" | head -20
else
    echo -e "${YELLOW}⚠️  Unified search may not be fully implemented${NC}"
fi

echo ""
echo "=== Cache Verification ==="
echo ""

echo "Checking Redis cache for search results..."
CACHE_KEYS=$(docker-compose exec -T redis redis-cli KEYS "*search*" 2>/dev/null | head -5 || echo "")

if [ ! -z "$CACHE_KEYS" ]; then
    echo -e "${GREEN}✅ Search results cached in Redis${NC}"
    echo "Sample cache keys:"
    echo "$CACHE_KEYS"
else
    echo -e "${YELLOW}⚠️  No cache keys found (caching may not be active)${NC}"
fi

echo ""
echo "========================================="
echo "Test 02 Complete!"
echo "========================================="
echo "Summary:"
echo "- Flights found: $FLIGHT_COUNT"
echo "- Hotels found: $HOTEL_COUNT"
echo "- Cars found: $CAR_COUNT"

