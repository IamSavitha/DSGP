"""
Admin Service - FastAPI application for admin management and analytics.
"""
from fastapi import FastAPI, Depends, Query, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import logging

from ...common.database import get_mysql_session, init_mysql_db
from ...common.exceptions import handle_not_found

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Kayak Admin Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting Admin Service...")
    init_mysql_db()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "admin-service"}


# ==================== Analytics Endpoints ====================

@app.get("/analytics/revenue")
async def get_revenue_analytics(
    period: str = Query(default="monthly", description="daily, weekly, monthly, yearly"),
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_mysql_session)
):
    """Get revenue analytics."""
    from .service import AdminService
    return AdminService(db).get_revenue_analytics(period, year, month)


@app.get("/analytics/top-properties")
async def get_top_properties(
    limit: int = Query(default=10, ge=1, le=50),
    year: Optional[int] = None,
    db: Session = Depends(get_mysql_session)
):
    """Get top 10 properties by revenue."""
    from .service import AdminService
    return AdminService(db).get_top_properties(limit, year)


@app.get("/analytics/city-revenue")
async def get_city_revenue(
    year: Optional[int] = None,
    db: Session = Depends(get_mysql_session)
):
    """Get city-wise revenue."""
    from .service import AdminService
    return AdminService(db).get_city_revenue(year)


@app.get("/analytics/top-providers")
async def get_top_providers(
    limit: int = Query(default=10, ge=1, le=50),
    month: Optional[int] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_mysql_session)
):
    """Get top hosts/providers with maximum properties sold."""
    from .service import AdminService
    return AdminService(db).get_top_providers(limit, month, year)


@app.get("/analytics/page-clicks")
async def get_page_clicks(db: Session = Depends(get_mysql_session)):
    """Get clicks per page analytics."""
    from .service import AdminService
    return await AdminService(db).get_page_clicks()


@app.get("/analytics/user-journey/{user_id}")
async def get_user_journey(user_id: str, db: Session = Depends(get_mysql_session)):
    """Get user journey trace diagram data."""
    from .service import AdminService
    return await AdminService(db).get_user_journey(user_id)


@app.get("/analytics/cohort")
async def get_cohort_analysis(
    city: Optional[str] = None,
    state: Optional[str] = None,
    db: Session = Depends(get_mysql_session)
):
    """Get cohort analysis for users from specific location."""
    from .service import AdminService
    return await AdminService(db).get_cohort_analysis(city, state)


# ==================== User Management ====================

@app.get("/users")
async def list_all_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_mysql_session)
):
    """List all users (admin view)."""
    from .service import AdminService
    return AdminService(db).list_users(page, page_size, search)


@app.put("/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    is_active: bool,
    db: Session = Depends(get_mysql_session)
):
    """Activate/deactivate user account."""
    from .service import AdminService
    return AdminService(db).update_user_status(user_id, is_active)


# ==================== Listing Management ====================

@app.get("/listings")
async def list_all_listings(
    listing_type: Optional[str] = Query(None, description="flight, hotel, car"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_mysql_session)
):
    """List all listings."""
    from .service import AdminService
    return AdminService(db).list_listings(listing_type, page, page_size)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)

