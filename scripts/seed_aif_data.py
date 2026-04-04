"""Seed AIF data. AIF data is included in the main seed script."""

from backend.db.seed import seed_database

if __name__ == "__main__":
    seed_database()
