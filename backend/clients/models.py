"""
Ultron Empire — Client Data Models (Pydantic schemas for API validation)
"""

from pydantic import BaseModel
from typing import Optional
from datetime import date


class ClientGoal(BaseModel):
    name: str
    target: float  # in Cr
    years: int


class ClientHolding(BaseModel):
    product: str
    amount: float  # in Cr
    date: str


class FamilyMember(BaseModel):
    name: str
    relation: str
    age: int


class ClientProfile(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    occupation: Optional[str] = None
    city: Optional[str] = None
    risk_profile: Optional[str] = None  # Conservative, Moderate, Aggressive
    investment_horizon: Optional[int] = None
    total_investable_wealth: Optional[float] = None
    current_aum_with_us: Optional[float] = None
    annual_income: Optional[float] = None
    goals: Optional[list[ClientGoal]] = None
    holdings: Optional[list[ClientHolding]] = None
    family_members: Optional[list[FamilyMember]] = None
    notes: Optional[str] = None
    tags: Optional[list[str]] = None
    communication_preference: Optional[str] = None
