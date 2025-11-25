"""
Admin Service - Business logic for admin operations and analytics.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import Optional, List
from datetime import datetime
import math

from ...models.mysql_models import User, Flight, Hotel, Car, Booking, Billing
from ...common.database import get_async_mongodb, MongoCollections


class AdminService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_revenue_analytics(self, period: str, year: Optional[int], month: Optional[int]) -> dict:
        """Get revenue analytics by period."""
        query = self.db.query(
            func.sum(Billing.total_amount).label('total_revenue'),
            func.count(Billing.billing_id).label('total_transactions')
        )
        
        if year:
            query = query.filter(extract('year', Billing.transaction_date) == year)
        if month:
            query = query.filter(extract('month', Billing.transaction_date) == month)
        
        result = query.first()
        
        # Revenue by booking type
        by_type = self.db.query(
            Billing.booking_type,
            func.sum(Billing.total_amount).label('revenue'),
            func.count(Billing.billing_id).label('count')
        ).group_by(Billing.booking_type).all()
        
        return {
            "period": period,
            "total_revenue": float(result.total_revenue or 0),
            "total_transactions": result.total_transactions or 0,
            "by_type": [
                {"type": str(r.booking_type), "revenue": float(r.revenue), "count": r.count}
                for r in by_type
            ]
        }
    
    def get_top_properties(self, limit: int, year: Optional[int]) -> List[dict]:
        """Get top properties by revenue."""
        query = self.db.query(
            Booking.listing_id,
            Booking.booking_type,
            func.sum(Billing.total_amount).label('revenue'),
            func.count(Booking.booking_id).label('bookings')
        ).join(Billing, Booking.booking_id == Billing.booking_id)
        
        if year:
            query = query.filter(extract('year', Billing.transaction_date) == year)
        
        results = query.group_by(
            Booking.listing_id, Booking.booking_type
        ).order_by(func.sum(Billing.total_amount).desc()).limit(limit).all()
        
        return [
            {
                "listing_id": r.listing_id,
                "type": str(r.booking_type),
                "revenue": float(r.revenue),
                "bookings": r.bookings
            }
            for r in results
        ]
    
    def get_city_revenue(self, year: Optional[int]) -> List[dict]:
        """Get city-wise revenue."""
        # For hotels
        hotel_query = self.db.query(
            Hotel.city,
            func.sum(Billing.total_amount).label('revenue')
        ).join(
            Booking, Hotel.hotel_id == Booking.listing_id
        ).join(
            Billing, Booking.booking_id == Billing.booking_id
        ).filter(Booking.booking_type == 'hotel')
        
        if year:
            hotel_query = hotel_query.filter(extract('year', Billing.transaction_date) == year)
        
        results = hotel_query.group_by(Hotel.city).all()
        
        return [
            {"city": r.city, "revenue": float(r.revenue)}
            for r in results
        ]
    
    def get_top_providers(self, limit: int, month: Optional[int], year: Optional[int]) -> List[dict]:
        """Get top providers by sales."""
        # Airlines for flights
        query = self.db.query(
            Flight.airline_name.label('provider'),
            func.count(Booking.booking_id).label('sales'),
            func.sum(Billing.total_amount).label('revenue')
        ).join(
            Booking, Flight.flight_id == Booking.listing_id
        ).join(
            Billing, Booking.booking_id == Billing.booking_id
        ).filter(Booking.booking_type == 'flight')
        
        if year:
            query = query.filter(extract('year', Billing.transaction_date) == year)
        if month:
            query = query.filter(extract('month', Billing.transaction_date) == month)
        
        results = query.group_by(Flight.airline_name).order_by(
            func.sum(Billing.total_amount).desc()
        ).limit(limit).all()
        
        return [
            {"provider": r.provider, "sales": r.sales, "revenue": float(r.revenue)}
            for r in results
        ]
    
    async def get_page_clicks(self) -> List[dict]:
        """Get page click analytics from MongoDB."""
        db = get_async_mongodb()
        
        pipeline = [
            {"$group": {
                "_id": "$page_name",
                "clicks": {"$sum": 1}
            }},
            {"$sort": {"clicks": -1}},
            {"$limit": 20}
        ]
        
        results = await db[MongoCollections.LOGS].aggregate(pipeline).to_list(20)
        return [{"page": r["_id"], "clicks": r["clicks"]} for r in results]
    
    async def get_user_journey(self, user_id: str) -> dict:
        """Get user journey trace data."""
        db = get_async_mongodb()
        
        logs = await db[MongoCollections.USER_LOGS].find(
            {"user_id": user_id}
        ).sort("timestamp", 1).to_list(100)
        
        return {
            "user_id": user_id,
            "journey_steps": logs,
            "total_actions": len(logs)
        }
    
    async def get_cohort_analysis(self, city: Optional[str], state: Optional[str]) -> dict:
        """Get cohort analysis for users from specific location."""
        filters = {}
        if city:
            filters["user_city"] = city
        if state:
            filters["user_state"] = state
        
        db = get_async_mongodb()
        
        journeys = await db[MongoCollections.ANALYTICS].find(filters).to_list(100)
        
        return {
            "filters": {"city": city, "state": state},
            "total_users": len(journeys),
            "data": journeys
        }
    
    def list_users(self, page: int, page_size: int, search: Optional[str]) -> dict:
        """List all users with pagination."""
        query = self.db.query(User)
        
        if search:
            query = query.filter(
                User.email.ilike(f"%{search}%") |
                User.first_name.ilike(f"%{search}%") |
                User.last_name.ilike(f"%{search}%")
            )
        
        total = query.count()
        offset = (page - 1) * page_size
        users = query.offset(offset).limit(page_size).all()
        
        return {
            "users": [
                {
                    "user_id": u.user_id,
                    "name": f"{u.first_name} {u.last_name}",
                    "email": u.email,
                    "is_active": u.is_active,
                    "created_at": str(u.created_at)
                }
                for u in users
            ],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    def update_user_status(self, user_id: str, is_active: bool) -> dict:
        """Update user active status."""
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        user.is_active = is_active
        self.db.commit()
        
        return {"user_id": user_id, "is_active": is_active}
    
    def list_listings(self, listing_type: Optional[str], page: int, page_size: int) -> dict:
        """List all listings."""
        results = []
        offset = (page - 1) * page_size
        
        if not listing_type or listing_type == "flight":
            flights = self.db.query(Flight).offset(offset).limit(page_size).all()
            results.extend([{"type": "flight", "id": f.flight_id, "name": f.airline_name} for f in flights])
        
        if not listing_type or listing_type == "hotel":
            hotels = self.db.query(Hotel).offset(offset).limit(page_size).all()
            results.extend([{"type": "hotel", "id": h.hotel_id, "name": h.hotel_name} for h in hotels])
        
        if not listing_type or listing_type == "car":
            cars = self.db.query(Car).offset(offset).limit(page_size).all()
            results.extend([{"type": "car", "id": c.car_id, "name": f"{c.make} {c.model}"} for c in cars])
        
        return {"listings": results, "page": page, "page_size": page_size}

