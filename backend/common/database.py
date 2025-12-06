"""
Database connection utilities for MySQL and MongoDB.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from contextlib import contextmanager
from typing import Generator
import logging

from .config import settings

logger = logging.getLogger(__name__)

# ==================== MySQL Configuration ====================

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    settings.MYSQL_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()


def get_mysql_session() -> Generator[Session, None, None]:
    """
    Get a MySQL database session.
    Use as a dependency in FastAPI endpoints.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_mysql_context() -> Generator[Session, None, None]:
    """
    Context manager for MySQL sessions.
    Use for background tasks or non-FastAPI code.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()


# ==================== MongoDB Configuration ====================

# Async MongoDB client (for FastAPI async endpoints)
async_mongo_client: AsyncIOMotorClient = None

# Sync MongoDB client (for background tasks)
sync_mongo_client: MongoClient = None


def get_async_mongodb():
    """Get async MongoDB database instance."""
    global async_mongo_client
    if async_mongo_client is None:
        async_mongo_client = AsyncIOMotorClient(settings.MONGODB_URI)
    return async_mongo_client[settings.MONGODB_DATABASE]


def get_sync_mongodb():
    """Get sync MongoDB database instance."""
    global sync_mongo_client
    if sync_mongo_client is None:
        sync_mongo_client = MongoClient(settings.MONGODB_URI)
    return sync_mongo_client[settings.MONGODB_DATABASE]


# Alias for convenience
def get_mongodb():
    """Get MongoDB database (async version)."""
    return get_async_mongodb()


# MongoDB Collections
class MongoCollections:
    """MongoDB collection names."""
    REVIEWS = "reviews"
    IMAGES = "images"
    LOGS = "logs"
    ANALYTICS = "analytics"
    USER_LOGS = "user_logs"
    SEARCH_LOGS = "search_logs"
    BOOKING_LOGS = "booking_logs"
    ADMIN_AUDIT_LOGS = "admin_audit_logs"
    CHAT_SESSIONS = "chat_sessions"
    USER_PREFERENCES = "user_preferences"
    PRICE_HISTORY = "price_history"


# ==================== Database Initialization ====================

def init_mysql_db():
    """Initialize MySQL database tables."""
    from ..models import mysql_models  # Import models to register them
    Base.metadata.create_all(bind=engine)
    logger.info("MySQL database tables created successfully")


async def init_mongodb():
    """Initialize MongoDB collections and indexes."""
    db = get_async_mongodb()
    
    # Create indexes for reviews collection
    await db[MongoCollections.REVIEWS].create_index("user_id")
    await db[MongoCollections.REVIEWS].create_index("listing_id")
    await db[MongoCollections.REVIEWS].create_index("listing_type")
    await db[MongoCollections.REVIEWS].create_index("created_at")
    
    # Create indexes for images collection
    await db[MongoCollections.IMAGES].create_index("listing_id")
    await db[MongoCollections.IMAGES].create_index("listing_type")
    
    # Create indexes for logs collection
    await db[MongoCollections.LOGS].create_index("timestamp")
    await db[MongoCollections.LOGS].create_index("user_id")
    await db[MongoCollections.LOGS].create_index("action")
    
    # Create indexes for analytics
    await db[MongoCollections.ANALYTICS].create_index("metric_type")
    await db[MongoCollections.ANALYTICS].create_index("timestamp")
    
    # Create indexes for chat sessions
    await db[MongoCollections.CHAT_SESSIONS].create_index("session_id", unique=True)
    await db[MongoCollections.CHAT_SESSIONS].create_index("user_id")
    await db[MongoCollections.CHAT_SESSIONS].create_index("started_at")
    await db[MongoCollections.CHAT_SESSIONS].create_index("last_activity")
    
    # Create indexes for user preferences
    await db[MongoCollections.USER_PREFERENCES].create_index("user_id", unique=True)
    
    # Create indexes for price history
    await db[MongoCollections.PRICE_HISTORY].create_index([("listing_id", 1), ("listing_type", 1)])
    await db[MongoCollections.PRICE_HISTORY].create_index("timestamp", -1)
    
    # Create indexes for admin audit logs
    await db[MongoCollections.ADMIN_AUDIT_LOGS].create_index("admin_id")
    await db[MongoCollections.ADMIN_AUDIT_LOGS].create_index("action_type")
    await db[MongoCollections.ADMIN_AUDIT_LOGS].create_index([("entity_type", 1), ("entity_id", 1)])
    await db[MongoCollections.ADMIN_AUDIT_LOGS].create_index("timestamp", -1)
    
    logger.info("MongoDB indexes created successfully")


def close_db_connections():
    """Close all database connections."""
    global async_mongo_client, sync_mongo_client
    
    if async_mongo_client:
        async_mongo_client.close()
        async_mongo_client = None
    
    if sync_mongo_client:
        sync_mongo_client.close()
        sync_mongo_client = None
    
    engine.dispose()
    logger.info("Database connections closed")

