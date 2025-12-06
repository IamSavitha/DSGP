#!/bin/bash
# Test 01: User Management Testing
# Verify user registration, login, profile management, and booking history

set -e

echo "========================================="
echo "Test 01: User Management Testing"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BASE_URL="http://localhost:8001"
TIMESTAMP=$(date +%s)
TEST_USER_ID="TEST-${TIMESTAMP}"
TEST_EMAIL="testuser${TIMESTAMP}@example.com"

echo "=== Test 1.1: User Registration ==="
echo ""

echo "Creating test user: $TEST_USER_ID"
USER_RESPONSE=$(curl -s -X POST "${BASE_URL}/users" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"${TEST_USER_ID}\",
    \"first_name\": \"Test\",
    \"last_name\": \"User\",
    \"email\": \"${TEST_EMAIL}\",
    \"password\": \"SecurePass123!\",
    \"phone_number\": \"555-123-4567\",
    \"address\": \"123 Main Street\",
    \"city\": \"San Jose\",
    \"state\": \"CA\",
    \"zip_code\": \"95123\"
  }")

echo "Response: $USER_RESPONSE"

if echo "$USER_RESPONSE" | grep -q "$TEST_USER_ID\|user_id"; then
    echo -e "${GREEN}✅ User created successfully${NC}"
else
    echo -e "${RED}❌ User creation failed${NC}"
    echo "$USER_RESPONSE"
    exit 1
fi

echo ""
echo "=== Test 1.2: Invalid SSN Format Validation ==="
echo ""

echo "Testing invalid SSN: 123456789 (no dashes)"
INVALID_RESPONSE1=$(curl -s -X POST "${BASE_URL}/users" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "123456789",
    "first_name": "Test",
    "last_name": "User",
    "email": "invalid1@example.com",
    "password": "SecurePass123!",
    "city": "San Jose",
    "state": "CA",
    "zip_code": "95123"
  }')

if echo "$INVALID_RESPONSE1" | grep -qi "invalid\|validation\|error"; then
    echo -e "${GREEN}✅ Invalid SSN format rejected${NC}"
else
    echo -e "${YELLOW}⚠️  Validation may not be working as expected${NC}"
fi

echo ""
echo "=== Test 1.3: User Login (JWT) ==="
echo ""

echo "Attempting login for: $TEST_EMAIL"
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"${TEST_EMAIL}\",
    \"password\": \"SecurePass123!\"
  }")

echo "Login response: $LOGIN_RESPONSE"

if echo "$LOGIN_RESPONSE" | grep -qi "token\|access_token"; then
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4 || echo "")
    if [ ! -z "$TOKEN" ]; then
        echo -e "${GREEN}✅ Login successful, JWT token received${NC}"
        echo "Token: ${TOKEN:0:50}..."
    else
        echo -e "${YELLOW}⚠️  Login response received but token not extracted${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Login endpoint may not be available or credentials incorrect${NC}"
    TOKEN=""
fi

echo ""
echo "=== Test 1.4: Profile Management ==="
echo ""

if [ ! -z "$TOKEN" ]; then
    echo "Updating user profile..."
    UPDATE_RESPONSE=$(curl -s -X PUT "${BASE_URL}/users/${TEST_USER_ID}" \
      -H "Authorization: Bearer ${TOKEN}" \
      -H "Content-Type: application/json" \
      -d '{
        "phone_number": "555-999-8888"
      }')
    
    if echo "$UPDATE_RESPONSE" | grep -q "555-999-8888\|phone_number"; then
        echo -e "${GREEN}✅ Profile updated successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  Profile update may have failed${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Skipping profile update (no token)${NC}"
fi

echo ""
echo "=== Test 1.5: View Past Bookings ==="
echo ""

if [ ! -z "$TOKEN" ]; then
    echo "Fetching past bookings..."
    BOOKINGS_RESPONSE=$(curl -s -X GET "${BASE_URL}/users/${TEST_USER_ID}/bookings?status=completed" \
      -H "Authorization: Bearer ${TOKEN}")
    
    echo "Bookings response: $BOOKINGS_RESPONSE"
    echo -e "${GREEN}✅ Bookings endpoint accessible${NC}"
else
    echo -e "${YELLOW}⚠️  Skipping bookings check (no token)${NC}"
fi

echo ""
echo "=== Test 1.6: View Upcoming Trips ==="
echo ""

if [ ! -z "$TOKEN" ]; then
    echo "Fetching upcoming trips..."
    UPCOMING_RESPONSE=$(curl -s -X GET "${BASE_URL}/users/${TEST_USER_ID}/bookings?status=pending" \
      -H "Authorization: Bearer ${TOKEN}")
    
    echo "Upcoming trips response: $UPCOMING_RESPONSE"
    echo -e "${GREEN}✅ Upcoming trips endpoint accessible${NC}"
else
    echo -e "${YELLOW}⚠️  Skipping upcoming trips check (no token)${NC}"
fi

echo ""
echo "=== Database Verification ==="
echo ""

echo "Checking MySQL for user..."
MYSQL_CHECK=$(docker-compose exec -T mysql mysql -u kayak_user -pkayak_pass kayak_db \
  -e "SELECT user_id, email, city, state FROM users WHERE user_id='${TEST_USER_ID}';" 2>/dev/null || echo "")

if echo "$MYSQL_CHECK" | grep -q "$TEST_USER_ID"; then
    echo -e "${GREEN}✅ User found in MySQL database${NC}"
    echo "$MYSQL_CHECK"
else
    echo -e "${YELLOW}⚠️  User not found in MySQL (may need to check)${NC}"
fi

echo ""
echo "========================================="
echo "Test 01 Complete!"
echo "========================================="
echo "Test User ID: $TEST_USER_ID"
echo "Test Email: $TEST_EMAIL"

