#!/bin/bash

# Script to check Redis cache for flight, hotel, and car search results
# Usage: ./scripts/check_redis_cache.sh [service]
# Example: ./scripts/check_redis_cache.sh flight

REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"

echo "=========================================="
echo "Redis Cache Checker for KAYAK Simulation"
echo "=========================================="
echo "Redis Host: $REDIS_HOST:$REDIS_PORT"
echo ""

# Check if Redis is accessible
if ! redis-cli -h $REDIS_HOST -p $REDIS_PORT ping > /dev/null 2>&1; then
    echo "❌ ERROR: Cannot connect to Redis at $REDIS_HOST:$REDIS_PORT"
    echo "Make sure Redis is running: docker-compose up -d redis"
    exit 1
fi

echo "✅ Redis connection successful"
echo ""

# Function to check cache keys
check_cache() {
    local pattern=$1
    local service_name=$2
    
    echo "--- $service_name Search Cache ---"
    keys=$(redis-cli -h $REDIS_HOST -p $REDIS_PORT KEYS "$pattern" 2>/dev/null)
    
    if [ -z "$keys" ]; then
        echo "  No cached results found for pattern: $pattern"
    else
        echo "  Found $(echo "$keys" | wc -l) cached key(s):"
        echo "$keys" | while read -r key; do
            if [ -n "$key" ]; then
                ttl=$(redis-cli -h $REDIS_HOST -p $REDIS_PORT TTL "$key" 2>/dev/null)
                size=$(redis-cli -h $REDIS_HOST -p $REDIS_PORT STRLEN "$key" 2>/dev/null)
                echo "    Key: $key"
                echo "      TTL: ${ttl}s (expires in ${ttl} seconds)"
                echo "      Size: ${size} bytes"
                
                # Show first 200 characters of cached value
                value=$(redis-cli -h $REDIS_HOST -p $REDIS_PORT GET "$key" 2>/dev/null)
                if [ -n "$value" ]; then
                    preview=$(echo "$value" | head -c 200)
                    echo "      Preview: ${preview}..."
                fi
                echo ""
            fi
        done
    fi
    echo ""
}

# Check all cache types
if [ -z "$1" ] || [ "$1" = "all" ]; then
    check_cache "kayak:flight_search:*" "Flight"
    check_cache "kayak:hotel_search:*" "Hotel"
    check_cache "kayak:car_search:*" "Car"
    check_cache "kayak:unified_search:*" "Unified Search"
elif [ "$1" = "flight" ]; then
    check_cache "kayak:flight_search:*" "Flight"
elif [ "$1" = "hotel" ]; then
    check_cache "kayak:hotel_search:*" "Hotel"
elif [ "$1" = "car" ]; then
    check_cache "kayak:car_search:*" "Car"
elif [ "$1" = "unified" ]; then
    check_cache "kayak:unified_search:*" "Unified Search"
else
    echo "Usage: $0 [flight|hotel|car|unified|all]"
    exit 1
fi

# Show all cache keys
echo "--- All Cache Keys ---"
all_keys=$(redis-cli -h $REDIS_HOST -p $REDIS_PORT KEYS "kayak:*" 2>/dev/null)
if [ -z "$all_keys" ]; then
    echo "  No keys found with prefix 'kayak:'"
else
    echo "  Total keys: $(echo "$all_keys" | wc -l)"
    echo "$all_keys" | head -20
    if [ $(echo "$all_keys" | wc -l) -gt 20 ]; then
        echo "  ... (showing first 20)"
    fi
fi

echo ""
echo "--- Cache Statistics ---"
info=$(redis-cli -h $REDIS_HOST -p $REDIS_PORT INFO stats 2>/dev/null)
keyspace_hits=$(echo "$info" | grep "keyspace_hits" | cut -d: -f2 | tr -d '\r')
keyspace_misses=$(echo "$info" | grep "keyspace_misses" | cut -d: -f2 | tr -d '\r')
if [ -n "$keyspace_hits" ] && [ -n "$keyspace_misses" ]; then
    total=$(($keyspace_hits + $keyspace_misses))
    if [ $total -gt 0 ]; then
        hit_rate=$(echo "scale=2; $keyspace_hits * 100 / $total" | bc)
        echo "  Cache Hits: $keyspace_hits"
        echo "  Cache Misses: $keyspace_misses"
        echo "  Hit Rate: ${hit_rate}%"
    fi
fi

echo ""
echo "=========================================="

