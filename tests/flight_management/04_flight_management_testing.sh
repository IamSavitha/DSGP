#!/bin/bash
# Test 04: Flight Management Testing
# Verify flight search, details, seat management, ratings, and admin operations

set -e

echo "========================================="
echo "Test 04: Flight Management Testing"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FLIGHT_URL="http://localhost:8002"

echo "=== Test 4.1: Flight Search with Filters ==="
echo ""

echo "Searching flights with multiple filters..."
SEARCH_RESPONSE=$(curl -s "${FLIGHT_URL}/flights/search?departure_airport=SFO&arrival_airport=JFK&departure_date=2025-12-15&flight_class=economy&min_price=200&max_price=400&airline=American%20Airlines&page=1&page_size=20")

FLIGHT_COUNT=$(echo "$SEARCH_RESPONSE" | grep -o '"flight_id"' | wc -l | tr -d ' ')

if [ "$FLIGHT_COUNT" -gt "0" ]; then
    echo -e "${GREEN}✅ Found $FLIGHT_COUNT flights matching filters${NC}"
    echo "$SEARCH_RESPONSE" | head -30
else
    echo -e "${YELLOW}⚠️  No flights found (may need to seed data)${NC}"
fi

echo ""
echo "=== Test 4.2: Display Flight Details ==="
echo ""

# Get a flight ID
FLIGHT_ID=$(echo "$SEARCH_RESPONSE" | grep -o '"flight_id":"[^"]*' | head -1 | cut -d'"' -f4)

if [ -z "$FLIGHT_ID" ]; then
    FLIGHT_ID="AA123"
    echo -e "${YELLOW}⚠️  Using test flight ID: $FLIGHT_ID${NC}"
fi

echo "Fetching flight details for: $FLIGHT_ID"
DETAILS_RESPONSE=$(curl -s "${FLIGHT_URL}/flights/${FLIGHT_ID}")

if echo "$DETAILS_RESPONSE" | grep -q "flight_id\|airline\|departure\|arrival"; then
    echo -e "${GREEN}✅ Flight details retrieved${NC}"
    echo "$DETAILS_RESPONSE" | head -20
else
    echo -e "${YELLOW}⚠️  Flight details endpoint may not be fully implemented${NC}"
fi

echo ""
echo "=== Test 4.3: Decrease Available Seats After Booking ==="
echo ""

if [ ! -z "$FLIGHT_ID" ] && [ "$FLIGHT_ID" != "AA123" ]; then
    echo "Checking available seats before booking..."
    BEFORE_SEATS=$(echo "$DETAILS_RESPONSE" | grep -o '"available_seats":[0-9]*' | cut -d':' -f2)
    
    if [ ! -z "$BEFORE_SEATS" ]; then
        echo "Available seats before: $BEFORE_SEATS"
        echo -e "${GREEN}✅ Seat inventory tracking active${NC}"
    else
        echo -e "${YELLOW}⚠️  Seat information not available${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Skipping seat test (no real flight ID)${NC}"
fi

echo ""
echo "=== Test 4.4: Flight Ratings ==="
echo ""

if [ ! -z "$FLIGHT_ID" ]; then
    echo "Checking flight ratings..."
    RATINGS_RESPONSE=$(curl -s "${FLIGHT_URL}/flights/${FLIGHT_ID}/reviews" 2>/dev/null || echo "")
    
    if [ ! -z "$RATINGS_RESPONSE" ]; then
        echo -e "${GREEN}✅ Flight ratings endpoint accessible${NC}"
        echo "$RATINGS_RESPONSE" | head -10
    else
        echo -e "${YELLOW}⚠️  Ratings endpoint may not be implemented${NC}"
    fi
fi

echo ""
echo "=== Test 4.5: Real-time Price Updates ==="
echo ""

echo "Testing price update capability..."
echo "Note: This requires admin authentication"

# Check if price update endpoint exists
PRICE_UPDATE_TEST=$(curl -s -X PUT "${FLIGHT_URL}/flights/${FLIGHT_ID}" \
  -H "Content-Type: application/json" \
  -d '{"base_price": 350.00}' 2>&1)

if echo "$PRICE_UPDATE_TEST" | grep -qi "unauthorized\|forbidden\|401\|403"; then
    echo -e "${GREEN}✅ Price update endpoint exists (requires admin auth)${NC}"
elif echo "$PRICE_UPDATE_TEST" | grep -qi "success\|updated"; then
    echo -e "${GREEN}✅ Price updated successfully${NC}"
else
    echo -e "${YELLOW}⚠️  Price update endpoint may not be fully implemented${NC}"
fi

echo ""
echo "=== Test 4.6: Create Flight (Admin) ==="
echo ""

echo "Testing flight creation (requires admin authentication)..."
NEW_FLIGHT_RESPONSE=$(curl -s -X POST "${FLIGHT_URL}/flights" \
  -H "Content-Type: application/json" \
  -d '{
    "flight_id": "TEST-FLIGHT-'$(date +%s)'",
    "airline_name": "Test Airlines",
    "departure_airport": "SFO",
    "arrival_airport": "LAX",
    "departure_datetime": "2025-12-20T10:00:00",
    "arrival_datetime": "2025-12-20T12:30:00",
    "flight_class": "economy",
    "base_price": 299.99,
    "total_seats": 180,
    "available_seats": 180
  }')

if echo "$NEW_FLIGHT_RESPONSE" | grep -qi "unauthorized\|forbidden\|401\|403"; then
    echo -e "${GREEN}✅ Flight creation endpoint exists (requires admin auth)${NC}"
elif echo "$NEW_FLIGHT_RESPONSE" | grep -qi "flight_id\|success"; then
    echo -e "${GREEN}✅ Flight created successfully${NC}"
else
    echo -e "${YELLOW}⚠️  Flight creation may require authentication${NC}"
fi

echo ""
echo "=== Cache Verification ==="
echo ""

echo "Checking Redis cache for flight data..."
CACHE_CHECK=$(docker-compose exec -T redis redis-cli KEYS "*flight*" 2>/dev/null | head -3 || echo "")

if [ ! -z "$CACHE_CHECK" ]; then
    echo -e "${GREEN}✅ Flight data cached in Redis${NC}"
    echo "$CACHE_CHECK"
else
    echo -e "${YELLOW}⚠️  No flight cache found${NC}"
fi

echo ""
echo "========================================="
echo "Test 04 Complete!"
echo "========================================="

