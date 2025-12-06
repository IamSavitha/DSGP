#!/bin/bash
# Verify database state and connectivity

set -e

echo "=========================================="
echo "Database State Verification"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# MySQL Verification
echo ""
echo "--- MySQL Database ---"
echo "Checking MySQL connection..."
if docker-compose exec -T mysql mysql -u kayak_user -pkayak_pass kayak_db -e "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ MySQL connection successful${NC}"
    
    echo "Checking tables..."
    TABLES=("users" "flights" "hotels" "hotel_rooms" "cars" "bookings" "billings")
    for table in "${TABLES[@]}"; do
        if docker-compose exec -T mysql mysql -u kayak_user -pkayak_pass kayak_db -e "SHOW TABLES LIKE '${table}';" | grep -q "${table}"; then
            count=$(docker-compose exec -T mysql mysql -u kayak_user -pkayak_pass kayak_db -e "SELECT COUNT(*) FROM ${table};" -s -N)
            echo -e "  ${GREEN}✓${NC} ${table}: ${count} records"
        else
            echo -e "  ${RED}✗${NC} ${table}: Table not found"
        fi
    done
else
    echo -e "${RED}✗ MySQL connection failed${NC}"
fi

# MongoDB Verification
echo ""
echo "--- MongoDB Database ---"
echo "Checking MongoDB connection..."
if docker-compose exec -T mongodb mongosh -u admin -p kayak_mongo_pass --authenticationDatabase admin --quiet --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ MongoDB connection successful${NC}"
    
    echo "Checking collections..."
    COLLECTIONS=("logs" "reviews" "admin_audit_logs" "user_preferences" "price_history")
    for collection in "${COLLECTIONS[@]}"; do
        count=$(docker-compose exec -T mongodb mongosh -u admin -p kayak_mongo_pass --authenticationDatabase admin --quiet --eval "db.${collection}.countDocuments()" kayak_db 2>/dev/null || echo "0")
        if [ "$count" != "0" ] || docker-compose exec -T mongodb mongosh -u admin -p kayak_mongo_pass --authenticationDatabase admin --quiet --eval "db.getCollectionNames()" kayak_db 2>/dev/null | grep -q "\"${collection}\""; then
            echo -e "  ${GREEN}✓${NC} ${collection}: ${count} documents"
        else
            echo -e "  ${YELLOW}⚠${NC} ${collection}: Collection exists but empty or not found"
        fi
    done
else
    echo -e "${RED}✗ MongoDB connection failed${NC}"
fi

# Redis Verification
echo ""
echo "--- Redis Cache ---"
echo "Checking Redis connection..."
if docker-compose exec -T redis redis-cli PING > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis connection successful${NC}"
    
    key_count=$(docker-compose exec -T redis redis-cli DBSIZE | tr -d '\r')
    echo "  Cache keys: ${key_count}"
    
    # Check for sample cache keys
    sample_keys=$(docker-compose exec -T redis redis-cli KEYS "kayak:*" | head -5 | wc -l | tr -d '\r')
    if [ "$sample_keys" -gt 0 ]; then
        echo -e "  ${GREEN}✓${NC} Found ${sample_keys} cache keys with 'kayak:' prefix"
    else
        echo -e "  ${YELLOW}⚠${NC} No cache keys found (cache may be empty)"
    fi
else
    echo -e "${RED}✗ Redis connection failed${NC}"
fi

echo ""
echo "=========================================="
echo "Database verification complete"
echo "=========================================="

