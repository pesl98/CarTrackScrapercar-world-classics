from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class Car:
    """Car data model"""
    id: Optional[int] = None
    autotrack_id: str = ''
    make: str = ''
    model: str = ''
    year: Optional[int] = None
    mileage: Optional[int] = None
    fuel_type: Optional[str] = None
    description: str = ''
    image_url: Optional[str] = None
    current_price: int = 0
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    is_sold: bool = False
    sold_date: Optional[datetime] = None
    days_on_market: Optional[float] = None

@dataclass
class PriceHistory:
    """Price history data model"""
    id: Optional[int] = None
    car_id: int = 0
    price: int = 0
    recorded_at: Optional[datetime] = None

@dataclass
class DashboardStats:
    """Dashboard statistics data model"""
    total_cars: int = 0
    active_cars: int = 0
    sold_cars: int = 0
    avg_days_on_market: float = 0.0
    recent_price_changes: int = 0
    avg_price: int = 0
