"""Export client data for backup."""

import json
from backend.db.database import SessionLocal
from backend.db.models import Client


def export_clients(output_file: str = "clients_backup.json"):
    session = SessionLocal()
    try:
        clients = session.query(Client).all()
        data = []
        for c in clients:
            data.append({
                "name": c.name, "phone": c.phone, "email": c.email,
                "age": c.age, "city": c.city, "risk_profile": c.risk_profile,
                "total_wealth": c.total_investable_wealth,
                "aum_with_us": c.current_aum_with_us,
                "holdings": c.holdings, "goals": c.goals, "tags": c.tags,
            })
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2, default=str)
        print(f"Exported {len(data)} clients to {output_file}")
    finally:
        session.close()


if __name__ == "__main__":
    export_clients()
