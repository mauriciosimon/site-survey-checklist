#!/usr/bin/env python3
"""
Seed script to populate the database with test users and sample checklists.
Run with: python seed_data.py
"""

import sys
from datetime import date
from database import SessionLocal, engine, Base
from models import User, Checklist
from auth import get_password_hash

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)


def clear_existing_data(db):
    """Clear existing checklists and users (optional)"""
    db.query(Checklist).delete()
    db.query(User).delete()
    db.commit()
    print("Cleared existing data.")


def create_users(db):
    """Create test users"""
    users_data = [
        {
            "email": "admin@company.com",
            "password": "admin123",
            "full_name": "Admin Manager",
            "role": "admin"
        },
        {
            "email": "john@company.com",
            "password": "user123",
            "full_name": "John Smith",
            "role": "user"
        },
        {
            "email": "sarah@company.com",
            "password": "user123",
            "full_name": "Sarah Johnson",
            "role": "user"
        }
    ]

    created_users = {}
    for user_data in users_data:
        # Check if user already exists
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if existing:
            print(f"User {user_data['email']} already exists, skipping...")
            created_users[user_data["email"]] = existing
            continue

        user = User(
            email=user_data["email"],
            password_hash=get_password_hash(user_data["password"]),
            full_name=user_data["full_name"],
            role=user_data["role"]
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        created_users[user_data["email"]] = user
        print(f"Created user: {user_data['full_name']} ({user_data['email']}) - {user_data['role']}")

    return created_users


def create_checklists(db, users):
    """Create sample checklists"""
    john = users.get("john@company.com")
    sarah = users.get("sarah@company.com")

    if not john or not sarah:
        print("Error: Could not find John or Sarah users")
        return

    checklists_data = [
        # John Smith's checklists
        {
            "user_id": john.id,
            "site_name": "Marina Tower - Level 12",
            "surveyor_name": "John Smith",
            "survey_date": date(2025, 1, 10),
            "site_address": "Dubai Marina, Tower B, Level 12",
            "client_name": "Emirates Properties",
            "client_contact": "+971 4 555 1234",
            "project_name": "Marina Tower Office Fitout",
            "building_level": 12,
            "ceiling_height": 3.2,
            "skirting_size": "100mm",
            "floor_type": "Raised Floor",
            "soffit_type": "Concrete",
            "existing_ceiling_trims": "Aluminium grid ceiling with mineral fiber tiles",
            "ceiling_void_depth": 450,
            "floor_void_depth": 150,
            "service_penetrations_scale": 7,
            "goods_lift_available": True,
            "good_staircase_access": True,
            "loading_bay_restrictions": "Access via basement B2, max vehicle height 3.5m",
            "street_restrictions": None,
            "noise_restrictions": "Core drilling hours: 10pm - 6am only",
            "mullion_perimeter_details": "Curtain wall system with 150mm mullions",
            "wall_deflection_needed": True,
            "door_finish": "Veneer",
            "frame_type": "Timber",
            "glazing_details": "10mm clear toughened glass, full height partitions",
            "head_track_detail": "Deflection head with 25mm movement allowance",
            "start_date": date(2025, 2, 1),
            "project_secured": True,
            "programme_available": True,
            "acoustic_baffles_required": False,
            "fire_stopping_required": True,
            "mullion_details": "Standard aluminium mullions, powder coated RAL 9005",
            "pricing_details": "Budget: AED 850,000 - Fit out only",
            "supplier_notes": "Preferred suppliers: Al Futtaim Interiors, Depa",
            "additional_notes": "Client requires LEED Gold certification. All materials must have EPD documentation."
        },
        {
            "user_id": john.id,
            "site_name": "DIFC Office Fitout",
            "surveyor_name": "John Smith",
            "survey_date": date(2025, 1, 14),
            "site_address": "Gate District, DIFC, Building 5",
            "client_name": "Global Finance Ltd",
            "client_contact": "+971 4 555 5678",
            "project_name": "GFL Dubai Office",
            "building_level": 8,
            "ceiling_height": 2.8,
            "skirting_size": "150mm",
            "floor_type": "Concrete",
            "soffit_type": "Rib Deck",
            "existing_ceiling_trims": "Exposed soffit with services",
            "ceiling_void_depth": 0,
            "floor_void_depth": 0,
            "service_penetrations_scale": 5,
            "goods_lift_available": True,
            "good_staircase_access": True,
            "loading_bay_restrictions": "Loading dock access 7am-7pm",
            "street_restrictions": "No parking on Gate Avenue",
            "noise_restrictions": "No drilling after 6pm - occupied floors above",
            "mullion_perimeter_details": "Full height glazing to perimeter",
            "wall_deflection_needed": False,
            "door_finish": "Laminate",
            "frame_type": "Metal",
            "glazing_details": "Double glazed units, low-E coating",
            "head_track_detail": "Fixed head detail - no deflection required",
            "start_date": date(2025, 3, 15),
            "project_secured": False,
            "programme_available": False,
            "acoustic_baffles_required": True,
            "fire_stopping_required": True,
            "mullion_details": "Black anodised aluminium, 100x50mm sections",
            "pricing_details": "Awaiting final scope confirmation",
            "supplier_notes": "Client open to suggestions",
            "additional_notes": "Pending landlord approval for exposed ceiling concept. Acoustic treatment critical due to open plan layout."
        },
        # Sarah Johnson's checklists
        {
            "user_id": sarah.id,
            "site_name": "JBR Retail Unit",
            "surveyor_name": "Sarah Johnson",
            "survey_date": date(2025, 1, 8),
            "site_address": "The Walk, JBR, Unit G-15",
            "client_name": "Sunset Retail Group",
            "client_contact": "+971 4 555 9012",
            "project_name": "Sunset Flagship Store",
            "building_level": 0,
            "ceiling_height": 4.5,
            "skirting_size": "100mm",
            "floor_type": "Screed",
            "soffit_type": "Concrete",
            "existing_ceiling_trims": "None - shell and core",
            "ceiling_void_depth": 800,
            "floor_void_depth": 0,
            "service_penetrations_scale": 4,
            "goods_lift_available": False,
            "good_staircase_access": True,
            "loading_bay_restrictions": "Deliveries before 10am only - pedestrian zone",
            "street_restrictions": "The Walk is pedestrianised, rear access only",
            "noise_restrictions": "No noisy works during retail hours (10am-10pm)",
            "mullion_perimeter_details": "Shopfront system with bi-fold doors",
            "wall_deflection_needed": False,
            "door_finish": "Paint Grade",
            "frame_type": "Metal",
            "glazing_details": "12mm clear toughened, automatic sliding entrance",
            "head_track_detail": "Bulkhead detail at shopfront",
            "start_date": date(2025, 1, 20),
            "project_secured": True,
            "programme_available": True,
            "acoustic_baffles_required": False,
            "fire_stopping_required": True,
            "mullion_details": "Shopfront system - Schuco or equivalent",
            "pricing_details": "Budget: AED 1,200,000 including FF&E",
            "supplier_notes": "Fixtures from approved brand list only",
            "additional_notes": "High footfall area - security during works essential. Hoarding required throughout."
        },
        {
            "user_id": sarah.id,
            "site_name": "Business Bay Tower",
            "surveyor_name": "Sarah Johnson",
            "survey_date": date(2025, 1, 12),
            "site_address": "Business Bay, Plot 15, Tower A",
            "client_name": "Bay Developments",
            "client_contact": "+971 4 555 3456",
            "project_name": "Bay Dev HQ Relocation",
            "building_level": 22,
            "ceiling_height": 3.0,
            "skirting_size": "200mm",
            "floor_type": "Raised Floor",
            "soffit_type": "Rib Deck",
            "existing_ceiling_trims": "Suspended plasterboard ceiling",
            "ceiling_void_depth": 350,
            "floor_void_depth": 200,
            "service_penetrations_scale": 8,
            "goods_lift_available": True,
            "good_staircase_access": True,
            "loading_bay_restrictions": "Shared loading bay - book 48hrs in advance",
            "street_restrictions": None,
            "noise_restrictions": "Building occupied - standard working hours only",
            "mullion_perimeter_details": "Unitised curtain wall, limited modification possible",
            "wall_deflection_needed": True,
            "door_finish": "Veneer",
            "frame_type": "Timber",
            "glazing_details": "8mm clear toughened for internal partitions",
            "head_track_detail": "Deflection head required - 30mm allowance",
            "start_date": date(2025, 2, 15),
            "project_secured": True,
            "programme_available": True,
            "acoustic_baffles_required": True,
            "fire_stopping_required": True,
            "mullion_details": "Match existing curtain wall colour",
            "pricing_details": "Budget: AED 2,100,000 - CAT A already complete",
            "supplier_notes": "Reuse existing raised floor tiles where possible",
            "additional_notes": "Executive floor - high quality finishes required. Boardroom to seat 20 with integrated AV."
        },
        # Additional checklists for variety
        {
            "user_id": john.id,
            "site_name": "Palm Jumeirah Villa",
            "surveyor_name": "John Smith",
            "survey_date": date(2025, 1, 5),
            "site_address": "Frond K, Villa 42, Palm Jumeirah",
            "client_name": "Private Client",
            "client_contact": "+971 50 555 7890",
            "project_name": "Villa Renovation",
            "building_level": 0,
            "ceiling_height": 3.8,
            "skirting_size": "150mm",
            "floor_type": "Screed",
            "soffit_type": "Concrete",
            "existing_ceiling_trims": "Ornate plaster cornices - to be retained",
            "ceiling_void_depth": 200,
            "floor_void_depth": 0,
            "service_penetrations_scale": 3,
            "goods_lift_available": False,
            "good_staircase_access": True,
            "loading_bay_restrictions": "Driveway access only, no crane access",
            "street_restrictions": "Security gate - contractor passes required",
            "noise_restrictions": "Neighbours sensitive - no weekend works",
            "mullion_perimeter_details": "Existing aluminium windows to be replaced",
            "wall_deflection_needed": False,
            "door_finish": "Veneer",
            "frame_type": "Timber",
            "glazing_details": "Impact resistant glazing required (hurricane rated)",
            "head_track_detail": "Standard head details",
            "start_date": date(2025, 4, 1),
            "project_secured": True,
            "programme_available": False,
            "acoustic_baffles_required": False,
            "fire_stopping_required": False,
            "mullion_details": "Bronze anodised aluminium to match railing",
            "pricing_details": "TBC - design development stage",
            "supplier_notes": "Client prefers European suppliers",
            "additional_notes": "Listed property - heritage approval required for external changes. Interior free reign."
        },
        {
            "user_id": sarah.id,
            "site_name": "Downtown Mall Kiosk",
            "surveyor_name": "Sarah Johnson",
            "survey_date": date(2025, 1, 15),
            "site_address": "Dubai Mall, Fashion Avenue, Unit K-23",
            "client_name": "Luxe Accessories LLC",
            "client_contact": "+971 4 555 2468",
            "project_name": "Luxe Pop-up Store",
            "building_level": 2,
            "ceiling_height": 5.0,
            "skirting_size": "100mm",
            "floor_type": "Concrete",
            "soffit_type": "Other",
            "existing_ceiling_trims": "Mall atrium - open to above",
            "ceiling_void_depth": 0,
            "floor_void_depth": 0,
            "service_penetrations_scale": 2,
            "goods_lift_available": True,
            "good_staircase_access": True,
            "loading_bay_restrictions": "Mall loading dock, night deliveries only",
            "street_restrictions": "N/A - internal mall unit",
            "noise_restrictions": "All noisy works between 11pm-8am",
            "mullion_perimeter_details": "Freestanding kiosk - no fixed perimeter",
            "wall_deflection_needed": False,
            "door_finish": "PG",
            "frame_type": "Metal",
            "glazing_details": "Frameless glass display cases",
            "head_track_detail": "Canopy structure - TBC by designer",
            "start_date": date(2025, 1, 25),
            "project_secured": True,
            "programme_available": True,
            "acoustic_baffles_required": False,
            "fire_stopping_required": False,
            "mullion_details": "N/A",
            "pricing_details": "Budget: AED 450,000 - 6 month lease",
            "supplier_notes": "Fast track programme - 3 week fitout window",
            "additional_notes": "Pop-up format - must be fully demountable. Emaar design guidelines to be followed."
        }
    ]

    for checklist_data in checklists_data:
        checklist = Checklist(**checklist_data)
        db.add(checklist)
        print(f"Created checklist: {checklist_data['site_name']} for user_id {checklist_data['user_id']}")

    db.commit()
    print(f"\nCreated {len(checklists_data)} checklists.")


def main():
    print("=" * 50)
    print("Site Checklist - Database Seeder")
    print("=" * 50)

    db = SessionLocal()

    try:
        # Ask if user wants to clear existing data
        if "--clear" in sys.argv:
            clear_existing_data(db)

        print("\n--- Creating Users ---")
        users = create_users(db)

        print("\n--- Creating Checklists ---")
        create_checklists(db, users)

        print("\n" + "=" * 50)
        print("Seeding complete!")
        print("=" * 50)
        print("\nTest Accounts:")
        print("  Admin:  admin@company.com / admin123")
        print("  User 1: john@company.com / user123")
        print("  User 2: sarah@company.com / user123")
        print("")

    except Exception as e:
        print(f"\nError: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
