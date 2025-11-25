"""
Car Service - Business logic for car rental operations.
"""
from sqlalchemy.orm import Session
from typing import Optional
import math

from ...models.mysql_models import Car
from ...schemas.car_schemas import CarCreate, CarUpdate, CarSearchParams, CarSearchResponse, CarResponse
from ...common.cache import RedisCache, CacheKeys


class CarService:
    def __init__(self, db: Session):
        self.db = db
        self.cache = RedisCache()
    
    def create_car(self, car_data: CarCreate) -> Car:
        car = Car(**car_data.model_dump())
        self.db.add(car)
        self.db.commit()
        self.db.refresh(car)
        return car
    
    def get_car(self, car_id: str) -> Optional[Car]:
        return self.db.query(Car).filter(Car.car_id == car_id).first()
    
    def update_car(self, car_id: str, car_data: CarUpdate) -> Optional[Car]:
        car = self.db.query(Car).filter(Car.car_id == car_id).first()
        if not car:
            return None
        
        for field, value in car_data.model_dump(exclude_unset=True).items():
            if hasattr(car, field):
                setattr(car, field, value)
        
        self.db.commit()
        self.db.refresh(car)
        return car
    
    def delete_car(self, car_id: str) -> bool:
        car = self.db.query(Car).filter(Car.car_id == car_id).first()
        if not car:
            return False
        car.is_active = False
        self.db.commit()
        return True
    
    def search_cars(self, params: CarSearchParams) -> CarSearchResponse:
        query = self.db.query(Car).filter(Car.is_active == True, Car.is_available == True)
        
        if params.city:
            query = query.filter(Car.city.ilike(f"%{params.city}%"))
        if params.car_type:
            query = query.filter(Car.car_type == params.car_type)
        if params.provider_name:
            query = query.filter(Car.provider_name.ilike(f"%{params.provider_name}%"))
        if params.min_price:
            query = query.filter(Car.daily_rental_price >= params.min_price)
        if params.max_price:
            query = query.filter(Car.daily_rental_price <= params.max_price)
        
        total_count = query.count()
        offset = (params.page - 1) * params.page_size
        cars = query.order_by(Car.daily_rental_price).offset(offset).limit(params.page_size).all()
        
        return CarSearchResponse(
            cars=[CarResponse.model_validate(c) for c in cars],
            total_count=total_count,
            page=params.page,
            page_size=params.page_size,
            total_pages=math.ceil(total_count / params.page_size) if total_count > 0 else 1,
            filters_applied=params.model_dump(exclude_none=True)
        )

