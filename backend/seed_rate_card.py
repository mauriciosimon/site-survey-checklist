"""
Seed rate card items from CSV into database.
Run this script once to populate the rate_card_items table.
"""

import csv
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import RateCardItem, Base
from database import get_db, engine

def seed_rate_card():
    """Load rate card data from CSV and insert into database."""
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = next(get_db())
    
    # Check if already seeded
    existing_count = db.query(RateCardItem).count()
    if existing_count > 0:
        print(f"Rate card already seeded with {existing_count} items.")
        choice = input("Do you want to re-seed (will clear existing data)? (y/N): ")
        if choice.lower() != 'y':
            print("Seeding cancelled.")
            return
        
        # Clear existing data
        db.query(RateCardItem).delete()
        db.commit()
        print("Existing rate card data cleared.")
    
    # Load CSV
    csv_path = Path(__file__).parent / "reference_files" / "BMTrada_ART_Codes_RateCard_Mapping.csv"
    
    if not csv_path.exists():
        print(f"Error: CSV file not found at {csv_path}")
        return
    
    print(f"Loading rate card from: {csv_path}")
    
    items = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            item = RateCardItem(
                art_code=row['ART Code'].strip(),
                description=row['Description'].strip(),
                rate_card_code=row['WestPark Rate Card Code'].strip(),
                unit_price=None,  # Will be set by Westley
                category=None
            )
            items.append(item)
    
    # Bulk insert
    db.bulk_save_objects(items)
    db.commit()
    
    print(f"✅ Successfully seeded {len(items)} rate card items!")
    
    # Show sample
    sample = db.query(RateCardItem).limit(5).all()
    print("\nSample items:")
    for item in sample:
        print(f"  {item.art_code}: {item.description[:50]}... → {item.rate_card_code}")
    
    db.close()


if __name__ == "__main__":
    seed_rate_card()
