#!/bin/bash
# Verify Kafka topics and consumer groups

set -e

echo "=========================================="
echo "Kafka Events Verification"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check Kafka broker
echo ""
echo "--- Kafka Broker ---"
if docker-compose exec -T kafka kafka-broker-api-versions --bootstrap-server localhost:9092 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Kafka broker is accessible${NC}"
else
    echo -e "${RED}✗ Kafka broker is not accessible${NC}"
    exit 1
fi

# List topics
echo ""
echo "--- Kafka Topics ---"
echo "Listing all topics..."
TOPICS=$(docker-compose exec -T kafka kafka-topics --bootstrap-server localhost:9092 --list 2>/dev/null | grep -v "^__" || echo "")

if [ -z "$TOPICS" ]; then
    echo -e "${YELLOW}⚠ No topics found${NC}"
else
    echo "$TOPICS" | while read topic; do
        if [ ! -z "$topic" ]; then
            echo -e "  ${GREEN}✓${NC} ${topic}"
        fi
    done
fi

# Required topics from test plan
echo ""
echo "Checking required topics..."
REQUIRED_TOPICS=(
    "kayak.user.created"
    "kayak.booking.created"
    "kayak.booking.cancelled"
    "kayak.payment.completed"
    "kayak.payment.initiated"
)

for topic in "${REQUIRED_TOPICS[@]}"; do
    if echo "$TOPICS" | grep -q "^${topic}$"; then
        echo -e "  ${GREEN}✓${NC} ${topic} exists"
    else
        echo -e "  ${YELLOW}⚠${NC} ${topic} not found (may be auto-created)"
    fi
done

# Consumer groups
echo ""
echo "--- Kafka Consumer Groups ---"
GROUPS=$(docker-compose exec -T kafka kafka-consumer-groups --bootstrap-server localhost:9092 --list 2>/dev/null || echo "")

if [ -z "$GROUPS" ]; then
    echo -e "${YELLOW}⚠ No consumer groups found${NC}"
else
    echo "Active consumer groups:"
    echo "$GROUPS" | while read group; do
        if [ ! -z "$group" ]; then
            echo -e "  ${GREEN}✓${NC} ${group}"
            
            # Get consumer group details
            details=$(docker-compose exec -T kafka kafka-consumer-groups --bootstrap-server localhost:9092 --describe --group "$group" 2>/dev/null | head -3 || echo "")
            if [ ! -z "$details" ]; then
                echo "$details" | grep -E "TOPIC|PARTITION" | head -2 | sed 's/^/    /'
            fi
        fi
    done
fi

# Check email-service-group specifically
echo ""
echo "Checking email-service-group..."
if echo "$GROUPS" | grep -q "email-service-group"; then
    echo -e "${GREEN}✓${NC} email-service-group is active"
    docker-compose exec -T kafka kafka-consumer-groups --bootstrap-server localhost:9092 --describe --group email-service-group 2>/dev/null | head -5 | sed 's/^/  /' || true
else
    echo -e "${YELLOW}⚠${NC} email-service-group not found (email service may not be running)"
fi

echo ""
echo "=========================================="
echo "Kafka verification complete"
echo "=========================================="

