#!/bin/bash
# Test 08: Email Notifications Testing
# Verify booking confirmation emails are sent via Kafka events

set -e

echo "========================================="
echo "Test 08: Email Notifications Testing"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=== Test 8.1: Booking Confirmation Email ==="
echo ""

echo "1. Recent Booking Confirmation Emails:"
echo "--------------------------------------"
EMAIL_LOGS=$(docker-compose logs email-service --since 2h 2>&1 | grep -E "EMAIL SENT|Sent booking confirmation" | tail -10)

if [ -z "$EMAIL_LOGS" ]; then
    echo -e "${YELLOW}⚠️  No recent email logs found${NC}"
    echo "This may be normal if no bookings were created recently."
else
    echo -e "${GREEN}✅ Email logs found:${NC}"
    echo "$EMAIL_LOGS"
fi

echo ""
echo "2. Kafka Consumer Status (Booking Created Events):"
echo "---------------------------------------------------"
CONSUMER_STATUS=$(docker-compose exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 --group email-service-group --describe 2>/dev/null | grep "kayak.booking.created" | head -3 || echo "")

if [ -z "$CONSUMER_STATUS" ]; then
    echo -e "${YELLOW}⚠️  Consumer group not active or no events processed${NC}"
else
    echo -e "${GREEN}✅ Consumer group active:${NC}"
    echo "$CONSUMER_STATUS"
fi

echo ""
echo "=== Test 8.2: Payment Confirmation Email ==="
echo ""

PAYMENT_LOGS=$(docker-compose logs email-service --since 2h 2>&1 | grep -E "payment.completed|payment confirmation" | tail -5)

if [ -z "$PAYMENT_LOGS" ]; then
    echo -e "${YELLOW}⚠️  No payment email logs found${NC}"
else
    echo -e "${GREEN}✅ Payment email logs found:${NC}"
    echo "$PAYMENT_LOGS"
fi

echo ""
echo "=== Test 8.3: Email Service Consumer Running ==="
echo ""

CONSUMER_GROUPS=$(docker-compose exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 --list 2>/dev/null || echo "")

if echo "$CONSUMER_GROUPS" | grep -q "email-service-group"; then
    echo -e "${GREEN}✅ email-service-group is active${NC}"
else
    echo -e "${RED}❌ email-service-group not found${NC}"
fi

echo ""
echo "3. To monitor in real-time, use:"
echo "   docker-compose logs -f email-service 2>&1 | grep -E 'EMAIL SENT|Sent booking confirmation'"

echo ""
echo "========================================="
echo "Test 08 Complete!"
echo "========================================="

