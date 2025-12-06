"""
Email Service - FastAPI application for email notification service.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging

from .consumer import EmailConsumerService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Email consumer instance
email_consumer: EmailConsumerService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    global email_consumer
    
    logger.info("Starting Email Service...")
    
    # Start email consumer
    email_consumer = EmailConsumerService()
    asyncio.create_task(email_consumer.start())
    
    logger.info("Email Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Email Service...")
    if email_consumer:
        await email_consumer.stop()


app = FastAPI(
    title="Kayak Email Service",
    description="Email notification microservice for Kayak simulation",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint with database connectivity checks."""
    from ...common.health import get_comprehensive_health
    health = await get_comprehensive_health(
        check_mysql=True,
        service_name="email-service"
    )
    # Add Kafka consumer status
    global email_consumer
    if email_consumer:
        health["checks"]["kafka_consumer"] = {
            "status": "healthy" if email_consumer.running else "unhealthy",
            "consumer_group": "email-service-group"
        }
    return health


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)

