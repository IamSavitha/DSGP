#!/bin/bash

# Test 3.1: Flight Booking Creation
# This script verifies all components of the flight booking flow

echo "=========================================="
echo "Test 3.1: Flight Booking Creation"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check services
echo "1. Checking Services..."
echo "----------------------"

# Booking Service
if curl -s http://localhost:8009/health | grep -q "healthy"; then
    echo -e "${GREEN}✅ Booking Service: Running${NC}"
else
    echo -e "${RED}❌ Booking Service: Not Running${NC}"
    exit 1
fi

# Email Service
if curl -s http://localhost:8010/health | grep -q "healthy"; then
    echo -e "${GREEN}✅ Email Service: Running${NC}"
else
    echo -e "${RED}❌ Email Service: Not Running${NC}"
    exit 1
fi

# Kafka
if docker ps | grep -q kayak_kafka; then
    echo -e "${GREEN}✅ Kafka: Running${NC}"
else
    echo -e "${RED}❌ Kafka: Not Running${NC}"
    exit 1
fi

echo ""
echo "2. Checking Kafka Topics..."
echo "----------------------------"
TOPICS=$(docker exec kayak_kafka kafka-topics --bootstrap-server localhost:9092 --list 2>/dev/null | grep booking)
if echo "$TOPICS" | grep -q "kayak.booking.created"; then
    echo -e "${GREEN}✅ Topic 'kayak.booking.created' exists${NC}"
else
    echo -e "${RED}❌ Topic 'kayak.booking.created' not found${NC}"
fi

echo ""
echo "3. Checking Email Consumer..."
echo "-----------------------------"
EMAIL_LOGS=$(docker logs kayak_email_service 2>&1 | grep -i "consumer\|started" | tail -5)
if echo "$EMAIL_LOGS" | grep -qi "consumer started\|email service consumer"; then
    echo -e "${GREEN}✅ Email Consumer: Started${NC}"
    echo "$EMAIL_LOGS"
else
    echo -e "${YELLOW}⚠️  Email Consumer: Status unclear (check logs)${NC}"
    echo "Recent logs:"
    docker logs kayak_email_service --tail 5 2>&1
fi

echo ""
echo "4. Getting Sample Flight..."
echo "----------------------------"
FLIGHT_RESPONSE=$(curl -s "http://localhost:8002/flights/search?page=1&page_size=1")
if echo "$FLIGHT_RESPONSE" | grep -q "flight_id"; then
    FLIGHT_ID=$(echo "$FLIGHT_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['flights'][0]['flight_id'] if data.get('flights') else '')" 2>/dev/null)
    if [ -n "$FLIGHT_ID" ]; then
        echo -e "${GREEN}✅ Found flight: $FLIGHT_ID${NC}"
        
        # Get flight details
        FLIGHT_DETAILS=$(curl -s "http://localhost:8002/flights/$FLIGHT_ID")
        SEATS=$(echo "$FLIGHT_DETAILS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('available_seats', 0))" 2>/dev/null)
        echo "   Available seats: $SEATS"
    else
        echo -e "${RED}❌ No flights found${NC}"
    fi
else
    echo -e "${RED}❌ Failed to get flights${NC}"
fi

echo ""
echo "5. Manual Testing Instructions"
echo "-------------------------------"
echo "To complete the test:"
echo ""
echo "1. Open frontend: http://localhost:3000"
echo "2. Login with valid credentials"
echo "3. Go to Flights page: http://localhost:3000/flights"
echo "4. Search for flights (e.g., SFO → NYC)"
echo "5. Click 'Select Flight' on any flight"
echo "6. Click 'Confirm Booking' in the modal"
echo ""
echo "After booking, verify:"
echo ""
echo "a) Check booking in database:"
echo "   docker exec -it kayak_mysql mysql -ukayak_user -pkayak_pass kayak_db -e \\"
echo "     \"SELECT booking_id, status, total_price FROM bookings ORDER BY created_at DESC LIMIT 1;\""
echo ""
echo "b) Check seats decremented:"
echo "   docker exec -it kayak_mysql mysql -ukayak_user -pkayak_pass kayak_db -e \\"
echo "     \"SELECT flight_id, available_seats FROM flights WHERE flight_id='$FLIGHT_ID';\""
echo ""
echo "c) Check Kafka event:"
echo "   Open http://localhost:8080 (Kafka UI)"
echo "   Go to Topics → kayak.booking.created"
echo "   Check for new messages"
echo ""
echo "d) Check email service logs:"
echo "   docker logs kayak_email_service --tail 20 | grep -i booking"
echo ""

echo "=========================================="
echo "Test script complete!"
echo "=========================================="

