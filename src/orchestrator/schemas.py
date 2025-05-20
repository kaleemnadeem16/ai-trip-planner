from __future__ import annotations
from typing import List, Optional, Literal, Dict
from pydantic import BaseModel, Field, field_validator


class Money(BaseModel):
    amount: float
    currency: str = Field(description="ISO currency code, e.g., USD, EUR")


class Place(BaseModel):
    query: str
    lat: Optional[float] = None
    lon: Optional[float] = None


class POI(BaseModel):
    name: str
    category: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    open_hours: Optional[str] = None


class LegDates(BaseModel):
    fixed: Optional[List[str]] = Field(default=None, description="[start, end] ISO dates")
    duration_days: Optional[int] = None

    @field_validator("fixed")
    def validate_fixed(cls, v):
        if v is not None and len(v) != 2:
            raise ValueError("fixed must be [start, end]")
        return v


class LegRequest(BaseModel):
    from_place: Place = Field(..., alias="from")
    to_place: Place = Field(..., alias="to")
    dates: LegDates
    must_visit: Optional[List[POI]] = None
    budget: Optional[Money] = None


class Preferences(BaseModel):
    pace: Optional[Literal["easy", "normal", "packed"]] = "normal"
    interests: Optional[List[str]] = None
    mobility: Optional[str] = None
    accommodation_class: Optional[str] = None


class Constraints(BaseModel):
    must_visit_global: Optional[List[POI]] = None
    date_range: Optional[List[str]] = None


class TripRequest(BaseModel):
    origin: Optional[Place] = None
    detect_origin: bool = False
    legs: List[LegRequest]
    global_budget: Optional[Money] = None
    preferences: Optional[Preferences] = None
    constraints: Optional[Constraints] = None


class Weather(BaseModel):
    summary: str
    temp_c: float
    precip_prob: float


class ScheduledItem(BaseModel):
    kind: Literal["flight", "hotel", "activity", "transit", "meal", "buffer"]
    title: str
    start: str
    end: str
    tz: str
    location: Optional[Place] = None
    cost: Optional[Money] = None
    details: Optional[Dict] = None


class DayPlan(BaseModel):
    date: str
    segments: List[ScheduledItem]
    notes: Optional[str] = None
    weather: Optional[Weather] = None


class Itinerary(BaseModel):
    days: List[DayPlan]
    totals: Optional[Dict] = None
    artifacts: Optional[Dict] = None
