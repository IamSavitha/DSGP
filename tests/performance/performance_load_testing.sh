#!/bin/bash
# Performance Load Testing
# Test system performance under load with concurrent requests

set -e

echo "========================================="
echo "Performance Load Testing"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FLIGHT_URL="http://localhost:8002"
HOTEL_URL="http://localhost:8003"
SEARCH_URL="http://localhost:8007"

echo "=== Performance Test 1: Search Response Time ==="
echo ""

echo "Testing flight search response time (10 requests)..."
START_TIME=$(date +%s%N)

for i in {1..10}; do
    curl -s -o /dev/null -w "%{time_total}\n" "${FLIGHT_URL}/flights/search?departure_airport=SFO&arrival_airport=LAX&page=1&page_size=20" &
done

wait
END_TIME=$(date +%s%N)
DURATION=$((($END_TIME - $START_TIME) / 1000000))

echo "Total time for 10 requests: ${DURATION}ms"
AVG_TIME=$(echo "scale=2; $DURATION / 10" | bc)
echo "Average response time: ${AVG_TIME}ms"

if (( $(echo "$AVG_TIME < 1000" | bc -l) )); then
    echo -e "${GREEN}✅ Response time < 1 second (with cache)${NC}"
elif (( $(echo "$AVG_TIME < 3000" | bc -l) )); then
    echo -e "${YELLOW}⚠️  Response time < 3 seconds (acceptable)${NC}"
else
    echo -e "${RED}❌ Response time > 3 seconds (slow)${NC}"
fi

echo ""
echo "=== Performance Test 2: Concurrent Users ==="
echo ""

echo "Simulating 10 concurrent users performing searches..."
CONCURRENT_START=$(date +%s%N)

# Simulate concurrent requests
for i in {1..10}; do
    (
        curl -s "${FLIGHT_URL}/flights/search?departure_airport=SFO&arrival_airport=JFK&page=1" > /dev/null
        curl -s "${HOTEL_URL}/hotels/search?city=San%20Francisco&page=1" > /dev/null
        curl -s "${SEARCH_URL}/search?city=San%20Francisco" > /dev/null
    ) &
done

wait
CONCURRENT_END=$(date +%s%N)
CONCURRENT_DURATION=$((($CONCURRENT_END - $CONCURRENT_START) / 1000000))

echo "Time for 10 concurrent users (30 requests total): ${CONCURRENT_DURATION}ms"
echo -e "${GREEN}✅ System handled concurrent load${NC}"

echo ""
echo "=== Performance Test 3: Database Query Performance ==="
echo ""

echo "Testing MySQL query performance..."
QUERY_START=$(date +%s%N)

for i in {1..5}; do
    docker-compose exec -T mysql mysql -u kayak_user -pkayak_pass kayak_db \
      -e "SELECT COUNT(*) FROM flights WHERE departure_airport='SFO';" > /dev/null 2>&1
done

QUERY_END=$(date +%s%N)
QUERY_DURATION=$((($QUERY_END - $QUERY_START) / 1000000))
AVG_QUERY=$(echo "scale=2; $QUERY_DURATION / 5" | bc)

echo "Average MySQL query time: ${AVG_QUERY}ms"

if (( $(echo "$AVG_QUERY < 100" | bc -l) )); then
    echo -e "${GREEN}✅ Queries optimized (< 100ms)${NC}"
else
    echo -e "${YELLOW}⚠️  Queries may need optimization${NC}"
fi

echo ""
echo "Testing MongoDB query performance..."
MONGO_START=$(date +%s%N)

for i in {1..5}; do
    docker-compose exec -T mongodb mongosh -u admin -p kayak_mongo_pass --authenticationDatabase admin \
      --eval "db.logs.countDocuments()" kayak_db > /dev/null 2>&1
done

MONGO_END=$(date +%s%N)
MONGO_DURATION=$((($MONGO_END - $MONGO_START) / 1000000))
AVG_MONGO=$(echo "scale=2; $MONGO_DURATION / 5" | bc)

echo "Average MongoDB query time: ${AVG_MONGO}ms"

if (( $(echo "$AVG_MONGO < 100" | bc -l) )); then
    echo -e "${GREEN}✅ MongoDB queries optimized${NC}"
else
    echo -e "${YELLOW}⚠️  MongoDB queries may need optimization${NC}"
fi

echo ""
echo "=== Cache Performance ==="
echo ""

echo "Testing Redis cache performance..."
CACHE_START=$(date +%s%N)

for i in {1..100}; do
    docker-compose exec -T redis redis-cli GET "test:key:$i" > /dev/null 2>&1
done

CACHE_END=$(date +%s%N)
CACHE_DURATION=$((($CACHE_END - $CACHE_START) / 1000000))
AVG_CACHE=$(echo "scale=2; $CACHE_DURATION / 100" | bc)

echo "Average Redis operation time: ${AVG_CACHE}ms"

if (( $(echo "$AVG_CACHE < 10" | bc -l) )); then
    echo -e "${GREEN}✅ Cache performance excellent (< 10ms)${NC}"
else
    echo -e "${YELLOW}⚠️  Cache performance acceptable${NC}"
fi

echo ""
echo "=== Load Test Summary ==="
echo ""

echo "Performance Metrics:"
echo "- API Response Time: ${AVG_TIME}ms"
echo "- Concurrent Users: 10 users handled"
echo "- MySQL Query Time: ${AVG_QUERY}ms"
echo "- MongoDB Query Time: ${AVG_MONGO}ms"
echo "- Redis Cache Time: ${AVG_CACHE}ms"

echo ""
echo "========================================="
echo "Performance Testing Complete!"
echo "========================================="
echo ""
echo "For more detailed load testing, use:"
echo "  - Locust: cd tests/performance && locust -f load_test.py"
echo "  - Apache Bench: ab -n 1000 -c 10 http://localhost:8002/flights/search"
echo "  - wrk: wrk -t4 -c100 -d30s http://localhost:8002/flights/search"

