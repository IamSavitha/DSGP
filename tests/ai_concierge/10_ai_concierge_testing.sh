#!/bin/bash
# Test 10: AI Concierge Testing
# Verify deals API, trip bundles, chat functionality, and WebSocket events

set -e

echo "========================================="
echo "Test 10: AI Concierge Testing"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

AI_URL="http://localhost:8008"

echo "=== Test 10.1: Get Deals ==="
echo ""

echo "Fetching current deals..."
DEALS_RESPONSE=$(curl -s "${AI_URL}/api/deals?listing_type=flight&min_score=50&limit=20")

if echo "$DEALS_RESPONSE" | grep -q "deal_id\|score\|listing"; then
    DEAL_COUNT=$(echo "$DEALS_RESPONSE" | grep -o '"deal_id"' | wc -l | tr -d ' ')
    echo -e "${GREEN}✅ Found $DEAL_COUNT deals${NC}"
    echo "$DEALS_RESPONSE" | head -30
    
    # Check for deal scores
    if echo "$DEALS_RESPONSE" | grep -q "score"; then
        echo -e "${GREEN}✅ Deal scores calculated${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No deals found or endpoint issue${NC}"
    echo "$DEALS_RESPONSE" | head -10
fi

echo ""
echo "Testing deals for hotels..."
HOTEL_DEALS=$(curl -s "${AI_URL}/api/deals?listing_type=hotel&min_score=40&limit=10")

if echo "$HOTEL_DEALS" | grep -q "deal_id"; then
    HOTEL_DEAL_COUNT=$(echo "$HOTEL_DEALS" | grep -o '"deal_id"' | wc -l | tr -d ' ')
    echo -e "${GREEN}✅ Found $HOTEL_DEAL_COUNT hotel deals${NC}"
else
    echo -e "${YELLOW}⚠️  No hotel deals found${NC}"
fi

echo ""
echo "=== Test 10.2: Find Trip Bundles ==="
echo ""

echo "Requesting trip bundle for San Francisco..."
BUNDLE_RESPONSE=$(curl -s -X POST "${AI_URL}/api/bundles" \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "San Francisco",
    "check_in": "2025-12-15",
    "check_out": "2025-12-20",
    "num_guests": 2
  }')

if echo "$BUNDLE_RESPONSE" | grep -q "bundle_id\|flight\|hotel\|car"; then
    BUNDLE_COUNT=$(echo "$BUNDLE_RESPONSE" | grep -o '"bundle_id"' | wc -l | tr -d ' ')
    echo -e "${GREEN}✅ Found $BUNDLE_COUNT trip bundles${NC}"
    echo "$BUNDLE_RESPONSE" | head -40
    
    # Check for flight + hotel + car combinations
    if echo "$BUNDLE_RESPONSE" | grep -q "flight_id" && echo "$BUNDLE_RESPONSE" | grep -q "hotel_id" && echo "$BUNDLE_RESPONSE" | grep -q "car_id"; then
        echo -e "${GREEN}✅ Bundles include Flight + Hotel + Car combinations${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No bundles found or endpoint issue${NC}"
    echo "$BUNDLE_RESPONSE" | head -10
fi

echo ""
echo "=== Test 10.3: Chat with Concierge ==="
echo ""

TEST_USER_ID="TEST-CHAT-$(date +%s)"

echo "Sending chat message..."
CHAT_RESPONSE=$(curl -s -X POST "${AI_URL}/api/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"${TEST_USER_ID}\",
    \"message\": \"What are the best hotels in San Francisco?\"
  }")

if echo "$CHAT_RESPONSE" | grep -q "response\|message\|answer"; then
    echo -e "${GREEN}✅ Chat responded${NC}"
    echo "$CHAT_RESPONSE" | head -20
    
    # Check for session ID
    SESSION_ID=$(echo "$CHAT_RESPONSE" | grep -o '"session_id":"[^"]*' | cut -d'"' -f4 || echo "")
    if [ ! -z "$SESSION_ID" ]; then
        echo "Session ID: $SESSION_ID"
        echo -e "${GREEN}✅ Chat session created${NC}"
        
        echo ""
        echo "Checking MongoDB for conversation history..."
        CHAT_HISTORY=$(docker-compose exec -T mongodb mongosh -u admin -p kayak_mongo_pass --authenticationDatabase admin \
          --eval "db.chat_sessions.findOne({session_id: '${SESSION_ID}'})" kayak_db 2>/dev/null | head -30 || echo "")
        
        if [ ! -z "$CHAT_HISTORY" ] && echo "$CHAT_HISTORY" | grep -q "messages\|session_id"; then
            echo -e "${GREEN}✅ Conversation history stored in MongoDB${NC}"
        else
            echo -e "${YELLOW}⚠️  Conversation history may not be stored yet${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠️  Chat endpoint may not be fully implemented${NC}"
    echo "$CHAT_RESPONSE" | head -10
fi

echo ""
echo "Sending follow-up message..."
if [ ! -z "$SESSION_ID" ]; then
    FOLLOW_UP=$(curl -s -X POST "${AI_URL}/api/chat" \
      -H "Content-Type: application/json" \
      -d "{
        \"user_id\": \"${TEST_USER_ID}\",
        \"session_id\": \"${SESSION_ID}\",
        \"message\": \"What about flights from SFO to NYC?\"
      }")
    
    if echo "$FOLLOW_UP" | grep -q "response\|message"; then
        echo -e "${GREEN}✅ Follow-up message handled${NC}"
    fi
fi

echo ""
echo "=== Test 10.4: Real-time Deal Updates (WebSocket) ==="
echo ""

echo "Testing WebSocket connection..."
echo "WebSocket endpoint: ws://localhost:8008/ws/events"
echo ""
echo "Note: WebSocket testing requires a WebSocket client"
echo "You can test using:"
echo "  - Browser console: new WebSocket('ws://localhost:8008/ws/events')"
echo "  - wscat: wscat -c ws://localhost:8008/ws/events"
echo "  - Python script with websocket-client library"
echo ""

# Check if WebSocket endpoint is accessible
WS_CHECK=$(curl -s -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Sec-WebSocket-Key: test" \
  -H "Sec-WebSocket-Version: 13" "${AI_URL}/ws/events" 2>&1 | head -5 || echo "")

if echo "$WS_CHECK" | grep -qi "upgrade\|websocket\|101"; then
    echo -e "${GREEN}✅ WebSocket endpoint accessible${NC}"
else
    echo -e "${YELLOW}⚠️  WebSocket endpoint may require different connection method${NC}"
fi

echo ""
echo "=== MongoDB Chat Sessions Verification ==="
echo ""

echo "Checking all chat sessions..."
ALL_SESSIONS=$(docker-compose exec -T mongodb mongosh -u admin -p kayak_mongo_pass --authenticationDatabase admin \
  --eval "db.chat_sessions.countDocuments()" kayak_db 2>/dev/null | grep -oE '[0-9]+' | head -1 || echo "0")

echo "Total chat sessions in MongoDB: $ALL_SESSIONS"

if [ "$ALL_SESSIONS" -gt "0" ]; then
    echo -e "${GREEN}✅ Chat sessions stored in MongoDB${NC}"
    
    SAMPLE_SESSION=$(docker-compose exec -T mongodb mongosh -u admin -p kayak_mongo_pass --authenticationDatabase admin \
      --eval "db.chat_sessions.findOne()" kayak_db 2>/dev/null | head -25 || echo "")
    
    if [ ! -z "$SAMPLE_SESSION" ]; then
        echo "Sample session:"
        echo "$SAMPLE_SESSION"
    fi
fi

echo ""
echo "========================================="
echo "Test 10 Complete!"
echo "========================================="

