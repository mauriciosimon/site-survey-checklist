from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from models import Checklist, User
from schemas import ChecklistCreate, ChecklistUpdate, UserCreate
from auth import get_password_hash
from typing import Optional, List


# ============ User CRUD ============

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(
        email=user.email,
        password_hash=get_password_hash(user.password),
        full_name=user.full_name,
        role="user"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_all_users(db: Session) -> List[User]:
    return db.query(User).order_by(User.created_at.desc()).all()


def get_users_with_checklist_count(db: Session):
    return db.query(
        User,
        func.count(Checklist.id).label("checklist_count")
    ).outerjoin(Checklist).group_by(User.id).all()


# ============ Checklist CRUD ============

def get_checklist(db: Session, checklist_id: int, user_id: Optional[int] = None, is_admin: bool = False):
    query = db.query(Checklist).filter(Checklist.id == checklist_id)
    if user_id and not is_admin:
        query = query.filter(Checklist.user_id == user_id)
    return query.first()


def get_checklists(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    user_id: Optional[int] = None,
    is_admin: bool = False
):
    query = db.query(Checklist)

    # Filter by user unless admin
    if user_id and not is_admin:
        query = query.filter(Checklist.user_id == user_id)

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


def get_all_checklists_with_owners(db: Session, skip: int = 0, limit: int = 100, user_filter: Optional[int] = None):
    query = db.query(Checklist)
    if user_filter:
        query = query.filter(Checklist.user_id == user_filter)
    return query.order_by(Checklist.created_at.desc()).offset(skip).limit(limit).all()


def create_checklist(db: Session, checklist: ChecklistCreate, user_id: Optional[int] = None, surveyor_name: Optional[str] = None):
    data = checklist.model_dump()
    if user_id:
        data["user_id"] = user_id
    if surveyor_name and not data.get("surveyor_name"):
        data["surveyor_name"] = surveyor_name
    db_checklist = Checklist(**data)
    db.add(db_checklist)
    db.commit()
    db.refresh(db_checklist)
    return db_checklist


def update_checklist(db: Session, checklist_id: int, checklist: ChecklistUpdate, user_id: Optional[int] = None, is_admin: bool = False):
    query = db.query(Checklist).filter(Checklist.id == checklist_id)
    if user_id and not is_admin:
        query = query.filter(Checklist.user_id == user_id)
    db_checklist = query.first()
    if db_checklist:
        update_data = checklist.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_checklist, key, value)
        db.commit()
        db.refresh(db_checklist)
    return db_checklist


def delete_checklist(db: Session, checklist_id: int, user_id: Optional[int] = None, is_admin: bool = False):
    query = db.query(Checklist).filter(Checklist.id == checklist_id)
    if user_id and not is_admin:
        query = query.filter(Checklist.user_id == user_id)
    db_checklist = query.first()
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
