from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List, Any
from datetime import date, datetime


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
    # Header Info
    site_name: str
    surveyor_name: Optional[str] = None
    survey_date: Optional[date] = None
    site_address: Optional[str] = None
    client_name: Optional[str] = None
    client_contact: Optional[str] = None
    project_name: Optional[str] = None

    # Building Specs (all text fields for flexibility)
    building_level: Optional[str] = None
    ceiling_height: Optional[str] = None
    skirting_size: Optional[str] = None
    floor_type: Optional[str] = None
    soffit_type: Optional[str] = None
    existing_ceiling_trims: Optional[str] = None
    ceiling_void_depth: Optional[str] = None
    floor_void_depth: Optional[str] = None

    # Access & Logistics
    service_penetrations_scale: Optional[str] = None
    goods_lift_available: Optional[bool] = False
    goods_lift_notes: Optional[str] = None
    good_staircase_access: Optional[bool] = False
    staircase_access_notes: Optional[str] = None
    loading_bay_restrictions: Optional[str] = None
    street_restrictions: Optional[str] = None
    noise_restrictions: Optional[str] = None

    # Finishes & Details
    mullion_perimeter_details: Optional[str] = None
    wall_deflection_needed: Optional[bool] = False
    wall_deflection_notes: Optional[str] = None
    door_finish: Optional[str] = None
    door_finish_other: Optional[str] = None
    frame_type: Optional[str] = None
    frame_type_other: Optional[str] = None
    glazing_details: Optional[str] = None
    head_track_detail: Optional[str] = None

    # Project Status
    start_date: Optional[date] = None
    project_secured: Optional[bool] = False
    programme_available: Optional[bool] = False

    # Technical Requirements
    acoustic_baffles_required: Optional[bool] = False
    acoustic_baffles_notes: Optional[str] = None
    fire_stopping_required: Optional[bool] = False
    fire_stopping_notes: Optional[str] = None

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
    monday_item_id: Optional[str] = None

    # Coerce numeric values to strings for text fields (handles legacy data)
    @field_validator(
        'building_level', 'ceiling_height', 'skirting_size', 'floor_type',
        'soffit_type', 'ceiling_void_depth', 'floor_void_depth',
        'service_penetrations_scale', mode='before'
    )
    @classmethod
    def coerce_to_string(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        return str(v)

    class Config:
        from_attributes = True


class ChecklistWithOwner(ChecklistResponse):
    owner_name: Optional[str] = None
    owner_email: Optional[str] = None
