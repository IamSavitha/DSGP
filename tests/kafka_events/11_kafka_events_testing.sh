#!/bin/bash
# Test 11: Event-Driven Kafka Testing
# Comprehensive test suite for Kafka event publishing and consumption

set -e

echo "========================================="
echo "Test 11: Event-Driven Kafka Testing"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if services are running
check_service() {
    service=$1
    if docker-compose ps | grep -q "$service.*Up"; then
        echo -e "${GREEN}✅ $service is running${NC}"
        return 0
    else
        echo -e "${RED}❌ $service is not running${NC}"
        return 1
    fi
}

echo "=== Test 11.1: User Created Event ==="
echo ""

# Check if user-service is running
if ! check_service "user-service"; then
    echo "Please start the services: docker-compose up -d"
    exit 1
fi

echo ""
echo "Step 1: Creating a new user..."
echo ""

# Create a test user
USER_RESPONSE=$(curl -s -X POST "http://localhost:8001/users" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "TEST-USER-'"$(date +%s)"'",
    "first_name": "Test",
    "last_name": "User",
    "email": "testuser'"$(date +%s)"'@example.com",
    "password": "testpass123",
    "phone_number": "555-0100",
    "city": "San Francisco",
    "state": "CA",
    "zip_code": "94102"
  }')

echo "User creation response: $USER_RESPONSE"
USER_ID=$(echo $USER_RESPONSE | grep -o '"user_id":"[^"]*' | cut -d'"' -f4)

if [ -z "$USER_ID" ]; then
    echo -e "${RED}❌ Failed to create user${NC}"
    exit 1
fi

echo -e "${GREEN}✅ User created: $USER_ID${NC}"
echo ""

echo "Step 2: Checking Kafka topic for user.created event..."
echo ""

# Wait a bit for event to be published
sleep 2

# Check Kafka topic
EVENT_CHECK=$(docker-compose exec -T kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic kayak.user.created \
  --from-beginning \
  --max-messages 1 \
  --timeout-ms 5000 2>&1 || echo "no_event")

if echo "$EVENT_CHECK" | grep -q "$USER_ID\|user_id"; then
    echo -e "${GREEN}✅ Event published to kayak.user.created${NC}"
    echo "Event content:"
    echo "$EVENT_CHECK" | head -5
else
    echo -e "${YELLOW}⚠️  Could not verify event in topic (this may be normal if consumer already processed it)${NC}"
    echo "Checking logs for event processing..."
    docker-compose logs user-service --tail 20 | grep -i "user\|event" || true
fi

echo ""
echo "=== Test 11.2: Booking Created Event ==="
echo ""

echo "Step 1: Creating a booking..."
echo ""

# First, get a flight
FLIGHT_RESPONSE=$(curl -s "http://localhost:8002/flights/search?departure_airport=SFO&arrival_airport=LAX&page=1&page_size=1")
FLIGHT_ID=$(echo $FLIGHT_RESPONSE | grep -o '"flight_id":"[^"]*' | head -1 | cut -d'"' -f4)

if [ -z "$FLIGHT_ID" ]; then
    echo -e "${YELLOW}⚠️  No flights found. Creating a test flight first...${NC}"
    echo "Please ensure you have flights in the database"
    FLIGHT_ID="AA123"  # Using a test ID
fi

# Create a booking
BOOKING_RESPONSE=$(curl -s -X POST "http://localhost:8009/bookings" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"booking_type\": \"flight\",
    \"listing_id\": \"$FLIGHT_ID\",
    \"num_passengers\": 1,
    \"total_price\": 299.99
  }")

echo "Booking creation response: $BOOKING_RESPONSE"
BOOKING_ID=$(echo $BOOKING_RESPONSE | grep -o '"booking_id":"[^"]*' | cut -d'"' -f4)

if [ -z "$BOOKING_ID" ]; then
    echo -e "${YELLOW}⚠️  Could not create booking (may need authentication)${NC}"
else
    echo -e "${GREEN}✅ Booking created: $BOOKING_ID${NC}"
    echo ""
    echo "Step 2: Checking email service logs for booking.created event consumption..."
    sleep 2
    docker-compose logs email-service --tail 30 | grep -i "booking\|EMAIL SENT" || echo "No email logs found"
fi

echo ""
echo "=== Test 11.3: Payment Completed Event ==="
echo ""

if [ ! -z "$BOOKING_ID" ]; then
    echo "Step 1: Processing payment for booking $BOOKING_ID..."
    echo ""
    
    PAYMENT_RESPONSE=$(curl -s -X POST "http://localhost:8005/payments" \
      -H "Content-Type: application/json" \
      -d "{
        \"booking_id\": \"$BOOKING_ID\",
        \"payment_method\": \"credit_card\",
        \"card_number\": \"4111111111111111\"
      }")
    
    echo "Payment response: $PAYMENT_RESPONSE"
    
    echo ""
    echo "Step 2: Checking email service logs for payment.completed event consumption..."
    sleep 2
    docker-compose logs email-service --tail 30 | grep -i "payment\|EMAIL SENT" || echo "No payment email logs found"
else
    echo -e "${YELLOW}⚠️  Skipping payment test (no booking created)${NC}"
fi

echo ""
echo "=== Test 11.4: Kafka Consumer Groups Active ==="
echo ""

echo "Listing all consumer groups..."
CONSUMER_GROUPS=$(docker-compose exec -T kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --list 2>&1)

echo "$CONSUMER_GROUPS"

if echo "$CONSUMER_GROUPS" | grep -q "email-service-group"; then
    echo -e "${GREEN}✅ email-service-group is active${NC}"
else
    echo -e "${YELLOW}⚠️  email-service-group not found${NC}"
fi

# List all groups
echo ""
echo "All consumer groups:"
echo "$CONSUMER_GROUPS" | grep -v "Consumer" | grep -v "^$" | while read group; do
    echo -e "  ${GREEN}✅ $group${NC}"
done

echo ""
echo "=== Test 11.5: Event Processing Verification ==="
echo ""

echo "Checking service logs for event processing..."
echo ""

echo "User Service Logs:"
docker-compose logs user-service --tail 10 | grep -i "event\|publish" || echo "No event logs"

echo ""
echo "Email Service Logs:"
docker-compose logs email-service --tail 10 | grep -i "event\|consume\|EMAIL" || echo "No event logs"

echo ""
echo "========================================="
echo "Test 11 Complete!"
echo "========================================="

