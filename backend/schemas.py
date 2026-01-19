from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


# ============ User Schemas ============

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=1)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserWithStats(UserResponse):
    checklist_count: int = 0


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============ Checklist Schemas ============

class ChecklistBase(BaseModel):
    # Deal link (optional)
    deal_id: Optional[int] = None

    # Header Info
    site_name: str
    surveyor_name: Optional[str] = None
    survey_date: Optional[date] = None
    site_address: Optional[str] = None
    client_name: Optional[str] = None
    client_contact: Optional[str] = None
    project_name: Optional[str] = None

    # Building Specs
    building_level: Optional[int] = None
    ceiling_height: Optional[Decimal] = Field(None, ge=0, le=999.99)
    skirting_size: Optional[str] = None
    floor_type: Optional[str] = None
    soffit_type: Optional[str] = None
    existing_ceiling_trims: Optional[str] = None
    ceiling_void_depth: Optional[int] = None
    floor_void_depth: Optional[int] = None

    # Access & Logistics
    service_penetrations_scale: Optional[int] = Field(None, ge=1, le=10)
    goods_lift_available: Optional[bool] = False
    good_staircase_access: Optional[bool] = False
    loading_bay_restrictions: Optional[str] = None
    street_restrictions: Optional[str] = None
    noise_restrictions: Optional[str] = None

    # Finishes & Details
    mullion_perimeter_details: Optional[str] = None
    wall_deflection_needed: Optional[bool] = False
    door_finish: Optional[str] = None
    frame_type: Optional[str] = None
    glazing_details: Optional[str] = None
    head_track_detail: Optional[str] = None

    # Project Status
    start_date: Optional[date] = None
    project_secured: Optional[bool] = False
    programme_available: Optional[bool] = False

    # Technical Requirements
    acoustic_baffles_required: Optional[bool] = False
    fire_stopping_required: Optional[bool] = False
    mullion_details: Optional[str] = None

    # Commercial
    pricing_details: Optional[str] = None
    supplier_notes: Optional[str] = None

    # Documentation
    site_photos: Optional[List[str]] = []
    additional_notes: Optional[str] = None


class ChecklistCreate(ChecklistBase):
    pass


class ChecklistUpdate(ChecklistBase):
    site_name: Optional[str] = None


class ChecklistResponse(ChecklistBase):
    id: int
    user_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChecklistWithOwner(ChecklistResponse):
    owner_name: Optional[str] = None
    owner_email: Optional[str] = None


# ============ Deal Schemas ============

class DealBase(BaseModel):
    name: str
    owner_name: Optional[str] = None
    stage: Optional[str] = "Leads"  # Leads, Estimating, Submitted, Won, Lost, Declined
    grade: Optional[str] = None  # Grade 1, Grade 2, Grade 3

    # Company & Contact
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    # Deal details
    deal_type: Optional[str] = None  # New business, Renewal, Upsell
    products: Optional[List[str]] = []  # Fibre, Support, VoIP, 365, CCTV

    # Dates
    next_interaction: Optional[date] = None
    return_date: Optional[date] = None
    quote_sent_date: Optional[date] = None
    decision_date: Optional[date] = None
    close_date: Optional[date] = None
    status_update_date: Optional[date] = None

    # Probability
    close_probability: Optional[int] = Field(None, ge=0, le=100)

    # Location
    location_address: Optional[str] = None
    location_lat: Optional[Decimal] = None
    location_lng: Optional[Decimal] = None

    # Links & Files
    link_url: Optional[str] = None
    files: Optional[List[str]] = []

    # Monday.com sync
    monday_item_id: Optional[str] = None


class DealCreate(DealBase):
    pass


class DealUpdate(DealBase):
    name: Optional[str] = None


class DealResponse(DealBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
