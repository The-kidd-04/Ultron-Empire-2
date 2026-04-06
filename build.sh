#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements-render.txt

# Initialize the SQLite database
python -c "
from backend.db.database import init_db
init_db()
print('Database initialized')
"

# Seed fund data (skip if already seeded)
python -c "
from backend.db.database import SessionLocal
from backend.db.models import FundData
session = SessionLocal()
count = session.query(FundData).count()
session.close()
if count == 0:
    print('Seeding fund data...')
    from scripts.seed_pms_data import seed_pms_data
    seed_pms_data()
    print('PMS data seeded')
    from scripts.seed_mf_data import seed_mf_data
    seed_mf_data()
    print('MF data seeded')
    from scripts.seed_aif_data import seed_aif_data
    seed_aif_data()
    print('AIF data seeded')
else:
    print(f'Database already has {count} funds — skipping seed')
" || echo "Seeding skipped (non-critical)"

echo "Build complete"
