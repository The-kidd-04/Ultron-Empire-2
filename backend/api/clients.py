"""
Ultron Empire — Clients API
CRUD operations for client management.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from datetime import date

from backend.db.database import SessionLocal
from backend.db.models import Client

router = APIRouter()


class ClientCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    occupation: Optional[str] = None
    city: Optional[str] = None
    risk_profile: Optional[str] = None
    investment_horizon: Optional[int] = None
    total_investable_wealth: Optional[float] = None
    current_aum_with_us: Optional[float] = None
    annual_income: Optional[float] = None
    goals: Optional[list] = None
    holdings: Optional[list] = None
    family_members: Optional[list] = None
    notes: Optional[str] = None
    tags: Optional[list] = None
    communication_preference: Optional[str] = None


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    occupation: Optional[str] = None
    city: Optional[str] = None
    risk_profile: Optional[str] = None
    investment_horizon: Optional[int] = None
    total_investable_wealth: Optional[float] = None
    current_aum_with_us: Optional[float] = None
    annual_income: Optional[float] = None
    goals: Optional[list] = None
    holdings: Optional[list] = None
    notes: Optional[str] = None
    tags: Optional[list] = None


@router.get("")
async def list_clients(
    search: Optional[str] = None,
    risk_profile: Optional[str] = None,
    limit: int = Query(default=50, le=200),
):
    """List all clients with optional filtering."""
    session = SessionLocal()
    try:
        q = session.query(Client)
        if search:
            q = q.filter(Client.name.ilike(f"%{search}%"))
        if risk_profile:
            q = q.filter(Client.risk_profile == risk_profile)
        clients = q.order_by(Client.name).limit(limit).all()

        return [
            {
                "id": c.id,
                "name": c.name,
                "city": c.city,
                "risk_profile": c.risk_profile,
                "current_aum_with_us": c.current_aum_with_us,
                "tags": c.tags,
                "next_review_date": str(c.next_review_date) if c.next_review_date else None,
            }
            for c in clients
        ]
    finally:
        session.close()


@router.get("/{client_id}")
async def get_client(client_id: int):
    """Get full client details."""
    session = SessionLocal()
    try:
        client = session.query(Client).get(client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        return {
            "id": client.id,
            "name": client.name,
            "phone": client.phone,
            "email": client.email,
            "age": client.age,
            "occupation": client.occupation,
            "city": client.city,
            "risk_profile": client.risk_profile,
            "investment_horizon": client.investment_horizon,
            "total_investable_wealth": client.total_investable_wealth,
            "current_aum_with_us": client.current_aum_with_us,
            "annual_income": client.annual_income,
            "goals": client.goals,
            "holdings": client.holdings,
            "family_members": client.family_members,
            "notes": client.notes,
            "last_review_date": str(client.last_review_date) if client.last_review_date else None,
            "next_review_date": str(client.next_review_date) if client.next_review_date else None,
            "first_investment_date": str(client.first_investment_date) if client.first_investment_date else None,
            "tags": client.tags,
            "communication_preference": client.communication_preference,
        }
    finally:
        session.close()


@router.post("")
async def create_client(data: ClientCreate):
    """Create a new client."""
    session = SessionLocal()
    try:
        client = Client(**data.model_dump(exclude_none=True))
        session.add(client)
        session.commit()
        session.refresh(client)
        return {"id": client.id, "name": client.name, "status": "created"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.put("/{client_id}")
async def update_client(client_id: int, data: ClientUpdate):
    """Update client details."""
    session = SessionLocal()
    try:
        client = session.query(Client).get(client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        update_data = data.model_dump(exclude_none=True)
        for key, value in update_data.items():
            setattr(client, key, value)

        session.commit()
        return {"id": client.id, "status": "updated"}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@router.delete("/{client_id}")
async def delete_client(client_id: int):
    """Delete a client."""
    session = SessionLocal()
    try:
        client = session.query(Client).get(client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        session.delete(client)
        session.commit()
        return {"status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()
