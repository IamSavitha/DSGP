#!/bin/bash
# Script to create all Kafka topics for Kayak Simulation

set -e

KAFKA_CONTAINER="kafka"
BOOTSTRAP_SERVER="localhost:9092"
PARTITIONS=3
REPLICATION_FACTOR=1

echo "Creating Kafka topics for Kayak Simulation..."

# Function to create topic inside container
create_topic() {
    docker-compose exec -T $KAFKA_CONTAINER kafka-topics --create \
        --bootstrap-server $BOOTSTRAP_SERVER \
        --topic "$1" \
        --partitions $PARTITIONS \
        --replication-factor $REPLICATION_FACTOR \
        --if-not-exists 2>/dev/null && echo "✅ $1" || echo "⚠️  $1 (exists or error)"
}

# User Events
create_topic "kayak.user.created"
create_topic "kayak.user.updated"
create_topic "kayak.user.deleted"

# Search Events
create_topic "kayak.search.flight"
create_topic "kayak.search.hotel"
create_topic "kayak.search.car"

# Booking Events
create_topic "kayak.booking.created"
create_topic "kayak.booking.updated"
create_topic "kayak.booking.cancelled"
create_topic "kayak.booking.completed"

# Payment Events
create_topic "kayak.payment.initiated"
create_topic "kayak.payment.completed"
create_topic "kayak.payment.failed"
create_topic "kayak.payment.refunded"

# Listing Events
create_topic "kayak.listing.flight.created"
create_topic "kayak.listing.flight.updated"
create_topic "kayak.listing.hotel.created"
create_topic "kayak.listing.hotel.updated"
create_topic "kayak.listing.car.created"
create_topic "kayak.listing.car.updated"

# Review Events
create_topic "kayak.review.created"
create_topic "kayak.review.updated"
create_topic "kayak.review.deleted"

# Analytics Events
create_topic "kayak.analytics.pageview"
create_topic "kayak.analytics.click"
create_topic "kayak.analytics.search"

# AI Service Events
create_topic "kayak.ai.raw_supplier_feeds"
create_topic "kayak.ai.deals.normalized"
create_topic "kayak.ai.deals.scored"
create_topic "kayak.ai.deals.tagged"
create_topic "kayak.ai.deal.events"

# Notification Events
create_topic "kayak.notification.email"
create_topic "kayak.notification.sms"
create_topic "kayak.notification.push"

echo ""
echo "✅ Topic creation complete!"
echo ""
echo "Listing all Kayak topics:"
docker-compose exec -T $KAFKA_CONTAINER kafka-topics --list --bootstrap-server $BOOTSTRAP_SERVER 2>/dev/null | grep "^kayak\." | sort
