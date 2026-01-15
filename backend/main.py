import os
import uuid
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional

from database import engine, get_db, Base
from schemas import ChecklistCreate, ChecklistUpdate, ChecklistResponse
import crud

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Site Visit Checklist API",
    description="API for managing construction site visit checklists",
    version="1.0.0"
)

# CORS middleware - allow Vercel deployments and localhost
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3001,http://localhost:3000").split(",")
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
    return {"message": "Site Visit Checklist API", "docs": "/docs"}


@app.get("/checklists", response_model=List[ChecklistResponse])
def list_checklists(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return crud.get_checklists(db, skip=skip, limit=limit, search=search)


@app.get("/checklists/{checklist_id}", response_model=ChecklistResponse)
def get_checklist(checklist_id: int, db: Session = Depends(get_db)):
    checklist = crud.get_checklist(db, checklist_id)
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")
    return checklist


@app.post("/checklists", response_model=ChecklistResponse)
def create_checklist(checklist: ChecklistCreate, db: Session = Depends(get_db)):
    return crud.create_checklist(db, checklist)


@app.put("/checklists/{checklist_id}", response_model=ChecklistResponse)
def update_checklist(
    checklist_id: int,
    checklist: ChecklistUpdate,
    db: Session = Depends(get_db)
):
    db_checklist = crud.update_checklist(db, checklist_id, checklist)
    if not db_checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")
    return db_checklist


@app.delete("/checklists/{checklist_id}")
def delete_checklist(checklist_id: int, db: Session = Depends(get_db)):
    success = crud.delete_checklist(db, checklist_id)
    if not success:
        raise HTTPException(status_code=404, detail="Checklist not found")
    return {"message": "Checklist deleted successfully"}


@app.post("/checklists/{checklist_id}/photos", response_model=ChecklistResponse)
async def upload_photo(
    checklist_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    checklist = crud.get_checklist(db, checklist_id)
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
