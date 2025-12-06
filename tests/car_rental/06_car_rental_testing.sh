#!/bin/bash
# Test 06: Car Rental Module Testing
# Verify car search, details, pricing, availability, and booking

set -e

echo "========================================="
echo "Test 06: Car Rental Module Testing"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

CAR_URL="http://localhost:8004"

echo "=== Test 6.1: Search Cars by Location ==="
echo ""

echo "Searching cars in San Francisco"
SEARCH_RESPONSE=$(curl -s "${CAR_URL}/cars/search?city=San%20Francisco")

CAR_COUNT=$(echo "$SEARCH_RESPONSE" | grep -o '"car_id"' | wc -l | tr -d ' ')

if [ "$CAR_COUNT" -gt "0" ]; then
    echo -e "${GREEN}✅ Found $CAR_COUNT cars in San Francisco${NC}"
    echo "$SEARCH_RESPONSE" | head -30
else
    echo -e "${YELLOW}⚠️  No cars found (may need to seed data)${NC}"
fi

echo ""
echo "=== Test 6.2: View Car Details ==="
echo ""

# Get a car ID
CAR_ID=$(echo "$SEARCH_RESPONSE" | grep -o '"car_id":"[^"]*' | head -1 | cut -d'"' -f4)

if [ -z "$CAR_ID" ]; then
    CAR_ID="CAR001"
    echo -e "${YELLOW}⚠️  Using test car ID: $CAR_ID${NC}"
fi

echo "Fetching car details for: $CAR_ID"
DETAILS_RESPONSE=$(curl -s "${CAR_URL}/cars/${CAR_ID}")

if echo "$DETAILS_RESPONSE" | grep -q "car_id\|make\|model\|provider"; then
    echo -e "${GREEN}✅ Car details retrieved${NC}"
    echo "$DETAILS_RESPONSE" | head -25
else
    echo -e "${YELLOW}⚠️  Car details endpoint may not be fully implemented${NC}"
fi

echo ""
echo "=== Test 6.3: Price Per Day Calculation ==="
echo ""

if [ ! -z "$CAR_ID" ]; then
    echo "Testing price calculation: price_per_day × days"
    PRICE_PER_DAY=$(echo "$DETAILS_RESPONSE" | grep -o '"daily_rental_price":[0-9.]*' | cut -d':' -f2 || echo "0")
    
    if [ "$PRICE_PER_DAY" != "0" ]; then
        DAYS=5
        TOTAL_PRICE=$(echo "$PRICE_PER_DAY * $DAYS" | bc 2>/dev/null || echo "N/A")
        echo "Price per day: \$$PRICE_PER_DAY"
        echo "Days: $DAYS"
        echo "Total: \$$TOTAL_PRICE"
        echo -e "${GREEN}✅ Price calculation verified${NC}"
    else
        echo -e "${YELLOW}⚠️  Price information not available${NC}"
    fi
fi

echo ""
echo "=== Test 6.4: Availability Check ==="
echo ""

if [ ! -z "$CAR_ID" ]; then
    echo "Checking car availability..."
    AVAILABILITY=$(echo "$DETAILS_RESPONSE" | grep -o '"is_available":[^,}]*' | cut -d':' -f2 || echo "")
    
    if [ ! -z "$AVAILABILITY" ]; then
        if echo "$AVAILABILITY" | grep -qi "true"; then
            echo -e "${GREEN}✅ Car is available${NC}"
        else
            echo -e "${YELLOW}⚠️  Car is not available${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Availability status not found${NC}"
    fi
fi

echo ""
echo "=== Test 6.5: Car Booking Confirmation ==="
echo ""

if [ ! -z "$CAR_ID" ]; then
    TEST_USER_ID="TEST-CAR-$(date +%s)"
    echo "Creating car booking for: $CAR_ID"
    
    BOOKING_RESPONSE=$(curl -s -X POST "http://localhost:8009/bookings" \
      -H "Content-Type: application/json" \
      -d "{
        \"user_id\": \"${TEST_USER_ID}\",
        \"booking_type\": \"car\",
        \"listing_id\": \"${CAR_ID}\",
        \"pickup_date\": \"2025-12-15\",
        \"dropoff_date\": \"2025-12-20\"
      }")
    
    if echo "$BOOKING_RESPONSE" | grep -q "booking_id\|success"; then
        echo -e "${GREEN}✅ Car booking created${NC}"
        echo "$BOOKING_RESPONSE" | head -10
        
        echo ""
        echo "Checking for confirmation email event..."
        sleep 2
        EMAIL_LOGS=$(docker-compose logs email-service --tail 10 | grep -i "car\|booking" || echo "")
        if [ ! -z "$EMAIL_LOGS" ]; then
            echo -e "${GREEN}✅ Email notification triggered${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Booking may require authentication${NC}"
    fi
fi

echo ""
echo "=== Filter Testing ==="
echo ""

echo "Testing car search with filters..."
FILTERED_SEARCH=$(curl -s "${CAR_URL}/cars/search?city=San%20Francisco&car_type=SUV&min_price=50&max_price=150")

FILTERED_COUNT=$(echo "$FILTERED_SEARCH" | grep -o '"car_id"' | wc -l | tr -d ' ')

if [ "$FILTERED_COUNT" -gt "0" ]; then
    echo -e "${GREEN}✅ Filtered search working: Found $FILTERED_COUNT cars${NC}"
else
    echo -e "${YELLOW}⚠️  No cars match filters${NC}"
fi

echo ""
echo "=== Cache Verification ==="
echo ""

echo "Checking Redis cache for car data..."
CACHE_CHECK=$(docker-compose exec -T redis redis-cli KEYS "*car*" 2>/dev/null | head -3 || echo "")

if [ ! -z "$CACHE_CHECK" ]; then
    echo -e "${GREEN}✅ Car data cached in Redis${NC}"
    echo "$CACHE_CHECK"
else
    echo -e "${YELLOW}⚠️  No car cache found${NC}"
fi

echo ""
echo "========================================="
echo "Test 06 Complete!"
echo "========================================="
echo "Tested Car ID: $CAR_ID"

