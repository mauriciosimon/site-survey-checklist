import os
import uuid
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional

from database import engine, get_db, Base, SessionLocal
from schemas import (
    ChecklistCreate, ChecklistUpdate, ChecklistResponse, ChecklistWithOwner,
    UserCreate, UserLogin, UserResponse, UserWithStats, Token,
    DealCreate, DealUpdate, DealResponse,
    LeadCreate, LeadUpdate, LeadResponse
)
from auth import (
    get_current_user, get_current_user_required, get_admin_user,
    authenticate_user, create_access_token, get_password_hash
)
from models import User
import crud

# Create tables
Base.metadata.create_all(bind=engine)


def run_migrations():
    """Run database migrations on startup to ensure schema is up to date."""
    from sqlalchemy import text, inspect

    with engine.connect() as conn:
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        # Check if deal_id column exists in checklists table
        if 'checklists' in tables:
            columns = [col['name'] for col in inspector.get_columns('checklists')]
            if 'deal_id' not in columns:
                print("Running migration: Adding deal_id column to checklists table...")
                conn.execute(text('ALTER TABLE checklists ADD COLUMN deal_id INTEGER REFERENCES deals(id)'))
                conn.commit()
                print("Migration complete: deal_id column added")

        # Create leads table if it doesn't exist
        if 'leads' not in tables:
            print("Running migration: Creating leads table...")
            conn.execute(text('''
                CREATE TABLE leads (
                    id SERIAL PRIMARY KEY,
                    monday_item_id VARCHAR(50) UNIQUE,
                    name VARCHAR(255) NOT NULL,
                    status VARCHAR(30) DEFAULT 'New Lead',
                    priority VARCHAR(20),
                    source VARCHAR(50),
                    owner_id INTEGER REFERENCES users(id),
                    owner_name VARCHAR(255),
                    contact_name VARCHAR(255),
                    job_title VARCHAR(255),
                    email VARCHAR(255),
                    phone VARCHAR(50),
                    next_interaction_date DATE,
                    qualified_date DATE,
                    notes TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE
                )
            '''))
            conn.execute(text('CREATE INDEX ix_leads_id ON leads(id)'))
            conn.execute(text('CREATE INDEX ix_leads_monday_item_id ON leads(monday_item_id)'))
            conn.commit()
            print("Migration complete: leads table created")
        else:
            print("Schema up to date: leads table exists")


# Run migrations on startup
run_migrations()


def seed_admin_user():
    """Seed admin user from environment variables on startup."""
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin_name = os.getenv("ADMIN_NAME", "Admin User")

    if not admin_email or not admin_password:
        print("No ADMIN_EMAIL/ADMIN_PASSWORD set, skipping admin seeding")
        return

    db = SessionLocal()
    try:
        existing_user = crud.get_user_by_email(db, admin_email)
        if existing_user:
            if existing_user.role != "admin":
                existing_user.role = "admin"
                db.commit()
                print(f"Updated {admin_email} to admin role")
            else:
                print(f"Admin user {admin_email} already exists")
        else:
            new_admin = User(
                email=admin_email,
                password_hash=get_password_hash(admin_password),
                full_name=admin_name,
                role="admin"
            )
            db.add(new_admin)
            db.commit()
            print(f"Created admin user: {admin_email}")
    finally:
        db.close()


# Seed admin user on startup
seed_admin_user()

app = FastAPI(
    title="Site Visit Checklist API",
    description="API for managing construction site visit checklists",
    version="2.0.0"
)

# CORS middleware - allow Vercel deployments and localhost
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3001,http://localhost:3000,http://localhost:3002,http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/")
def root():
    return {"message": "Site Visit Checklist API", "docs": "/docs", "version": "2.0.0"}


# ============ Auth Endpoints ============

@app.post("/auth/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email exists
    existing_user = crud.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    db_user = crud.create_user(db, user)

    # Generate token
    access_token = create_access_token(data={"sub": db_user.id})

    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(db_user)
    )


@app.post("/auth/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.id})

    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@app.get("/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user_required)):
    return current_user


# ============ Admin Endpoints ============

@app.get("/admin/users", response_model=List[UserWithStats])
def admin_get_users(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    results = crud.get_users_with_checklist_count(db)
    users_with_stats = []
    for user, count in results:
        user_data = UserWithStats.model_validate(user)
        user_data.checklist_count = count
        users_with_stats.append(user_data)
    return users_with_stats


@app.get("/admin/checklists", response_model=List[ChecklistWithOwner])
def admin_get_all_checklists(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    checklists = crud.get_all_checklists_with_owners(db, skip=skip, limit=limit, user_filter=user_id)
    result = []
    for checklist in checklists:
        data = ChecklistWithOwner.model_validate(checklist)
        if checklist.owner:
            data.owner_name = checklist.owner.full_name
            data.owner_email = checklist.owner.email
        result.append(data)
    return result


# ============ Checklist Endpoints ============

@app.get("/checklists", response_model=List[ChecklistResponse])
def list_checklists(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else None
    is_admin = current_user.role == "admin" if current_user else False
    return crud.get_checklists(db, skip=skip, limit=limit, search=search, user_id=user_id, is_admin=is_admin)


@app.get("/checklists/{checklist_id}", response_model=ChecklistResponse)
def get_checklist(
    checklist_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else None
    is_admin = current_user.role == "admin" if current_user else False
    checklist = crud.get_checklist(db, checklist_id, user_id=user_id, is_admin=is_admin)
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")
    return checklist


@app.post("/checklists", response_model=ChecklistResponse)
def create_checklist(
    checklist: ChecklistCreate,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    return crud.create_checklist(
        db,
        checklist,
        user_id=current_user.id,
        surveyor_name=current_user.full_name
    )


@app.put("/checklists/{checklist_id}", response_model=ChecklistResponse)
def update_checklist(
    checklist_id: int,
    checklist: ChecklistUpdate,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    is_admin = current_user.role == "admin"
    db_checklist = crud.update_checklist(
        db, checklist_id, checklist,
        user_id=current_user.id,
        is_admin=is_admin
    )
    if not db_checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")
    return db_checklist


@app.delete("/checklists/{checklist_id}")
def delete_checklist(
    checklist_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    is_admin = current_user.role == "admin"
    success = crud.delete_checklist(db, checklist_id, user_id=current_user.id, is_admin=is_admin)
    if not success:
        raise HTTPException(status_code=404, detail="Checklist not found")
    return {"message": "Checklist deleted successfully"}


@app.post("/checklists/{checklist_id}/photos", response_model=ChecklistResponse)
async def upload_photo(
    checklist_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    is_admin = current_user.role == "admin"
    checklist = crud.get_checklist(db, checklist_id, user_id=current_user.id, is_admin=is_admin)
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")

    # Generate unique filename
    ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    # Save file
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    # Add to checklist
    photo_url = f"/uploads/{filename}"
    return crud.add_photo_to_checklist(db, checklist_id, photo_url)


# ============ Deal Endpoints ============

@app.get("/deals", response_model=List[DealResponse])
def list_deals(
    skip: int = 0,
    limit: int = 100,
    stage: Optional[str] = None,
    grade: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """List all deals with optional filtering by stage, grade, or search term."""
    return crud.get_deals(db, skip=skip, limit=limit, stage=stage, grade=grade, search=search)


@app.get("/deals/{deal_id}", response_model=DealResponse)
def get_deal(
    deal_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Get a single deal by ID."""
    deal = crud.get_deal(db, deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal


@app.post("/deals", response_model=DealResponse)
def create_deal(
    deal: DealCreate,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Create a new deal."""
    # Check for duplicate Monday item ID if provided
    if deal.monday_item_id:
        existing = crud.get_deal_by_monday_id(db, deal.monday_item_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Deal with this Monday.com item ID already exists"
            )
    return crud.create_deal(db, deal)


@app.put("/deals/{deal_id}", response_model=DealResponse)
def update_deal(
    deal_id: int,
    deal: DealUpdate,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Update an existing deal."""
    db_deal = crud.update_deal(db, deal_id, deal)
    if not db_deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return db_deal


@app.delete("/deals/{deal_id}")
def delete_deal(
    deal_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Delete a deal."""
    success = crud.delete_deal(db, deal_id)
    if not success:
        raise HTTPException(status_code=404, detail="Deal not found")
    return {"message": "Deal deleted successfully"}


# ============ Lead Endpoints ============

@app.get("/leads", response_model=List[LeadResponse])
def list_leads(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    source: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """List all leads with optional filtering by status, priority, source, or search term."""
    return crud.get_leads(
        db, skip=skip, limit=limit,
        status=status, priority=priority, source=source, search=search
    )


@app.get("/leads/{lead_id}", response_model=LeadResponse)
def get_lead(
    lead_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Get a single lead by ID."""
    lead = crud.get_lead(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@app.post("/leads", response_model=LeadResponse)
def create_lead(
    lead: LeadCreate,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Create a new lead."""
    # Check for duplicate Monday item ID if provided
    if lead.monday_item_id:
        existing = crud.get_lead_by_monday_id(db, lead.monday_item_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Lead with this Monday.com item ID already exists"
            )
    return crud.create_lead(db, lead, owner_id=current_user.id)


@app.put("/leads/{lead_id}", response_model=LeadResponse)
def update_lead(
    lead_id: int,
    lead: LeadUpdate,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Update an existing lead."""
    db_lead = crud.update_lead(db, lead_id, lead)
    if not db_lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return db_lead


@app.delete("/leads/{lead_id}")
def delete_lead(
    lead_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Delete a lead."""
    success = crud.delete_lead(db, lead_id)
    if not success:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"message": "Lead deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
