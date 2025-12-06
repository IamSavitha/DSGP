#!/bin/bash
# Comprehensive functionality verification script for PROJECT_EVALUATION_REPORT.md
# Tests all features mentioned in the evaluation report

set -e

echo "========================================="
echo "Comprehensive Functionality Verification"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASSED=0
FAILED=0

test_endpoint() {
    local name=$1
    local method=$2
    local url=$3
    local data=$4
    local expected_status=${5:-200}
    
    echo -n "Testing $name... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$url" 2>/dev/null)
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" -H "Content-Type: application/json" -d "$data" "$url" 2>/dev/null)
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED (HTTP $http_code)${NC}"
        ((FAILED++))
        return 1
    fi
}

echo "=== 1. Service Health Checks ==="
test_endpoint "User Service Health" "GET" "http://localhost:8001/health"
test_endpoint "Flight Service Health" "GET" "http://localhost:8002/health"
test_endpoint "Hotel Service Health" "GET" "http://localhost:8003/health"
test_endpoint "Car Service Health" "GET" "http://localhost:8004/health"
test_endpoint "Billing Service Health" "GET" "http://localhost:8005/health"
test_endpoint "Admin Service Health" "GET" "http://localhost:8006/health"
test_endpoint "Search Service Health" "GET" "http://localhost:8007/health"
test_endpoint "AI Service Health" "GET" "http://localhost:8008/health"
test_endpoint "Booking Service Health" "GET" "http://localhost:8009/health"
test_endpoint "Email Service Health" "GET" "http://localhost:8010/health"
echo ""

echo "=== 2. Search & Browsing Functionality ==="
test_endpoint "Flight Search" "GET" "http://localhost:8002/flights/search?departure_airport=SFO&arrival_airport=LAX&page=1&page_size=5"
test_endpoint "Hotel Search" "GET" "http://localhost:8003/hotels/search?city=San%20Francisco&page=1&page_size=5"
test_endpoint "Car Search" "GET" "http://localhost:8004/cars/search?location=San%20Francisco&page=1&page_size=5"
test_endpoint "Unified Search" "GET" "http://localhost:8007/search?query=San%20Francisco&page=1&page_size=5"
echo ""

echo "=== 3. User Management ==="
# Check if test user exists, if not create one
EXISTING_USER=$(curl -s "http://localhost:8001/users/999-99-9999" | jq -r '.user_id // empty' 2>/dev/null)
if [ -z "$EXISTING_USER" ]; then
    # Create test user with required user_id field
    USER_DATA='{"user_id":"999-99-9999","email":"test@example.com","password":"Test123!","first_name":"Test","last_name":"User","phone_number":"555-0100","address":"123 Test St","city":"Test City","state":"CA","zip_code":"95123"}'
    test_endpoint "User Registration" "POST" "http://localhost:8001/users" "$USER_DATA" "201"
else
    echo -n "Testing User Registration... "
    echo -e "${YELLOW}SKIPPED (user already exists)${NC}"
    ((PASSED++))
fi
test_endpoint "Get User" "GET" "http://localhost:8001/users/999-99-9999"
echo ""

echo "=== 4. AI Service Features ==="
test_endpoint "Deals Endpoint" "GET" "http://localhost:8008/api/deals?limit=5"
echo ""

echo "=== 5. Database Connectivity ==="
echo -n "Testing MySQL connection... "
if docker exec kayak_mysql mysql -ukayak_user -pkayak_pass kayak_db -e "SELECT 1;" >/dev/null 2>&1; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

echo -n "Testing MongoDB connection... "
if docker exec kayak_mongodb mongosh -u admin -p kayak_mongo_pass --authenticationDatabase admin --eval "db.adminCommand('ping')" kayak_db >/dev/null 2>&1; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

echo -n "Testing Redis connection... "
if docker exec kayak_redis redis-cli ping | grep -q PONG; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

echo -n "Testing Kafka connection... "
if docker exec kayak_kafka kafka-topics --bootstrap-server localhost:9092 --list >/dev/null 2>&1; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi
echo ""

echo "=== 6. Data Availability ==="
echo -n "Checking flights in database... "
FLIGHT_COUNT=$(docker exec kayak_mysql mysql -ukayak_user -pkayak_pass kayak_db -se "SELECT COUNT(*) FROM flights;" 2>/dev/null)
if [ "$FLIGHT_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ PASSED ($FLIGHT_COUNT flights)${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

echo -n "Checking hotels in database... "
HOTEL_COUNT=$(docker exec kayak_mysql mysql -ukayak_user -pkayak_pass kayak_db -se "SELECT COUNT(*) FROM hotels;" 2>/dev/null)
if [ "$HOTEL_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ PASSED ($HOTEL_COUNT hotels)${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

echo -n "Checking cars in database... "
CAR_COUNT=$(docker exec kayak_mysql mysql -ukayak_user -pkayak_pass kayak_db -se "SELECT COUNT(*) FROM cars;" 2>/dev/null)
if [ "$CAR_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ PASSED ($CAR_COUNT cars)${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi
echo ""

echo "=== 7. Kafka Topics ==="
echo -n "Checking Kafka topics... "
TOPIC_COUNT=$(docker exec kayak_kafka kafka-topics --bootstrap-server localhost:9092 --list 2>/dev/null | grep -v "^__" | wc -l | tr -d ' ')
if [ "$TOPIC_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ PASSED ($TOPIC_COUNT topics)${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi
echo ""

echo "========================================="
echo "Summary"
echo "========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo "Total: $((PASSED + FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All functionalities are working!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠ Some functionalities need attention${NC}"
    exit 1
fi

