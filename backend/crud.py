from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from models import Checklist, User, Deal, Lead, Account, Contact, Task, Workspace
from schemas import (
    ChecklistCreate, ChecklistUpdate, UserCreate,
    DealCreate, DealUpdate, LeadCreate, LeadUpdate,
    AccountCreate, AccountUpdate, ContactCreate, ContactUpdate,
    TaskCreate, TaskUpdate, WorkspaceCreate, WorkspaceUpdate
)
from datetime import date as date_type
from auth import get_password_hash
from typing import Optional, List


# ============ Workspace CRUD ============

def get_workspace(db: Session, workspace_id: int) -> Optional[Workspace]:
    """Get a single workspace by ID."""
    return db.query(Workspace).filter(Workspace.id == workspace_id).first()


def get_workspace_by_monday_id(db: Session, monday_workspace_id: str) -> Optional[Workspace]:
    """Get a workspace by Monday.com workspace ID."""
    return db.query(Workspace).filter(Workspace.monday_workspace_id == monday_workspace_id).first()


def get_workspaces(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    search: Optional[str] = None
) -> List[Workspace]:
    """Get workspaces with optional filtering."""
    query = db.query(Workspace)

    if is_active is not None:
        query = query.filter(Workspace.is_active == is_active)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Workspace.name.ilike(search_filter),
                Workspace.description.ilike(search_filter)
            )
        )

    return query.order_by(Workspace.name.asc()).offset(skip).limit(limit).all()


def get_workspace_with_counts(db: Session, workspace_id: int):
    """Get workspace with entity counts."""
    workspace = get_workspace(db, workspace_id)
    if not workspace:
        return None

    counts = {
        'lead_count': db.query(Lead).filter(Lead.workspace_id == workspace_id).count(),
        'deal_count': db.query(Deal).filter(Deal.workspace_id == workspace_id).count(),
        'account_count': db.query(Account).filter(Account.workspace_id == workspace_id).count(),
        'contact_count': db.query(Contact).filter(Contact.workspace_id == workspace_id).count(),
        'task_count': db.query(Task).filter(Task.workspace_id == workspace_id).count(),
        'checklist_count': db.query(Checklist).filter(Checklist.workspace_id == workspace_id).count(),
    }
    return workspace, counts


def create_workspace(db: Session, workspace: WorkspaceCreate) -> Workspace:
    """Create a new workspace."""
    data = workspace.model_dump()
    db_workspace = Workspace(**data)
    db.add(db_workspace)
    db.commit()
    db.refresh(db_workspace)
    return db_workspace


def update_workspace(db: Session, workspace_id: int, workspace: WorkspaceUpdate) -> Optional[Workspace]:
    """Update an existing workspace."""
    db_workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if db_workspace:
        update_data = workspace.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_workspace, key, value)
        db.commit()
        db.refresh(db_workspace)
    return db_workspace


def delete_workspace(db: Session, workspace_id: int) -> bool:
    """Delete a workspace."""
    db_workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if db_workspace:
        db.delete(db_workspace)
        db.commit()
        return True
    return False


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
    workspace_id: Optional[int] = None,
    search: Optional[str] = None,
    user_id: Optional[int] = None,
    is_admin: bool = False
):
    query = db.query(Checklist)

    if workspace_id:
        query = query.filter(Checklist.workspace_id == workspace_id)

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
    """Get a single deal by ID."""
    return db.query(Deal).filter(Deal.id == deal_id).first()


def get_deal_by_monday_id(db: Session, monday_item_id: str) -> Optional[Deal]:
    """Get a deal by Monday.com item ID."""
    return db.query(Deal).filter(Deal.monday_item_id == monday_item_id).first()


def get_deals(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    workspace_id: Optional[int] = None,
    stage: Optional[str] = None,
    status: Optional[str] = None,
    grade: Optional[str] = None,
    deal_type: Optional[str] = None,
    owner_id: Optional[int] = None,
    account_id: Optional[int] = None,
    lead_id: Optional[int] = None,
    search: Optional[str] = None
) -> List[Deal]:
    """Get deals with optional filtering."""
    query = db.query(Deal)

    if workspace_id:
        query = query.filter(Deal.workspace_id == workspace_id)

    if stage:
        query = query.filter(Deal.stage == stage)

    if status:
        query = query.filter(Deal.status == status)

    if grade:
        query = query.filter(Deal.grade == grade)

    if deal_type:
        query = query.filter(Deal.deal_type == deal_type)

    if owner_id:
        query = query.filter(Deal.owner_id == owner_id)

    if account_id:
        query = query.filter(Deal.account_id == account_id)

    if lead_id:
        query = query.filter(Deal.lead_id == lead_id)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Deal.name.ilike(search_filter),
                Deal.company_name.ilike(search_filter),
                Deal.contact_name.ilike(search_filter),
                Deal.email.ilike(search_filter)
            )
        )

    return query.order_by(Deal.created_at.desc()).offset(skip).limit(limit).all()


def create_deal(db: Session, deal: DealCreate, owner_id: Optional[int] = None) -> Deal:
    """Create a new deal."""
    data = deal.model_dump()
    if owner_id:
        data["owner_id"] = owner_id
    db_deal = Deal(**data)
    db.add(db_deal)
    db.commit()
    db.refresh(db_deal)
    return db_deal


def update_deal(db: Session, deal_id: int, deal: DealUpdate) -> Optional[Deal]:
    """Update an existing deal."""
    db_deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if db_deal:
        update_data = deal.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_deal, key, value)
        db.commit()
        db.refresh(db_deal)
    return db_deal


def delete_deal(db: Session, deal_id: int) -> bool:
    """Delete a deal."""
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
    workspace_id: Optional[int] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    source: Optional[str] = None,
    search: Optional[str] = None
) -> List[Lead]:
    """Get leads with optional filtering."""
    query = db.query(Lead)

    if workspace_id:
        query = query.filter(Lead.workspace_id == workspace_id)

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


# ============ Account CRUD ============

def get_account(db: Session, account_id: int) -> Optional[Account]:
    """Get a single account by ID."""
    return db.query(Account).filter(Account.id == account_id).first()


def get_account_by_monday_id(db: Session, monday_item_id: str) -> Optional[Account]:
    """Get an account by Monday.com item ID."""
    return db.query(Account).filter(Account.monday_item_id == monday_item_id).first()


def get_accounts(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    workspace_id: Optional[int] = None,
    status: Optional[str] = None,
    label: Optional[str] = None,
    industry: Optional[str] = None,
    search: Optional[str] = None
) -> List[Account]:
    """Get accounts with optional filtering."""
    query = db.query(Account)

    if workspace_id:
        query = query.filter(Account.workspace_id == workspace_id)

    if status:
        query = query.filter(Account.status == status)

    if label:
        query = query.filter(Account.label == label)

    if industry:
        # Industry can be comma-separated, so use ilike for partial match
        query = query.filter(Account.industry.ilike(f"%{industry}%"))

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Account.name.ilike(search_filter),
                Account.industry.ilike(search_filter),
                Account.address.ilike(search_filter),
                Account.website.ilike(search_filter)
            )
        )

    return query.order_by(Account.created_at.desc()).offset(skip).limit(limit).all()


def create_account(db: Session, account: AccountCreate, owner_id: Optional[int] = None) -> Account:
    """Create a new account."""
    data = account.model_dump()
    if owner_id:
        data["owner_id"] = owner_id
    db_account = Account(**data)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


def update_account(db: Session, account_id: int, account: AccountUpdate) -> Optional[Account]:
    """Update an existing account."""
    db_account = db.query(Account).filter(Account.id == account_id).first()
    if db_account:
        update_data = account.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_account, key, value)
        db.commit()
        db.refresh(db_account)
    return db_account


def delete_account(db: Session, account_id: int) -> bool:
    """Delete an account."""
    db_account = db.query(Account).filter(Account.id == account_id).first()
    if db_account:
        db.delete(db_account)
        db.commit()
        return True
    return False


# ============ Contact CRUD ============

def get_contact(db: Session, contact_id: int) -> Optional[Contact]:
    """Get a single contact by ID."""
    return db.query(Contact).filter(Contact.id == contact_id).first()


def get_contact_by_monday_id(db: Session, monday_item_id: str) -> Optional[Contact]:
    """Get a contact by Monday.com item ID."""
    return db.query(Contact).filter(Contact.monday_item_id == monday_item_id).first()


def get_contacts(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    workspace_id: Optional[int] = None,
    contact_type: Optional[str] = None,
    account_id: Optional[int] = None,
    icp_fit: Optional[str] = None,
    outreach_stage: Optional[str] = None,
    search: Optional[str] = None
) -> List[Contact]:
    """Get contacts with optional filtering."""
    query = db.query(Contact)

    if workspace_id:
        query = query.filter(Contact.workspace_id == workspace_id)

    if contact_type:
        query = query.filter(Contact.contact_type == contact_type)

    if account_id:
        query = query.filter(Contact.account_id == account_id)

    if icp_fit:
        query = query.filter(Contact.icp_fit == icp_fit)

    if outreach_stage:
        query = query.filter(Contact.outreach_stage == outreach_stage)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Contact.name.ilike(search_filter),
                Contact.company.ilike(search_filter),
                Contact.email.ilike(search_filter),
                Contact.job_title.ilike(search_filter),
                Contact.location.ilike(search_filter)
            )
        )

    return query.order_by(Contact.created_at.desc()).offset(skip).limit(limit).all()


def create_contact(db: Session, contact: ContactCreate, owner_id: Optional[int] = None) -> Contact:
    """Create a new contact."""
    data = contact.model_dump()
    if owner_id:
        data["owner_id"] = owner_id
    db_contact = Contact(**data)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def update_contact(db: Session, contact_id: int, contact: ContactUpdate) -> Optional[Contact]:
    """Update an existing contact."""
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if db_contact:
        update_data = contact.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact


def delete_contact(db: Session, contact_id: int) -> bool:
    """Delete a contact."""
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if db_contact:
        db.delete(db_contact)
        db.commit()
        return True
    return False


# ============ Task CRUD ============

def get_task(db: Session, task_id: int) -> Optional[Task]:
    """Get a single task by ID."""
    return db.query(Task).filter(Task.id == task_id).first()


def get_task_by_monday_id(db: Session, monday_item_id: str) -> Optional[Task]:
    """Get a task by Monday.com item ID."""
    return db.query(Task).filter(Task.monday_item_id == monday_item_id).first()


def get_tasks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    workspace_id: Optional[int] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    task_type: Optional[str] = None,
    owner_id: Optional[int] = None,
    due_date_from: Optional[date_type] = None,
    due_date_to: Optional[date_type] = None,
    deal_id: Optional[int] = None,
    lead_id: Optional[int] = None,
    account_id: Optional[int] = None,
    search: Optional[str] = None
) -> List[Task]:
    """Get tasks with optional filtering."""
    query = db.query(Task)

    if workspace_id:
        query = query.filter(Task.workspace_id == workspace_id)

    if status:
        query = query.filter(Task.status == status)

    if priority:
        query = query.filter(Task.priority == priority)

    if task_type:
        query = query.filter(Task.task_type == task_type)

    if owner_id:
        query = query.filter(Task.owner_id == owner_id)

    if due_date_from:
        query = query.filter(Task.due_date >= due_date_from)

    if due_date_to:
        query = query.filter(Task.due_date <= due_date_to)

    if deal_id:
        query = query.filter(Task.deal_id == deal_id)

    if lead_id:
        query = query.filter(Task.lead_id == lead_id)

    if account_id:
        query = query.filter(Task.account_id == account_id)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Task.name.ilike(search_filter),
                Task.related_to.ilike(search_filter),
                Task.notes.ilike(search_filter)
            )
        )

    return query.order_by(Task.due_date.asc().nullslast(), Task.created_at.desc()).offset(skip).limit(limit).all()


def create_task(db: Session, task: TaskCreate, owner_id: Optional[int] = None) -> Task:
    """Create a new task."""
    data = task.model_dump()
    if owner_id:
        data["owner_id"] = owner_id
    db_task = Task(**data)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: int, task: TaskUpdate) -> Optional[Task]:
    """Update an existing task."""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task:
        update_data = task.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_task, key, value)
        db.commit()
        db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int) -> bool:
    """Delete a task."""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
        return True
    return False
