from sqlalchemy.orm import Session
from sqlalchemy import or_
from models import Checklist
from schemas import ChecklistCreate, ChecklistUpdate
from typing import Optional


def get_checklist(db: Session, checklist_id: int):
    return db.query(Checklist).filter(Checklist.id == checklist_id).first()


def get_checklists(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
):
    query = db.query(Checklist)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Checklist.site_name.ilike(search_filter),
                Checklist.client_name.ilike(search_filter),
                Checklist.project_name.ilike(search_filter),
                Checklist.site_address.ilike(search_filter)
            )
        )

    return query.order_by(Checklist.created_at.desc()).offset(skip).limit(limit).all()


def create_checklist(db: Session, checklist: ChecklistCreate):
    db_checklist = Checklist(**checklist.model_dump())
    db.add(db_checklist)
    db.commit()
    db.refresh(db_checklist)
    return db_checklist


def update_checklist(db: Session, checklist_id: int, checklist: ChecklistUpdate):
    db_checklist = db.query(Checklist).filter(Checklist.id == checklist_id).first()
    if db_checklist:
        update_data = checklist.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_checklist, key, value)
        db.commit()
        db.refresh(db_checklist)
    return db_checklist


def delete_checklist(db: Session, checklist_id: int):
    db_checklist = db.query(Checklist).filter(Checklist.id == checklist_id).first()
    if db_checklist:
        db.delete(db_checklist)
        db.commit()
        return True
    return False


def add_photo_to_checklist(db: Session, checklist_id: int, photo_path: str):
    db_checklist = db.query(Checklist).filter(Checklist.id == checklist_id).first()
    if db_checklist:
        photos = db_checklist.site_photos or []
        photos.append(photo_path)
        db_checklist.site_photos = photos
        db.commit()
        db.refresh(db_checklist)
    return db_checklist
