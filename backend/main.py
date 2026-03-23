# Westpark Surveys API - Photo uploads via Vercel Blob
import os
import uuid
import logging
import shutil
import tempfile
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from typing import List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from database import engine, get_db, Base
from schemas import (
    ChecklistCreate, ChecklistUpdate, ChecklistResponse, ChecklistWithOwner,
    UserCreate, UserLogin, UserResponse, UserWithStats, Token
)
from auth import (
    get_current_user, get_current_user_required, get_admin_user,
    authenticate_user, create_access_token
)
from models import User, Checklist, RateCardItem
import crud
import monday_api

# Frontend URL for generating survey links
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://site-checklist.vercel.app")

# Create tables
Base.metadata.create_all(bind=engine)

# Migration: Add new columns if they don't exist
from sqlalchemy import text
columns_to_add = [
    ("monday_item_id", "VARCHAR(50)"),
    ("goods_lift_notes", "TEXT"),
    ("staircase_access_notes", "TEXT"),
    ("wall_deflection_notes", "TEXT"),
    ("door_finish_other", "TEXT"),
    ("frame_type_other", "TEXT"),
    ("acoustic_baffles_notes", "TEXT"),
    ("fire_stopping_notes", "TEXT"),
    ("is_draft", "BOOLEAN DEFAULT TRUE"),
]
for col_name, col_type in columns_to_add:
    try:
        with engine.connect() as conn:
            conn.execute(text(f"ALTER TABLE checklists ADD COLUMN {col_name} {col_type}"))
            conn.commit()
            print(f"Migration: added {col_name} column")
    except Exception as e:
        if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
            pass  # Column already exists, silently continue
        else:
            print(f"Migration skipped for {col_name}: column likely exists")

# Migration: Add rate_card_description column to rate_card_items table
try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE rate_card_items ADD COLUMN rate_card_description TEXT"))
        conn.commit()
        print("Migration: added rate_card_description column to rate_card_items")
except Exception as e:
    if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
        pass  # Column already exists
    else:
        print(f"Migration skipped for rate_card_description: {e}")

# Migration: Convert numeric building spec columns to text (VARCHAR)
# This fixes the "numeric field overflow" error when users enter large values
numeric_to_text_columns = [
    "ceiling_height",
    "skirting_size",
    "ceiling_void_depth",
    "floor_void_depth",
    "building_level",
    "service_penetrations_scale",
]
for col_name in numeric_to_text_columns:
    try:
        with engine.connect() as conn:
            # Try with USING clause to convert existing numeric data
            conn.execute(text(f"ALTER TABLE checklists ALTER COLUMN {col_name} TYPE VARCHAR(100) USING {col_name}::TEXT"))
            conn.commit()
            print(f"Migration: converted {col_name} from NUMERIC to VARCHAR(100)")
    except Exception as e:
        error_str = str(e).lower()
        if "does not exist" in error_str or "already" in error_str:
            # Column doesn't exist or already correct type
            pass
        else:
            print(f"Migration note for {col_name}: {str(e)[:100]}")

app = FastAPI(
    title="Site Visit Checklist API",
    description="API for managing construction site visit checklists",
    version="2.1.0"  # Added Monday.com integration
)

# CORS middleware - allow Vercel deployments and localhost
ALLOWED_ORIGINS_STR = os.getenv("ALLOWED_ORIGINS", "http://localhost:3001,http://localhost:3000,http://localhost:3002,http://localhost:5173,https://westpark-surveys.vercel.app")
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS_STR.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now - will restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Uploads now use Vercel Blob - no local storage needed

@app.on_event("startup")
async def startup_event():
    blob_token = os.getenv("BLOB_READ_WRITE_TOKEN")
    logger.info(f"[STARTUP] BLOB_READ_WRITE_TOKEN configured: {bool(blob_token)}")
    if blob_token:
        logger.info(f"[STARTUP] Token prefix: {blob_token[:20]}...")

@app.get("/")
def root():
    return {"message": "Site Visit Checklist API", "docs": "/docs", "version": "2.0.0"}

@app.get("/debug/blob-token")
def debug_blob_token():
    blob_token = os.getenv("BLOB_READ_WRITE_TOKEN")
    return {
        "configured": bool(blob_token),
        "prefix": blob_token[:20] if blob_token else None
    }


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
    try:
        logger.info(f"GET /checklists called - skip={skip}, limit={limit}, search={search}")
        user_id = current_user.id if current_user else None
        is_admin = current_user.role == "admin" if current_user else False
        logger.info(f"User context - user_id={user_id}, is_admin={is_admin}")
        checklists = crud.get_checklists(db, skip=skip, limit=limit, search=search, user_id=user_id, is_admin=is_admin)
        logger.info(f"Fetched {len(checklists)} checklists successfully")
        logger.info("About to return checklists - triggering Pydantic serialization...")
        # Try to serialize each checklist to catch validation errors
        result = []
        for i, checklist in enumerate(checklists):
            try:
                validated = ChecklistResponse.model_validate(checklist)
                result.append(validated)
                logger.info(f"Checklist {i+1}/{len(checklists)} validated OK (id={checklist.id})")
            except Exception as ve:
                logger.error(f"Validation failed for checklist {i+1} (id={checklist.id}): {type(ve).__name__}: {str(ve)}", exc_info=True)
                raise
        logger.info(f"All {len(result)} checklists validated successfully")
        return result
    except Exception as e:
        logger.error(f"Failed to list checklists: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list checklists: {str(e)}")


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
    # Create checklist in database
    db_checklist = crud.create_checklist(
        db,
        checklist,
        user_id=current_user.id,
        surveyor_name=current_user.full_name
    )

    # Sync to Monday.com Site Surveys board
    survey_url = f"{FRONTEND_URL}/view/{db_checklist.id}"
    survey_date = str(db_checklist.survey_date) if db_checklist.survey_date else None

    monday_result = monday_api.create_site_survey_item(
        name=db_checklist.site_name,
        survey_url=survey_url,
        survey_date=survey_date,
        status="Working on it",
        created_by=current_user.full_name
    )

    # Store Monday.com item ID if sync was successful
    if monday_result.get("success") and monday_result.get("item_id"):
        db_checklist.monday_item_id = monday_result["item_id"]
        db.commit()
        db.refresh(db_checklist)

    return db_checklist


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
    import requests
    
    is_admin = current_user.role == "admin"
    checklist = crud.get_checklist(db, checklist_id, user_id=current_user.id, is_admin=is_admin)
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")

    # Get Vercel Blob token from environment
    # TEMPORARY: Hardcoded for testing (Railway env var not working at runtime)
    blob_token = "vercel_blob_rw_sVwnQznFPrCYs2uq_OHVOAjS4N9DidHZPyt4nJfIntS12k7"
    logger.info(f"[UPLOAD] Using Vercel Blob token (hardcoded for testing)")
    if not blob_token:
        logger.error("[UPLOAD] BLOB_READ_WRITE_TOKEN not set")
        raise HTTPException(status_code=500, detail="Blob storage not configured")
    
    # Generate unique filename
    original_filename = file.filename or "untitled.jpg"
    ext = os.path.splitext(original_filename)[1] if original_filename else ".jpg"
    unique_filename = f"{uuid.uuid4()}{ext}"
    pathname = f"westpark-surveys/checklist-{checklist_id}/{unique_filename}"
    
    logger.info(f"[UPLOAD] Uploading to Vercel Blob: {pathname}")
    
    try:
        # Read file content
        content = await file.read()
        logger.info(f"[UPLOAD] Read {len(content)} bytes from uploaded file")
        
        # PUT request to Vercel Blob API
        blob_url = f"https://blob.vercel-storage.com/{pathname}"
        response = requests.put(
            blob_url,
            data=content,
            headers={
                "Content-Type": file.content_type or "application/octet-stream",
                "Authorization": f"Bearer {blob_token}"
            }
        )
        
        if response.status_code != 200:
            logger.error(f"[UPLOAD] Blob upload failed: {response.status_code} {response.text}")
            raise HTTPException(status_code=500, detail="Failed to upload to blob storage")
        
        blob_data = response.json()
        public_url = blob_data.get("url")
        logger.info(f"[UPLOAD] ✅ Blob uploaded: {public_url}")
        
    except Exception as e:
        logger.error(f"[UPLOAD] Blob upload exception: {e}")
        raise HTTPException(status_code=500, detail=f"Blob upload failed: {str(e)}")
    
    # Add to checklist with public URL
    return crud.add_photo_to_checklist(db, checklist_id, public_url, original_filename)


@app.delete("/checklists/{checklist_id}/photos/{photo_index}")
def delete_photo_by_index(
    checklist_id: int,
    photo_index: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Delete a specific photo by index from a checklist"""
    is_admin = current_user.role == "admin"
    checklist = crud.get_checklist(db, checklist_id, user_id=current_user.id, is_admin=is_admin)
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")
    
    photos = checklist.site_photos or []
    if photo_index < 0 or photo_index >= len(photos):
        raise HTTPException(status_code=404, detail="Photo index out of range")
    
    # Remove photo at index
    deleted_photo = photos.pop(photo_index)
    checklist.site_photos = photos
    flag_modified(checklist, "site_photos")
    db.commit()
    db.refresh(checklist)
    
    return {
        "message": f"Deleted photo at index {photo_index}",
        "deleted_photo": deleted_photo,
        "site_photos": checklist.site_photos
    }


@app.delete("/checklists/{checklist_id}/photos")
def clear_all_photos(
    checklist_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """Clear all photos from a checklist (requires authentication)"""
    is_admin = current_user.role == "admin"
    checklist = crud.get_checklist(db, checklist_id, user_id=current_user.id, is_admin=is_admin)
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")
    
    # Clear photos
    checklist.site_photos = []
    flag_modified(checklist, "site_photos")  # Tell SQLAlchemy the JSON field changed
    db.commit()
    db.refresh(checklist)
    
    return {"message": f"Cleared all photos from checklist {checklist_id}", "checklist_id": checklist_id}


@app.post("/admin/clear-photos/{checklist_id}")
def admin_clear_photos(
    checklist_id: int,
    admin_key: str,
    db: Session = Depends(get_db)
):
    """Admin endpoint to clear photos without authentication (temporary)"""
    # Simple admin key check (use env var in production)
    ADMIN_KEY = os.getenv("ADMIN_KEY", "temp-admin-key-123")
    if admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin key")
    
    # Get checklist
    checklist = db.query(Checklist).filter(Checklist.id == checklist_id).first()
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")
    
    # Count photos before clearing
    photo_count = len(checklist.site_photos) if checklist.site_photos else 0
    
    # Clear photos
    checklist.site_photos = []
    flag_modified(checklist, "site_photos")
    db.commit()
    db.refresh(checklist)
    
    return {
        "message": f"Cleared {photo_count} photos from checklist {checklist_id}",
        "checklist_id": checklist_id,
        "photos_cleared": photo_count
    }


# ==================== FIRE DOOR QUOTING ENDPOINT ====================
@app.post("/api/firedoor/process")
async def process_firedoor_survey(
    file: UploadFile = File(...),
    client_name: str = Form(...)
):
    """
    Process fire door survey file (PDF or Excel) and return populated quote Excel.
    
    Supports:
    - Type 1: PDF with FireDNA/RiskBase/BM TRADA ART codes
    - Type 2: Excel with door fault columns
    """
    import firedoor_processor as fdp
    
    if not client_name:
        raise HTTPException(status_code=400, detail="Client name is required")
    
    def cleanup_temp_dir(dir_path: str):
        """Clean up temp directory after response is sent."""
        try:
            shutil.rmtree(dir_path)
            logger.info(f"Cleaned up temp directory: {dir_path}")
        except Exception as e:
            logger.error(f"Error cleaning up temp directory {dir_path}: {e}")
    
    # Create temp directory (no auto-cleanup - we'll use BackgroundTask)
    temp_dir = tempfile.mkdtemp()
    logger.info(f"Created temp directory: {temp_dir}")
    
    try:
        # Save uploaded file
        input_path = Path(temp_dir) / file.filename
        with open(input_path, 'wb') as f:
            shutil.copyfileobj(file.file, f)
        
        # Detect format
        file_format = fdp.detect_format(str(input_path), file.filename)
        logger.info(f"Detected format: {file_format} for file: {file.filename}")
        
        if file_format == 'UNKNOWN':
            cleanup_temp_dir(temp_dir)
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Please upload a FireDNA/RiskBase PDF or Excel survey."
            )
        
        # Extract door data
        try:
            if file_format == 'TYPE_1':
                logger.info("Processing TYPE_1 (PDF with ART codes)")
                doors = fdp.extract_type1_pdf(str(input_path))
            elif file_format == 'TYPE_2':
                logger.info("Processing TYPE_2 (Excel with fault columns)")
                doors = fdp.extract_type2_excel(str(input_path))
            else:
                cleanup_temp_dir(temp_dir)
                raise HTTPException(status_code=400, detail=f"Unsupported format: {file_format}")
            
            logger.info(f"Extracted {len(doors)} doors from survey")
            
            if not doors:
                cleanup_temp_dir(temp_dir)
                raise HTTPException(
                    status_code=400,
                    detail="No door data could be extracted from the file. Please check the file format."
                )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error extracting door data: {str(e)}")
            cleanup_temp_dir(temp_dir)
            raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
        
        # Populate Excel template
        backend_dir = Path(__file__).parent
        template_path = backend_dir / "reference_files" / "WestPark_FireDoor_CostSheet_v3_AlphaSights.xlsx"
        output_filename = f"{client_name.replace(' ', '_')}_FireDoor_Quote.xlsx"
        output_path = Path(temp_dir) / output_filename
        
        logger.info(f"Template path: {template_path}, exists: {template_path.exists()}")
        logger.info(f"Output path: {output_path}")
        
        if not template_path.exists():
            cleanup_temp_dir(temp_dir)
            raise HTTPException(
                status_code=500,
                detail=f"Template file not found at: {template_path}"
            )
        
        try:
            result_path = fdp.populate_excel_template(doors, client_name, str(template_path), str(output_path))
            logger.info(f"populate_excel_template returned: {result_path}")
            
            # Double-check the file exists before returning
            if not output_path.exists():
                cleanup_temp_dir(temp_dir)
                raise HTTPException(
                    status_code=500,
                    detail=f"Output file was not created at: {output_path}"
                )
            
            logger.info(f"Returning file: {output_path}, size: {output_path.stat().st_size} bytes")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error populating Excel template: {str(e)}")
            cleanup_temp_dir(temp_dir)
            raise HTTPException(status_code=500, detail=f"Error generating quote: {str(e)}")
        
        # Return file with background cleanup
        return FileResponse(
            path=str(output_path),
            filename=output_filename,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            background=BackgroundTask(cleanup_temp_dir, temp_dir)
        )
    
    except Exception as e:
        # Final safety net - clean up on any unhandled exception
        cleanup_temp_dir(temp_dir)
        raise


# ============================================================================
# RATE CARD MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/api/firedoor/rates")
async def list_rate_card_items(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """
    Get all rate card items with optional search.
    """
    query = db.query(RateCardItem)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (RateCardItem.art_code.ilike(search_term)) |
            (RateCardItem.description.ilike(search_term)) |
            (RateCardItem.rate_card_code.ilike(search_term))
        )
    
    items = query.order_by(RateCardItem.art_code).all()
    
    return {
        "items": [{
            "id": item.id,
            "art_code": item.art_code,
            "description": item.description,
            "rate_card_code": item.rate_card_code,
            "rate_card_description": item.rate_card_description,
            "unit_price": item.unit_price,
            "category": item.category,
            "updated_at": item.updated_at.isoformat() if item.updated_at else None
        } for item in items],
        "count": len(items)
    }


@app.put("/api/firedoor/rates/{item_id}")
async def update_rate_card_item(
    item_id: int,
    unit_price: str = Form(...),
    category: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """
    Update a rate card item's price and category.
    Only unit_price and category are editable.
    """
    item = db.query(RateCardItem).filter(RateCardItem.id == item_id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Rate card item not found")
    
    item.unit_price = unit_price
    if category is not None:
        item.category = category
    
    db.commit()
    db.refresh(item)
    
    logger.info(f"User {current_user.email} updated rate card item {item.art_code} to {unit_price}")
    
    return {
        "id": item.id,
        "art_code": item.art_code,
        "description": item.description,
        "rate_card_code": item.rate_card_code,
        "unit_price": item.unit_price,
        "category": item.category,
        "updated_at": item.updated_at.isoformat() if item.updated_at else None
    }


@app.post("/api/firedoor/rates/seed")
async def seed_rate_card(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """
    Seed rate card items from CSV. Any authenticated user can seed.
    Only runs if table is empty.
    """
    import csv
    
    # Check if already seeded
    existing_count = db.query(RateCardItem).count()
    if existing_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Rate card already seeded with {existing_count} items. Delete existing items first if you want to re-seed."
        )
    
    # Load CSV
    backend_dir = Path(__file__).parent
    csv_path = backend_dir / "reference_files" / "BMTrada_ART_Codes_RateCard_Mapping.csv"
    
    if not csv_path.exists():
        raise HTTPException(status_code=500, detail=f"CSV file not found at {csv_path}")
    
    items = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            item = RateCardItem(
                art_code=row['ART Code'].strip(),
                description=row['Description'].strip(),
                rate_card_code=row['WestPark Rate Card Code'].strip(),
                unit_price=None,  # Will be set by user
                category=None
            )
            items.append(item)
    
    # Bulk insert
    db.bulk_save_objects(items)
    db.commit()
    
    logger.info(f"User {current_user.email} seeded {len(items)} rate card items")
    
    return {
        "message": f"Successfully seeded {len(items)} rate card items",
        "count": len(items)
    }


@app.delete("/api/firedoor/rates/clear")
async def clear_rate_card(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """
    Clear all rate card items. Any authenticated user can clear.
    Use with caution - this will delete all rate card data.
    """
    count = db.query(RateCardItem).delete()
    db.commit()
    
    logger.warning(f"User {current_user.email} cleared {count} rate card items")
    
    return {
        "message": f"Cleared {count} rate card items",
        "count": count
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
