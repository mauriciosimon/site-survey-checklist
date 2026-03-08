#!/usr/bin/env python3
"""Clear photos from a checklist by ID"""
import os
import sys
from sqlalchemy import create_engine, text

def clear_photos(checklist_id: int):
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("ERROR: DATABASE_URL not set")
        return False
    
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Check if checklist exists
            result = conn.execute(
                text("SELECT id, site_name FROM checklists WHERE id = :id"), 
                {"id": checklist_id}
            )
            row = result.fetchone()
            
            if not row:
                print(f"ERROR: Checklist {checklist_id} not found")
                return False
            
            print(f"Found checklist: ID={row[0]}, site_name={row[1]}")
            
            # Clear site_photos
            conn.execute(
                text("UPDATE checklists SET site_photos = '[]' WHERE id = :id"), 
                {"id": checklist_id}
            )
            conn.commit()
            
            print(f"✅ Cleared all photos from checklist {checklist_id}")
            return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python clear_photos.py <checklist_id>")
        sys.exit(1)
    
    checklist_id = int(sys.argv[1])
    success = clear_photos(checklist_id)
    sys.exit(0 if success else 1)
