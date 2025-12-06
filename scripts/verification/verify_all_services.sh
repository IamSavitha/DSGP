#!/bin/bash
# Verify all services are running and healthy

set -e

echo "=========================================="
echo "Service Health Verification"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Service ports
SERVICES=(
    "8001:user-service"
    "8002:flight-service"
    "8003:hotel-service"
    "8004:car-service"
    "8005:billing-service"
    "8006:admin-service"
    "8007:search-service"
    "8008:ai-service"
    "8009:booking-service"
    "8010:email-service"
)

echo ""
echo "Checking Docker containers..."
docker-compose ps

echo ""
echo "Checking service health endpoints..."
echo ""

FAILED=0
PASSED=0

for service in "${SERVICES[@]}"; do
    IFS=':' read -r port name <<< "$service"
    url="http://localhost:${port}/health"
    
    echo -n "Checking ${name} (port ${port})... "
    
    if response=$(curl -s -w "\n%{http_code}" "${url}" 2>/dev/null); then
        http_code=$(echo "$response" | tail -n1)
        body=$(echo "$response" | sed '$d')
        
        if [ "$http_code" -eq 200 ]; then
            status=$(echo "$body" | grep -o '"status":"[^"]*"' | cut -d'"' -f4 || echo "unknown")
            if [ "$status" = "healthy" ] || [ "$status" = "degraded" ]; then
                echo -e "${GREEN}✓ Healthy${NC}"
                PASSED=$((PASSED + 1))
            else
                echo -e "${YELLOW}⚠ Status: ${status}${NC}"
                echo "  Response: $body"
                FAILED=$((FAILED + 1))
            fi
        else
            echo -e "${RED}✗ Failed (HTTP ${http_code})${NC}"
            FAILED=$((FAILED + 1))
        fi
    else
        echo -e "${RED}✗ Connection failed${NC}"
        FAILED=$((FAILED + 1))
    fi
done

echo ""
echo "=========================================="
echo "Summary: ${PASSED} passed, ${FAILED} failed"
echo "=========================================="

if [ $FAILED -eq 0 ]; then
    exit 0
else
    exit 1
fi

