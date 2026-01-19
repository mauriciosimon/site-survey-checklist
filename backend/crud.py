from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from models import Checklist, User, Deal, Lead
from schemas import ChecklistCreate, ChecklistUpdate, UserCreate, DealCreate, DealUpdate, LeadCreate, LeadUpdate
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


# ============ Deal CRUD ============

def get_deal(db: Session, deal_id: int) -> Optional[Deal]:
    return db.query(Deal).filter(Deal.id == deal_id).first()


def get_deal_by_monday_id(db: Session, monday_item_id: str) -> Optional[Deal]:
    return db.query(Deal).filter(Deal.monday_item_id == monday_item_id).first()


def get_deals(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    stage: Optional[str] = None,
    grade: Optional[str] = None,
    search: Optional[str] = None
) -> List[Deal]:
    query = db.query(Deal)

    if stage:
        query = query.filter(Deal.stage == stage)

    if grade:
        query = query.filter(Deal.grade == grade)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Deal.name.ilike(search_filter),
                Deal.company_name.ilike(search_filter),
                Deal.contact_name.ilike(search_filter)
            )
        )

    return query.order_by(Deal.created_at.desc()).offset(skip).limit(limit).all()


def create_deal(db: Session, deal: DealCreate) -> Deal:
    db_deal = Deal(**deal.model_dump())
    db.add(db_deal)
    db.commit()
    db.refresh(db_deal)
    return db_deal


def update_deal(db: Session, deal_id: int, deal: DealUpdate) -> Optional[Deal]:
    db_deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if db_deal:
        update_data = deal.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_deal, key, value)
        db.commit()
        db.refresh(db_deal)
    return db_deal


def delete_deal(db: Session, deal_id: int) -> bool:
    db_deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if db_deal:
        db.delete(db_deal)
        db.commit()
        return True
    return False


# ============ Lead CRUD ============

def get_lead(db: Session, lead_id: int) -> Optional[Lead]:
    """Get a single lead by ID."""
    return db.query(Lead).filter(Lead.id == lead_id).first()


def get_lead_by_monday_id(db: Session, monday_item_id: str) -> Optional[Lead]:
    """Get a lead by Monday.com item ID."""
    return db.query(Lead).filter(Lead.monday_item_id == monday_item_id).first()


def get_leads(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    source: Optional[str] = None,
    search: Optional[str] = None
) -> List[Lead]:
    """Get leads with optional filtering."""
    query = db.query(Lead)

    if status:
        query = query.filter(Lead.status == status)

    if priority:
        query = query.filter(Lead.priority == priority)

    if source:
        query = query.filter(Lead.source == source)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Lead.name.ilike(search_filter),
                Lead.contact_name.ilike(search_filter),
                Lead.email.ilike(search_filter),
                Lead.phone.ilike(search_filter)
            )
        )

    return query.order_by(Lead.created_at.desc()).offset(skip).limit(limit).all()


def create_lead(db: Session, lead: LeadCreate, owner_id: Optional[int] = None) -> Lead:
    """Create a new lead."""
    data = lead.model_dump()
    if owner_id:
        data["owner_id"] = owner_id
    db_lead = Lead(**data)
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead


def update_lead(db: Session, lead_id: int, lead: LeadUpdate) -> Optional[Lead]:
    """Update an existing lead."""
    db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if db_lead:
        update_data = lead.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_lead, key, value)
        db.commit()
        db.refresh(db_lead)
    return db_lead


def delete_lead(db: Session, lead_id: int) -> bool:
    """Delete a lead."""
    db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if db_lead:
        db.delete(db_lead)
        db.commit()
        return True
    return False
