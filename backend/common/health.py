"""
Health check utilities for service health endpoints.
"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

from .database import engine, get_async_mongodb, get_sync_mongodb
from .cache import RedisCache
from .config import settings

logger = logging.getLogger(__name__)


async def check_mysql_health() -> Dict[str, Any]:
    """Check MySQL database connectivity."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        return {"status": "healthy", "database": "mysql"}
    except Exception as e:
        logger.error(f"MySQL health check failed: {e}")
        return {"status": "unhealthy", "database": "mysql", "error": str(e)}


async def check_mongodb_health() -> Dict[str, Any]:
    """Check MongoDB connectivity."""
    try:
        db = get_sync_mongodb()
        # Ping the database
        db.client.admin.command('ping')
        return {"status": "healthy", "database": "mongodb"}
    except Exception as e:
        logger.error(f"MongoDB health check failed: {e}")
        return {"status": "unhealthy", "database": "mongodb", "error": str(e)}


async def check_redis_health() -> Dict[str, Any]:
    """Check Redis connectivity."""
    try:
        cache = RedisCache()
        # Test connection
        cache.client.ping()
        return {"status": "healthy", "cache": "redis"}
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return {"status": "unhealthy", "cache": "redis", "error": str(e)}


async def get_comprehensive_health(
    check_mysql: bool = True,
    check_mongodb: bool = False,
    check_redis: bool = False,
    service_name: str = "service"
) -> Dict[str, Any]:
    """
    Get comprehensive health status for a service.
    
    Args:
        check_mysql: Whether to check MySQL connection
        check_mongodb: Whether to check MongoDB connection
        check_redis: Whether to check Redis connection
        service_name: Name of the service
    
    Returns:
        Dictionary with health status
    """
    health_status = {
        "status": "healthy",
        "service": service_name,
        "checks": {}
    }
    
    # Check MySQL
    if check_mysql:
        mysql_health = await check_mysql_health()
        health_status["checks"]["mysql"] = mysql_health
        if mysql_health["status"] != "healthy":
            health_status["status"] = "degraded"
    
    # Check MongoDB
    if check_mongodb:
        mongodb_health = await check_mongodb_health()
        health_status["checks"]["mongodb"] = mongodb_health
        if mongodb_health["status"] != "healthy":
            health_status["status"] = "degraded"
    
    # Check Redis
    if check_redis:
        redis_health = await check_redis_health()
        health_status["checks"]["redis"] = redis_health
        if redis_health["status"] != "healthy":
            health_status["status"] = "degraded"
    
    return health_status

