import os
import uuid
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import anthropic

from database import engine, get_db, Base, SessionLocal
from schemas import (
    ChecklistCreate, ChecklistUpdate, ChecklistResponse, ChecklistWithOwner,
    UserCreate, UserLogin, UserResponse, UserWithStats, Token,
    DealCreate, DealUpdate, DealResponse,
    LeadCreate, LeadUpdate, LeadResponse,
    AccountCreate, AccountUpdate, AccountResponse,
    ContactCreate, ContactUpdate, ContactResponse,
    TaskCreate, TaskUpdate, TaskResponse,
    OpportunityCreate, OpportunityUpdate, OpportunityResponse,
    WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse, WorkspaceWithCounts,
    ChatRequest, ChatResponse
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

        # Create workspaces table if it doesn't exist
        if 'workspaces' not in tables:
            print("Running migration: Creating workspaces table...")
            conn.execute(text('''
                CREATE TABLE workspaces (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    monday_workspace_id VARCHAR(50) UNIQUE,
                    icon VARCHAR(10),
                    color VARCHAR(20),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE
                )
            '''))
            conn.execute(text('CREATE INDEX ix_workspaces_id ON workspaces(id)'))
            conn.execute(text('CREATE INDEX ix_workspaces_monday_workspace_id ON workspaces(monday_workspace_id)'))
            conn.commit()
            print("Migration complete: workspaces table created")

            # Seed default workspaces
            print("Running migration: Seeding default workspaces...")
            conn.execute(text('''
                INSERT INTO workspaces (name, monday_workspace_id, icon, color, is_active)
                VALUES
                    ('CRM - Satoris', '4323419', '💼', '#0086c0', TRUE),
                    ('Business Technology Group', '5562899', '💻', '#00c875', TRUE),
                    ('MVP Template', '5556997', '📋', '#fdab3d', TRUE)
            '''))
            conn.commit()
            print("Migration complete: default workspaces seeded")
        else:
            print("Schema up to date: workspaces table exists")

        # Add workspace_id column to existing tables
        for table_name in ['deals', 'leads', 'accounts', 'contacts', 'tasks', 'checklists']:
            if table_name in tables:
                columns = [col['name'] for col in inspector.get_columns(table_name)]
                if 'workspace_id' not in columns:
                    print(f"Running migration: Adding workspace_id column to {table_name} table...")
                    conn.execute(text(f'ALTER TABLE {table_name} ADD COLUMN workspace_id INTEGER REFERENCES workspaces(id)'))
                    conn.execute(text(f'CREATE INDEX ix_{table_name}_workspace_id ON {table_name}(workspace_id)'))
                    conn.commit()
                    print(f"Migration complete: workspace_id column added to {table_name}")

                    # Assign existing data to CRM - Satoris workspace (id=1)
                    if table_name in ['deals', 'leads', 'accounts', 'contacts', 'tasks']:
                        print(f"Running migration: Assigning existing {table_name} to CRM - Satoris workspace...")
                        conn.execute(text(f'UPDATE {table_name} SET workspace_id = 1 WHERE workspace_id IS NULL'))
                        conn.commit()
                        print(f"Migration complete: existing {table_name} assigned to workspace")

        # Ensure existing data is assigned to CRM - Satoris workspace (run every time)
        if 'workspaces' in tables:
            # Check if workspaces exist, if not seed them
            result = conn.execute(text('SELECT COUNT(*) FROM workspaces'))
            workspace_count = result.scalar()
            
            if workspace_count == 0:
                print("Running migration: Seeding default workspaces (table was empty)...")
                conn.execute(text('''
                    INSERT INTO workspaces (name, monday_workspace_id, icon, color, is_active)
                    VALUES
                        ('CRM - Satoris', '4323419', '💼', '#0086c0', TRUE),
                        ('Business Technology Group', '5562899', '💻', '#00c875', TRUE),
                        ('MVP Template', '5556997', '📋', '#fdab3d', TRUE)
                '''))
                conn.commit()
                print("Migration complete: default workspaces seeded")
            
            result = conn.execute(text('SELECT COUNT(*) FROM workspaces WHERE id = 1'))
            workspace_exists = result.scalar() > 0

            if workspace_exists:
                for table_name in ['deals', 'leads', 'accounts', 'contacts', 'tasks']:
                    if table_name in tables:
                        result = conn.execute(text(f'SELECT COUNT(*) FROM {table_name} WHERE workspace_id IS NULL'))
                        null_count = result.scalar()
                        if null_count > 0:
                            print(f"Running migration: Assigning {null_count} {table_name} to CRM - Satoris workspace...")
                            conn.execute(text(f'UPDATE {table_name} SET workspace_id = 1 WHERE workspace_id IS NULL'))
                            conn.commit()
                            print(f"Migration complete: {table_name} assigned to workspace")

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

        # Create accounts table if it doesn't exist
        if 'accounts' not in tables:
            print("Running migration: Creating accounts table...")
            conn.execute(text('''
                CREATE TABLE accounts (
                    id SERIAL PRIMARY KEY,
                    monday_item_id VARCHAR(50) UNIQUE,
                    name VARCHAR(255) NOT NULL,
                    status VARCHAR(30) DEFAULT 'Prospect',
                    label VARCHAR(50),
                    industry TEXT,
                    employee_count VARCHAR(50),
                    account_type VARCHAR(100),
                    website TEXT,
                    company_profile_url TEXT,
                    address TEXT,
                    location_lat NUMERIC(10, 7),
                    location_lng NUMERIC(10, 7),
                    owner_id INTEGER REFERENCES users(id),
                    owner_name VARCHAR(255),
                    owner_job_title VARCHAR(255),
                    notes TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE
                )
            '''))
            conn.execute(text('CREATE INDEX ix_accounts_id ON accounts(id)'))
            conn.execute(text('CREATE INDEX ix_accounts_monday_item_id ON accounts(monday_item_id)'))
            conn.commit()
            print("Migration complete: accounts table created")
        else:
            print("Schema up to date: accounts table exists")

        # Create contacts table if it doesn't exist
        if 'contacts' not in tables:
            print("Running migration: Creating contacts table...")
            conn.execute(text('''
                CREATE TABLE contacts (
                    id SERIAL PRIMARY KEY,
                    monday_item_id VARCHAR(50) UNIQUE,
                    name VARCHAR(255) NOT NULL,
                    company VARCHAR(255),
                    contact_type VARCHAR(50),
                    job_title VARCHAR(255),
                    title_role VARCHAR(50),
                    tier VARCHAR(50),
                    email VARCHAR(255),
                    phone VARCHAR(50),
                    linkedin_url TEXT,
                    location VARCHAR(255),
                    icp_fit VARCHAR(20),
                    outreach_stage VARCHAR(50),
                    source VARCHAR(50),
                    next_action_date DATE,
                    industry VARCHAR(255),
                    description TEXT,
                    about TEXT,
                    birthday DATE,
                    tags JSON DEFAULT '[]',
                    account_id INTEGER REFERENCES accounts(id),
                    owner_id INTEGER REFERENCES users(id),
                    owner_name VARCHAR(255),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE
                )
            '''))
            conn.execute(text('CREATE INDEX ix_contacts_id ON contacts(id)'))
            conn.execute(text('CREATE INDEX ix_contacts_monday_item_id ON contacts(monday_item_id)'))
            conn.execute(text('CREATE INDEX ix_contacts_account_id ON contacts(account_id)'))
            conn.commit()
            print("Migration complete: contacts table created")
        else:
            print("Schema up to date: contacts table exists")

        # Create tasks table if it doesn't exist
        if 'tasks' not in tables:
            print("Running migration: Creating tasks table...")
            conn.execute(text('''
                CREATE TABLE tasks (
                    id SERIAL PRIMARY KEY,
                    monday_item_id VARCHAR(50) UNIQUE,
                    name VARCHAR(255) NOT NULL,
                    status VARCHAR(30) DEFAULT 'To do',
                    priority VARCHAR(20),
                    task_type VARCHAR(30),
                    due_date DATE,
                    close_date DATE,
                    related_to VARCHAR(255),
                    deal_id INTEGER REFERENCES deals(id),
                    lead_id INTEGER REFERENCES leads(id),
                    account_id INTEGER REFERENCES accounts(id),
                    contact_id INTEGER REFERENCES contacts(id),
                    owner_id INTEGER REFERENCES users(id),
                    owner_name VARCHAR(255),
                    notes TEXT,
                    files JSON DEFAULT '[]',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE
                )
            '''))
            conn.execute(text('CREATE INDEX ix_tasks_id ON tasks(id)'))
            conn.execute(text('CREATE INDEX ix_tasks_monday_item_id ON tasks(monday_item_id)'))
            conn.execute(text('CREATE INDEX ix_tasks_owner_id ON tasks(owner_id)'))
            conn.execute(text('CREATE INDEX ix_tasks_due_date ON tasks(due_date)'))
            conn.commit()
            print("Migration complete: tasks table created")
        else:
            print("Schema up to date: tasks table exists")

        # Update deals table to match Satoris schema
        if 'deals' in tables:
            deal_columns = [col['name'] for col in inspector.get_columns('deals')]

            # Add new columns
            if 'status' not in deal_columns:
                print("Running migration: Adding status column to deals table...")
                conn.execute(text("ALTER TABLE deals ADD COLUMN status VARCHAR(30) DEFAULT 'New deal'"))
                conn.commit()
                print("Migration complete: status column added to deals")

            if 'value' not in deal_columns:
                print("Running migration: Adding value column to deals table...")
                conn.execute(text("ALTER TABLE deals ADD COLUMN value NUMERIC(12, 2)"))
                conn.commit()
                print("Migration complete: value column added to deals")

            if 'deal_length' not in deal_columns:
                print("Running migration: Adding deal_length column to deals table...")
                conn.execute(text("ALTER TABLE deals ADD COLUMN deal_length INTEGER"))
                conn.commit()
                print("Migration complete: deal_length column added to deals")

            if 'proposal_sent_date' not in deal_columns:
                print("Running migration: Adding proposal_sent_date column to deals table...")
                conn.execute(text("ALTER TABLE deals ADD COLUMN proposal_sent_date DATE"))
                conn.commit()
                print("Migration complete: proposal_sent_date column added to deals")

            if 'owner_id' not in deal_columns:
                print("Running migration: Adding owner_id column to deals table...")
                conn.execute(text("ALTER TABLE deals ADD COLUMN owner_id INTEGER REFERENCES users(id)"))
                conn.commit()
                print("Migration complete: owner_id column added to deals")

            if 'account_id' not in deal_columns:
                print("Running migration: Adding account_id column to deals table...")
                conn.execute(text("ALTER TABLE deals ADD COLUMN account_id INTEGER REFERENCES accounts(id)"))
                conn.commit()
                print("Migration complete: account_id column added to deals")

            if 'lead_id' not in deal_columns:
                print("Running migration: Adding lead_id column to deals table...")
                conn.execute(text("ALTER TABLE deals ADD COLUMN lead_id INTEGER REFERENCES leads(id)"))
                conn.commit()
                print("Migration complete: lead_id column added to deals")

            # Drop deprecated columns (safe to do as they're optional)
            deprecated_columns = ['products', 'return_date', 'quote_sent_date', 'decision_date',
                                  'status_update_date', 'close_probability', 'location_address',
                                  'location_lat', 'location_lng', 'link_url']
            for col in deprecated_columns:
                if col in deal_columns:
                    print(f"Running migration: Dropping deprecated {col} column from deals table...")
                    conn.execute(text(f"ALTER TABLE deals DROP COLUMN {col}"))
                    conn.commit()
                    print(f"Migration complete: {col} column dropped from deals")

            # Update existing deals with old stage values to new stage values
            print("Running migration: Updating deal stage values to Satoris schema...")
            conn.execute(text("""
                UPDATE deals SET stage = CASE
                    WHEN stage = 'Leads' THEN 'Prospects'
                    WHEN stage = 'Estimating' THEN 'Preparing proposal'
                    WHEN stage = 'Submitted' THEN 'Proposal sent'
                    WHEN stage = 'Won' THEN 'Closed Won'
                    WHEN stage = 'Declined' THEN 'Lost'
                    ELSE stage
                END
            """))
            conn.commit()
            print("Migration complete: deal stage values updated")

        # Create opportunities table if it doesn't exist
        if 'opportunities' not in tables:
            print("Running migration: Creating opportunities table...")
            conn.execute(text('''
                CREATE TABLE opportunities (
                    id SERIAL PRIMARY KEY,
                    workspace_id INTEGER REFERENCES workspaces(id),
                    monday_item_id VARCHAR(50) UNIQUE,
                    name VARCHAR(255) NOT NULL,
                    stage VARCHAR(50) DEFAULT 'Leads',
                    grade VARCHAR(20),
                    contact_name VARCHAR(255),
                    company_name VARCHAR(255),
                    email VARCHAR(255),
                    phone VARCHAR(50),
                    sale_price NUMERIC(12, 2),
                    close_probability INTEGER,
                    owner_id INTEGER REFERENCES users(id),
                    owner_name VARCHAR(255),
                    survey_required BOOLEAN DEFAULT FALSE,
                    quote_template VARCHAR(50),
                    quotes_done INTEGER,
                    revisions_made BOOLEAN DEFAULT FALSE,
                    num_revisions INTEGER,
                    next_interaction DATE,
                    return_date DATE,
                    quote_sent_date DATE,
                    decision_date DATE,
                    close_date DATE,
                    start_date DATE,
                    end_date DATE,
                    location_address TEXT,
                    location_lat NUMERIC(10, 7),
                    location_lng NUMERIC(10, 7),
                    files JSON DEFAULT '[]',
                    link TEXT,
                    supplier_quotes JSON DEFAULT '[]',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE
                )
            '''))
            conn.execute(text('CREATE INDEX ix_opportunities_id ON opportunities(id)'))
            conn.execute(text('CREATE INDEX ix_opportunities_workspace_id ON opportunities(workspace_id)'))
            conn.execute(text('CREATE INDEX ix_opportunities_monday_item_id ON opportunities(monday_item_id)'))
            conn.execute(text('CREATE INDEX ix_opportunities_stage ON opportunities(stage)'))
            conn.execute(text('CREATE INDEX ix_opportunities_grade ON opportunities(grade)'))
            conn.commit()
            print("Migration complete: opportunities table created")
        else:
            print("Schema up to date: opportunities table exists")


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


# ============ Workspace Endpoints ============

@app.get("/workspaces", response_model=List[WorkspaceResponse])
def list_workspaces(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """List all workspaces with optional filtering."""
    return crud.get_workspaces(db, skip=skip, limit=limit, is_active=is_active, search=search)


@app.get("/workspaces/{workspace_id}", response_model=WorkspaceWithCounts)
def get_workspace(
    workspace_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Get a single workspace by ID with entity counts."""
    result = crud.get_workspace_with_counts(db, workspace_id)
    if not result:
        raise HTTPException(status_code=404, detail="Workspace not found")
    workspace, counts = result
    response = WorkspaceWithCounts.model_validate(workspace)
    response.lead_count = counts['lead_count']
    response.deal_count = counts['deal_count']
    response.account_count = counts['account_count']
    response.contact_count = counts['contact_count']
    response.task_count = counts['task_count']
    response.checklist_count = counts['checklist_count']
    return response


@app.post("/workspaces", response_model=WorkspaceResponse)
def create_workspace(
    workspace: WorkspaceCreate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new workspace (admin only)."""
    # Check for duplicate Monday workspace ID if provided
    if workspace.monday_workspace_id:
        existing = crud.get_workspace_by_monday_id(db, workspace.monday_workspace_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workspace with this Monday.com workspace ID already exists"
            )
    return crud.create_workspace(db, workspace)


@app.put("/workspaces/{workspace_id}", response_model=WorkspaceResponse)
def update_workspace(
    workspace_id: int,
    workspace: WorkspaceUpdate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update an existing workspace (admin only)."""
    db_workspace = crud.update_workspace(db, workspace_id, workspace)
    if not db_workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return db_workspace


@app.delete("/workspaces/{workspace_id}")
def delete_workspace(
    workspace_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a workspace (admin only)."""
    success = crud.delete_workspace(db, workspace_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return {"message": "Workspace deleted successfully"}


# ============ Checklist Endpoints ============

@app.get("/checklists", response_model=List[ChecklistResponse])
def list_checklists(
    skip: int = 0,
    limit: int = 100,
    workspace_id: Optional[int] = None,
    search: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else None
    is_admin = current_user.role == "admin" if current_user else False
    return crud.get_checklists(db, skip=skip, limit=limit, workspace_id=workspace_id, search=search, user_id=user_id, is_admin=is_admin)


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
    workspace_id: Optional[int] = None,
    stage: Optional[str] = None,
    status: Optional[str] = None,
    grade: Optional[str] = None,
    deal_type: Optional[str] = None,
    account_id: Optional[int] = None,
    lead_id: Optional[int] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """List all deals with optional filtering by workspace, stage, status, grade, deal_type, or search term."""
    return crud.get_deals(
        db, skip=skip, limit=limit, workspace_id=workspace_id,
        stage=stage, status=status, grade=grade, deal_type=deal_type,
        account_id=account_id, lead_id=lead_id, search=search
    )


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
    return crud.create_deal(db, deal, owner_id=current_user.id)


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
    workspace_id: Optional[int] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    source: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """List all leads with optional filtering by workspace, status, priority, source, or search term."""
    return crud.get_leads(
        db, skip=skip, limit=limit, workspace_id=workspace_id,
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


# ============ Account Endpoints ============

@app.get("/accounts", response_model=List[AccountResponse])
def list_accounts(
    skip: int = 0,
    limit: int = 100,
    workspace_id: Optional[int] = None,
    status: Optional[str] = None,
    label: Optional[str] = None,
    industry: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """List all accounts with optional filtering by workspace, status, label, industry, or search term."""
    return crud.get_accounts(
        db, skip=skip, limit=limit, workspace_id=workspace_id,
        status=status, label=label, industry=industry, search=search
    )


@app.get("/accounts/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Get a single account by ID."""
    account = crud.get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@app.post("/accounts", response_model=AccountResponse)
def create_account(
    account: AccountCreate,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Create a new account."""
    # Check for duplicate Monday item ID if provided
    if account.monday_item_id:
        existing = crud.get_account_by_monday_id(db, account.monday_item_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account with this Monday.com item ID already exists"
            )
    return crud.create_account(db, account, owner_id=current_user.id)


@app.put("/accounts/{account_id}", response_model=AccountResponse)
def update_account(
    account_id: int,
    account: AccountUpdate,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Update an existing account."""
    db_account = crud.update_account(db, account_id, account)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account


@app.delete("/accounts/{account_id}")
def delete_account(
    account_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Delete an account."""
    success = crud.delete_account(db, account_id)
    if not success:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"message": "Account deleted successfully"}


# ============ Contact Endpoints ============

@app.get("/contacts", response_model=List[ContactResponse])
def list_contacts(
    skip: int = 0,
    limit: int = 100,
    workspace_id: Optional[int] = None,
    contact_type: Optional[str] = None,
    account_id: Optional[int] = None,
    icp_fit: Optional[str] = None,
    outreach_stage: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """List all contacts with optional filtering by workspace."""
    return crud.get_contacts(
        db, skip=skip, limit=limit, workspace_id=workspace_id,
        contact_type=contact_type, account_id=account_id,
        icp_fit=icp_fit, outreach_stage=outreach_stage, search=search
    )


@app.get("/contacts/{contact_id}", response_model=ContactResponse)
def get_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Get a single contact by ID."""
    contact = crud.get_contact(db, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@app.post("/contacts", response_model=ContactResponse)
def create_contact(
    contact: ContactCreate,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Create a new contact."""
    # Check for duplicate Monday item ID if provided
    if contact.monday_item_id:
        existing = crud.get_contact_by_monday_id(db, contact.monday_item_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contact with this Monday.com item ID already exists"
            )
    return crud.create_contact(db, contact, owner_id=current_user.id)


@app.put("/contacts/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: int,
    contact: ContactUpdate,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Update an existing contact."""
    db_contact = crud.update_contact(db, contact_id, contact)
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@app.delete("/contacts/{contact_id}")
def delete_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Delete a contact."""
    success = crud.delete_contact(db, contact_id)
    if not success:
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"message": "Contact deleted successfully"}


# ============ Task Endpoints ============

@app.get("/tasks", response_model=List[TaskResponse])
def list_tasks(
    skip: int = 0,
    limit: int = 100,
    workspace_id: Optional[int] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    task_type: Optional[str] = None,
    owner_id: Optional[int] = None,
    due_date_from: Optional[date] = None,
    due_date_to: Optional[date] = None,
    deal_id: Optional[int] = None,
    lead_id: Optional[int] = None,
    account_id: Optional[int] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """List all tasks with optional filtering by workspace."""
    return crud.get_tasks(
        db, skip=skip, limit=limit, workspace_id=workspace_id,
        status=status, priority=priority, task_type=task_type,
        owner_id=owner_id, due_date_from=due_date_from, due_date_to=due_date_to,
        deal_id=deal_id, lead_id=lead_id, account_id=account_id, search=search
    )


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Get a single task by ID."""
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.post("/tasks", response_model=TaskResponse)
def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Create a new task."""
    # Check for duplicate Monday item ID if provided
    if task.monday_item_id:
        existing = crud.get_task_by_monday_id(db, task.monday_item_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task with this Monday.com item ID already exists"
            )
    return crud.create_task(db, task, owner_id=current_user.id)


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task: TaskUpdate,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Update an existing task."""
    db_task = crud.update_task(db, task_id, task)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Delete a task."""
    success = crud.delete_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}


# ============ Opportunity Endpoints ============

@app.get("/opportunities", response_model=List[OpportunityResponse])
def get_opportunities(
    skip: int = 0,
    limit: int = 100,
    workspace_id: Optional[int] = None,
    stage: Optional[str] = None,
    grade: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Get all opportunities with optional filters."""
    return crud.get_opportunities(
        db, skip=skip, limit=limit,
        workspace_id=workspace_id, stage=stage, grade=grade, search=search
    )


@app.get("/opportunities/{opportunity_id}", response_model=OpportunityResponse)
def get_opportunity(
    opportunity_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Get a single opportunity by ID."""
    opportunity = crud.get_opportunity(db, opportunity_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opportunity


@app.post("/opportunities", response_model=OpportunityResponse)
def create_opportunity(
    opportunity: OpportunityCreate,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Create a new opportunity."""
    # Check for duplicate monday_item_id
    if opportunity.monday_item_id:
        existing = crud.get_opportunity_by_monday_id(db, opportunity.monday_item_id)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Opportunity with this Monday.com item ID already exists"
            )
    return crud.create_opportunity(db, opportunity, owner_id=current_user.id)


@app.put("/opportunities/{opportunity_id}", response_model=OpportunityResponse)
def update_opportunity(
    opportunity_id: int,
    opportunity: OpportunityUpdate,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Update an existing opportunity."""
    db_opportunity = crud.update_opportunity(db, opportunity_id, opportunity)
    if not db_opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return db_opportunity


@app.delete("/opportunities/{opportunity_id}")
def delete_opportunity(
    opportunity_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Delete an opportunity."""
    success = crud.delete_opportunity(db, opportunity_id)
    if not success:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return {"message": "Opportunity deleted successfully"}


# ============ Chat Endpoint (West Park AI) ============

def build_workspace_context(db: Session, workspace_id: int) -> str:
    """Build context string with workspace data for the AI assistant."""
    # Get workspace info
    workspace = crud.get_workspace(db, workspace_id)
    if not workspace:
        return "No workspace data available."

    context_parts = [f"Current Workspace: {workspace.name}"]

    # Get deals
    deals = crud.get_deals(db, workspace_id=workspace_id, limit=50)
    if deals:
        context_parts.append(f"\n## Deals ({len(deals)} total)")
        for deal in deals[:20]:  # Limit to 20 for context size
            deal_info = f"- {deal.name}"
            if deal.stage:
                deal_info += f" | Stage: {deal.stage}"
            if deal.status:
                deal_info += f" | Status: {deal.status}"
            if deal.value:
                deal_info += f" | Value: ${deal.value:,.2f}"
            if deal.close_date:
                deal_info += f" | Close Date: {deal.close_date}"
            context_parts.append(deal_info)

    # Get leads
    leads = crud.get_leads(db, workspace_id=workspace_id, limit=50)
    if leads:
        context_parts.append(f"\n## Leads ({len(leads)} total)")
        for lead in leads[:20]:
            lead_info = f"- {lead.name}"
            if lead.status:
                lead_info += f" | Status: {lead.status}"
            if lead.priority:
                lead_info += f" | Priority: {lead.priority}"
            if lead.next_interaction_date:
                lead_info += f" | Next Interaction: {lead.next_interaction_date}"
            context_parts.append(lead_info)

    # Get tasks
    tasks = crud.get_tasks(db, workspace_id=workspace_id, limit=50)
    if tasks:
        open_tasks = [t for t in tasks if t.status not in ['Done', 'Completed']]
        context_parts.append(f"\n## Tasks ({len(open_tasks)} open / {len(tasks)} total)")
        for task in open_tasks[:15]:
            task_info = f"- {task.name}"
            if task.status:
                task_info += f" | Status: {task.status}"
            if task.priority:
                task_info += f" | Priority: {task.priority}"
            if task.due_date:
                task_info += f" | Due: {task.due_date}"
            context_parts.append(task_info)

    # Get opportunities (for BTG workspace)
    opportunities = crud.get_opportunities(db, workspace_id=workspace_id, limit=50)
    if opportunities:
        context_parts.append(f"\n## Opportunities ({len(opportunities)} total)")
        for opp in opportunities[:20]:
            opp_info = f"- {opp.name}"
            if opp.stage:
                opp_info += f" | Stage: {opp.stage}"
            if opp.grade:
                opp_info += f" | Grade: {opp.grade}"
            if opp.sale_price:
                opp_info += f" | Value: ${opp.sale_price:,.2f}"
            if opp.next_interaction:
                opp_info += f" | Next: {opp.next_interaction}"
            context_parts.append(opp_info)

    # Get accounts
    accounts = crud.get_accounts(db, workspace_id=workspace_id, limit=30)
    if accounts:
        context_parts.append(f"\n## Accounts ({len(accounts)} total)")
        for acc in accounts[:10]:
            acc_info = f"- {acc.name}"
            if acc.status:
                acc_info += f" | Status: {acc.status}"
            context_parts.append(acc_info)

    # Get contacts
    contacts = crud.get_contacts(db, workspace_id=workspace_id, limit=30)
    if contacts:
        context_parts.append(f"\n## Contacts ({len(contacts)} total)")
        for contact in contacts[:10]:
            contact_info = f"- {contact.name}"
            if contact.company:
                contact_info += f" | Company: {contact.company}"
            if contact.job_title:
                contact_info += f" | Title: {contact.job_title}"
            context_parts.append(contact_info)

    return "\n".join(context_parts)


WEST_PARK_AI_SYSTEM_PROMPT = """You are West Park AI, an intelligent assistant for West Park Contracting's CRM system. Your role is to help users understand their business data, identify priorities, and provide actionable insights.

## Your Capabilities
- Analyze deals, leads, opportunities, tasks, accounts, and contacts
- Identify urgent items requiring attention (overdue tasks, stalled deals, etc.)
- Provide summaries of pipeline status and key metrics
- Suggest next actions based on the data
- Answer questions about specific records or trends

## Communication Style
- Be concise and action-oriented
- Use bullet points for lists
- Highlight urgent items first
- Provide specific names/numbers from the data when relevant
- If you don't have enough data to answer, say so clearly

## Current Workspace Data
{workspace_context}

Remember: Only reference data from the current workspace. Be helpful but brief."""


@app.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Chat with West Park AI assistant."""
    # Get API key from environment
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="AI service not configured. Please contact administrator."
        )

    # Get workspace info
    workspace = crud.get_workspace(db, chat_request.workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Build context from workspace data
    workspace_context = build_workspace_context(db, chat_request.workspace_id)

    # Build system prompt with context
    system_prompt = WEST_PARK_AI_SYSTEM_PROMPT.format(workspace_context=workspace_context)

    # Build messages for Claude
    messages = []

    # Add conversation history
    for msg in chat_request.conversation_history:
        messages.append({
            "role": msg.role,
            "content": msg.content
        })

    # Add current user message
    messages.append({
        "role": "user",
        "content": chat_request.message
    })

    try:
        # Call Claude API
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=system_prompt,
            messages=messages
        )

        ai_response = response.content[0].text

        return ChatResponse(
            response=ai_response,
            workspace_name=workspace.name
        )

    except anthropic.APIError as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI service error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
