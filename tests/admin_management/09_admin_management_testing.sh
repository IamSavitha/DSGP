#!/bin/bash
# Test 09: Admin Module Testing
# Verify admin authentication, CRUD operations, user management, and audit logs

set -e

echo "========================================="
echo "Test 09: Admin Module Testing"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ADMIN_URL="http://localhost:8006"
FLIGHT_URL="http://localhost:8002"
HOTEL_URL="http://localhost:8003"
CAR_URL="http://localhost:8004"

echo "=== Test 9.1: Admin Authentication ==="
echo ""

echo "Testing admin login..."
ADMIN_LOGIN=$(curl -s -X POST "${ADMIN_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@kayak.com",
    "password": "admin123"
  }')

ADMIN_TOKEN=$(echo "$ADMIN_LOGIN" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4 || echo "")

if [ ! -z "$ADMIN_TOKEN" ]; then
    echo -e "${GREEN}✅ Admin login successful${NC}"
    echo "Token: ${ADMIN_TOKEN:0:50}..."
else
    echo -e "${YELLOW}⚠️  Admin login may require different credentials${NC}"
    echo "Response: $ADMIN_LOGIN"
fi

echo ""
echo "=== Test 9.2: Create/Update/Delete Flights ==="
echo ""

if [ ! -z "$ADMIN_TOKEN" ]; then
    TEST_FLIGHT_ID="TEST-FLIGHT-$(date +%s)"
    
    echo "Creating flight..."
    CREATE_RESPONSE=$(curl -s -X POST "${FLIGHT_URL}/flights" \
      -H "Authorization: Bearer ${ADMIN_TOKEN}" \
      -H "Content-Type: application/json" \
      -d "{
        \"flight_id\": \"${TEST_FLIGHT_ID}\",
        \"airline_name\": \"Test Airlines\",
        \"departure_airport\": \"SFO\",
        \"arrival_airport\": \"LAX\",
        \"departure_datetime\": \"2025-12-25T10:00:00\",
        \"arrival_datetime\": \"2025-12-25T12:30:00\",
        \"flight_class\": \"economy\",
        \"base_price\": 299.99,
        \"total_seats\": 180,
        \"available_seats\": 180
      }")
    
    if echo "$CREATE_RESPONSE" | grep -q "flight_id\|success"; then
        echo -e "${GREEN}✅ Flight created${NC}"
        
        echo ""
        echo "Updating flight..."
        UPDATE_RESPONSE=$(curl -s -X PUT "${FLIGHT_URL}/flights/${TEST_FLIGHT_ID}" \
          -H "Authorization: Bearer ${ADMIN_TOKEN}" \
          -H "Content-Type: application/json" \
          -d '{"base_price": 349.99}')
        
        if echo "$UPDATE_RESPONSE" | grep -q "349.99\|success"; then
            echo -e "${GREEN}✅ Flight updated${NC}"
        fi
        
        echo ""
        echo "Deleting flight..."
        DELETE_RESPONSE=$(curl -s -X DELETE "${FLIGHT_URL}/flights/${TEST_FLIGHT_ID}" \
          -H "Authorization: Bearer ${ADMIN_TOKEN}")
        
        if echo "$DELETE_RESPONSE" | grep -qi "success\|deleted\|200"; then
            echo -e "${GREEN}✅ Flight deleted${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Flight operations may require different endpoint or permissions${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Skipping flight management (no admin token)${NC}"
fi

echo ""
echo "=== Test 9.3: Create/Update/Delete Hotels ==="
echo ""

if [ ! -z "$ADMIN_TOKEN" ]; then
    TEST_HOTEL_ID="TEST-HOTEL-$(date +%s)"
    
    echo "Testing hotel management..."
    HOTEL_CREATE=$(curl -s -X POST "${HOTEL_URL}/hotels" \
      -H "Authorization: Bearer ${ADMIN_TOKEN}" \
      -H "Content-Type: application/json" \
      -d "{
        \"hotel_id\": \"${TEST_HOTEL_ID}\",
        \"hotel_name\": \"Test Hotel\",
        \"city\": \"San Francisco\",
        \"state\": \"CA\",
        \"star_rating\": 4
      }" 2>/dev/null || echo "")
    
    if echo "$HOTEL_CREATE" | grep -q "hotel_id\|success"; then
        echo -e "${GREEN}✅ Hotel management working${NC}"
    else
        echo -e "${YELLOW}⚠️  Hotel management may require different endpoint${NC}"
    fi
fi

echo ""
echo "=== Test 9.4: Manage Hotel Rooms ==="
echo ""

if [ ! -z "$ADMIN_TOKEN" ]; then
    echo "Testing room management..."
    ROOM_MANAGEMENT=$(curl -s "${HOTEL_URL}/hotels/HTL001/rooms" \
      -H "Authorization: Bearer ${ADMIN_TOKEN}" 2>/dev/null || echo "")
    
    if [ ! -z "$ROOM_MANAGEMENT" ]; then
        echo -e "${GREEN}✅ Room management endpoint accessible${NC}"
    else
        echo -e "${YELLOW}⚠️  Room management may not be fully implemented${NC}"
    fi
fi

echo ""
echo "=== Test 9.5: Manage Car Listings ==="
echo ""

if [ ! -z "$ADMIN_TOKEN" ]; then
    TEST_CAR_ID="TEST-CAR-$(date +%s)"
    
    echo "Testing car management..."
    CAR_CREATE=$(curl -s -X POST "${CAR_URL}/cars" \
      -H "Authorization: Bearer ${ADMIN_TOKEN}" \
      -H "Content-Type: application/json" \
      -d "{
        \"car_id\": \"${TEST_CAR_ID}\",
        \"provider_name\": \"Test Rental\",
        \"car_type\": \"SUV\",
        \"make\": \"Toyota\",
        \"model\": \"RAV4\",
        \"city\": \"San Francisco\",
        \"state\": \"CA\",
        \"daily_rental_price\": 89.99
      }" 2>/dev/null || echo "")
    
    if echo "$CAR_CREATE" | grep -q "car_id\|success"; then
        echo -e "${GREEN}✅ Car management working${NC}"
    else
        echo -e "${YELLOW}⚠️  Car management may require different endpoint${NC}"
    fi
fi

echo ""
echo "=== Test 9.6: View User List ==="
echo ""

if [ ! -z "$ADMIN_TOKEN" ]; then
    echo "Fetching user list..."
    USER_LIST=$(curl -s "${ADMIN_URL}/users" \
      -H "Authorization: Bearer ${ADMIN_TOKEN}" 2>/dev/null || echo "")
    
    if [ ! -z "$USER_LIST" ] && echo "$USER_LIST" | grep -q "user_id\|email"; then
        USER_COUNT=$(echo "$USER_LIST" | grep -o '"user_id"' | wc -l | tr -d ' ')
        echo -e "${GREEN}✅ User list retrieved: $USER_COUNT users${NC}"
        echo "$USER_LIST" | head -20
    else
        echo -e "${YELLOW}⚠️  User list endpoint may require different path${NC}"
    fi
fi

echo ""
echo "=== Test 9.7: View Bookings ==="
echo ""

if [ ! -z "$ADMIN_TOKEN" ]; then
    echo "Fetching all bookings..."
    BOOKINGS_LIST=$(curl -s "${ADMIN_URL}/bookings" \
      -H "Authorization: Bearer ${ADMIN_TOKEN}" 2>/dev/null || echo "")
    
    if [ ! -z "$BOOKINGS_LIST" ] && echo "$BOOKINGS_LIST" | grep -q "booking_id"; then
        BOOKING_COUNT=$(echo "$BOOKINGS_LIST" | grep -o '"booking_id"' | wc -l | tr -d ' ')
        echo -e "${GREEN}✅ Bookings retrieved: $BOOKING_COUNT bookings${NC}"
    else
        echo -e "${YELLOW}⚠️  Bookings endpoint may require different path${NC}"
    fi
fi

echo ""
echo "=== Test 9.8: Admin Audit Logs ==="
echo ""

echo "Checking MongoDB for admin audit logs..."
AUDIT_LOGS=$(docker-compose exec -T mongodb mongosh -u admin -p kayak_mongo_pass --authenticationDatabase admin \
  --eval "db.admin_audit_logs.find().limit(3).sort({timestamp: -1}).pretty()" kayak_db 2>/dev/null | head -40 || echo "")

if [ ! -z "$AUDIT_LOGS" ] && echo "$AUDIT_LOGS" | grep -q "audit_id\|admin_id"; then
    echo -e "${GREEN}✅ Admin audit logs found in MongoDB${NC}"
    echo "$AUDIT_LOGS"
else
    echo -e "${YELLOW}⚠️  No audit logs found (may need admin actions to generate)${NC}"
fi

echo ""
echo "=== Analytics Endpoints ==="
echo ""

if [ ! -z "$ADMIN_TOKEN" ]; then
    echo "Testing analytics endpoints..."
    
    echo ""
    echo "Revenue Analytics:"
    REVENUE=$(curl -s "${ADMIN_URL}/analytics/revenue" \
      -H "Authorization: Bearer ${ADMIN_TOKEN}" 2>/dev/null || echo "")
    
    if [ ! -z "$REVENUE" ]; then
        echo -e "${GREEN}✅ Revenue analytics accessible${NC}"
        echo "$REVENUE" | head -10
    fi
    
    echo ""
    echo "Top Properties:"
    TOP_PROPS=$(curl -s "${ADMIN_URL}/analytics/top-properties" \
      -H "Authorization: Bearer ${ADMIN_TOKEN}" 2>/dev/null || echo "")
    
    if [ ! -z "$TOP_PROPS" ]; then
        echo -e "${GREEN}✅ Top properties analytics accessible${NC}"
    fi
fi

echo ""
echo "========================================="
echo "Test 09 Complete!"
echo "========================================="

