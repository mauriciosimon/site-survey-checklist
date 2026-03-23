#!/usr/bin/env python3
"""
Fix ART04 WestPark Description to cover both B01 and B10.
"""
import os
import sys
from pathlib import Path

# Set DATABASE_URL to Railway production
os.environ['DATABASE_URL'] = 'postgresql://postgres:fxkNRkTWAyPMATyFUthxrCEaNxLNKgcQ@postgres.railway.internal:5432/railway'

sys.path.insert(0, str(Path(__file__).parent))

from database import SessionLocal
from models import RateCardItem

db = SessionLocal()

# Fix ART04
art04 = db.query(RateCardItem).filter(RateCardItem.art_code == "ART04").first()
if art04:
    art04.rate_card_description = "Supply & fit seals (B01) or Adjust / re-hang door leaf (B10) — determined by fault type on inspection."
    db.commit()
    print(f"✓ Updated ART04 WestPark Description: {art04.rate_card_description}")
else:
    print("✗ ART04 not found")

db.close()
