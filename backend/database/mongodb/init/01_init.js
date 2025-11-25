// MongoDB Initialization Script
// Run with: mongosh < 01_init.js

// Switch to kayak database
db = db.getSiblingDB('kayak_db');

// ==================== Collections ====================

// Reviews Collection
db.createCollection('reviews');
db.reviews.createIndex({ "user_id": 1 });
db.reviews.createIndex({ "listing_id": 1 });
db.reviews.createIndex({ "listing_type": 1 });
db.reviews.createIndex({ "created_at": -1 });

// Images Collection
db.createCollection('images');
db.images.createIndex({ "listing_id": 1 });
db.images.createIndex({ "listing_type": 1 });

// Logs Collection
db.createCollection('logs');
db.logs.createIndex({ "timestamp": -1 });
db.logs.createIndex({ "user_id": 1 });
db.logs.createIndex({ "action": 1 });

// User Logs Collection
db.createCollection('user_logs');
db.user_logs.createIndex({ "user_id": 1 });
db.user_logs.createIndex({ "session_id": 1 });
db.user_logs.createIndex({ "timestamp": -1 });

// Search Logs Collection
db.createCollection('search_logs');
db.search_logs.createIndex({ "user_id": 1 });
db.search_logs.createIndex({ "search_type": 1 });
db.search_logs.createIndex({ "timestamp": -1 });

// Booking Logs Collection
db.createCollection('booking_logs');
db.booking_logs.createIndex({ "user_id": 1 });
db.booking_logs.createIndex({ "booking_id": 1 });
db.booking_logs.createIndex({ "timestamp": -1 });

// Analytics Collection
db.createCollection('analytics');
db.analytics.createIndex({ "metric_type": 1 });
db.analytics.createIndex({ "timestamp": -1 });
db.analytics.createIndex({ "period_type": 1 });

// Click Tracking Collection
db.createCollection('click_tracking');
db.click_tracking.createIndex({ "session_id": 1 });
db.click_tracking.createIndex({ "page_name": 1 });
db.click_tracking.createIndex({ "timestamp": -1 });

// User Journeys Collection
db.createCollection('user_journeys');
db.user_journeys.createIndex({ "user_id": 1 });
db.user_journeys.createIndex({ "session_id": 1 });
db.user_journeys.createIndex({ "conversion": 1 });

print("MongoDB collections and indexes created successfully!");

