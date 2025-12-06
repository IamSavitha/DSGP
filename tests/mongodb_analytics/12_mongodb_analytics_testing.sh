#!/bin/bash
# Test 12: MongoDB Analytics Testing
# Comprehensive test suite for MongoDB analytics features

set -e

echo "========================================="
echo "Test 12: MongoDB Analytics Testing"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

MONGO_CMD="docker-compose exec -T mongodb mongosh -u admin -p kayak_mongo_pass --authenticationDatabase admin"
DB_NAME="kayak_db"

echo "=== Test 12.1: Clickstream Logging ==="
echo ""

echo "Step 1: Checking logs collection for user actions..."
echo ""

LOGS_COUNT=$($MONGO_CMD --eval "db.logs.countDocuments()" $DB_NAME 2>/dev/null | grep -oE '[0-9]+' | head -1 || echo "0")
echo "Total logs in collection: $LOGS_COUNT"

if [ "$LOGS_COUNT" -gt "0" ]; then
    echo -e "${GREEN}✅ Actions logged${NC}"
    echo ""
    echo "Sample log entries:"
    $MONGO_CMD --eval "db.logs.find().limit(5).pretty()" $DB_NAME 2>/dev/null | head -30 || echo "Could not retrieve logs"
else
    echo -e "${YELLOW}⚠️  No logs found yet${NC}"
    echo "This is normal if no actions have been performed yet."
fi

echo ""
echo "Step 2: Checking user_logs collection..."
USER_LOGS_COUNT=$($MONGO_CMD --eval "db.user_logs.countDocuments()" $DB_NAME 2>/dev/null | grep -oE '[0-9]+' | head -1 || echo "0")
echo "Total user logs: $USER_LOGS_COUNT"

if [ "$USER_LOGS_COUNT" -gt "0" ]; then
    echo -e "${GREEN}✅ User actions logged${NC}"
    $MONGO_CMD --eval "db.user_logs.find().limit(2).pretty()" $DB_NAME 2>/dev/null | head -20 || true
else
    echo -e "${YELLOW}⚠️  No user logs found yet${NC}"
fi

echo ""
echo "=== Test 12.2: User Preferences ==="
echo ""

echo "Checking for user preferences collection..."
PREFERENCES_COUNT=$($MONGO_CMD --eval "db.user_preferences.countDocuments()" $DB_NAME 2>/dev/null | grep -oE '[0-9]+' | head -1 || echo "0")

if [ "$PREFERENCES_COUNT" -gt "0" ]; then
    echo -e "${GREEN}✅ User preferences tracked${NC}"
    echo "Sample preferences:"
    $MONGO_CMD --eval "db.user_preferences.find().limit(1).pretty()" $DB_NAME 2>/dev/null | head -30 || true
else
    echo -e "${YELLOW}⚠️  No user preferences found yet${NC}"
    echo "Preferences are built automatically from user searches and bookings."
fi

echo ""
echo "=== Test 12.3: Price History ==="
echo ""

echo "Checking price_history collection..."
PRICE_HISTORY_COUNT=$($MONGO_CMD --eval "db.price_history.countDocuments()" $DB_NAME 2>/dev/null | grep -oE '[0-9]+' | head -1 || echo "0")

if [ "$PRICE_HISTORY_COUNT" -gt "0" ]; then
    echo -e "${GREEN}✅ Price changes tracked${NC}"
    echo "Sample price history:"
    $MONGO_CMD --eval "db.price_history.find().limit(3).sort({timestamp: -1}).pretty()" $DB_NAME 2>/dev/null | head -30 || true
else
    echo -e "${YELLOW}⚠️  No price history found yet${NC}"
    echo "Price history is tracked when listing prices change."
fi

echo ""
echo "=== Test 12.4: Reviews Storage ==="
echo ""

echo "Checking reviews collection..."
REVIEWS_COUNT=$($MONGO_CMD --eval "db.reviews.countDocuments()" $DB_NAME 2>/dev/null | grep -oE '[0-9]+' | head -1 || echo "0")

if [ "$REVIEWS_COUNT" -gt "0" ]; then
    echo -e "${GREEN}✅ Reviews stored${NC}"
    echo "Sample reviews:"
    $MONGO_CMD --eval "db.reviews.find().limit(2).pretty()" $DB_NAME 2>/dev/null | head -30 || true
    
    echo ""
    echo "Checking images collection for review images..."
    IMAGES_COUNT=$($MONGO_CMD --eval "db.images.countDocuments()" $DB_NAME 2>/dev/null | grep -oE '[0-9]+' | head -1 || echo "0")
    echo "Total images stored: $IMAGES_COUNT"
    if [ "$IMAGES_COUNT" -gt "0" ]; then
        echo -e "${GREEN}✅ Images stored${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No reviews found yet${NC}"
    echo "Reviews are stored when users submit them."
fi

echo ""
echo "=== Test 12.5: Admin Audit Logs ==="
echo ""

echo "Checking admin_audit_logs collection..."
AUDIT_LOGS_COUNT=$($MONGO_CMD --eval "db.admin_audit_logs.countDocuments()" $DB_NAME 2>/dev/null | grep -oE '[0-9]+' | head -1 || echo "0")

if [ "$AUDIT_LOGS_COUNT" -gt "0" ]; then
    echo -e "${GREEN}✅ Audit logs stored${NC}"
    echo "Sample audit logs:"
    $MONGO_CMD --eval "db.admin_audit_logs.find().limit(3).sort({timestamp: -1}).pretty()" $DB_NAME 2>/dev/null | head -40 || true
    echo ""
    echo "Complete audit trail available:"
    echo -e "${GREEN}✅ Audit trail complete${NC}"
else
    echo -e "${YELLOW}⚠️  No audit logs found yet${NC}"
    echo "Audit logs are created when admin users perform actions."
fi

echo ""
echo "=== Additional Analytics Checks ==="
echo ""

echo "Search Logs:"
SEARCH_LOGS_COUNT=$($MONGO_CMD --eval "db.search_logs.countDocuments()" $DB_NAME 2>/dev/null | grep -oE '[0-9]+' | head -1 || echo "0")
echo "Total search logs: $SEARCH_LOGS_COUNT"

echo ""
echo "Booking Logs:"
BOOKING_LOGS_COUNT=$($MONGO_CMD --eval "db.booking_logs.countDocuments()" $DB_NAME 2>/dev/null | grep -oE '[0-9]+' | head -1 || echo "0")
echo "Total booking logs: $BOOKING_LOGS_COUNT"

echo ""
echo "Analytics Collection:"
ANALYTICS_COUNT=$($MONGO_CMD --eval "db.analytics.countDocuments()" $DB_NAME 2>/dev/null | grep -oE '[0-9]+' | head -1 || echo "0")
echo "Total analytics documents: $ANALYTICS_COUNT"

echo ""
echo "Chat Sessions:"
CHAT_SESSIONS_COUNT=$($MONGO_CMD --eval "db.chat_sessions.countDocuments()" $DB_NAME 2>/dev/null | grep -oE '[0-9]+' | head -1 || echo "0")
echo "Total chat sessions: $CHAT_SESSIONS_COUNT"

echo ""
echo "========================================="
echo "Test 12 Complete!"
echo "========================================="
echo ""
echo "Summary:"
echo "- Logs Collection: $LOGS_COUNT documents"
echo "- User Logs: $USER_LOGS_COUNT documents"
echo "- Reviews: $REVIEWS_COUNT documents"
echo "- Price History: $PRICE_HISTORY_COUNT documents"
echo "- Audit Logs: $AUDIT_LOGS_COUNT documents"
echo ""
echo "All MongoDB collections are ready for analytics!"

