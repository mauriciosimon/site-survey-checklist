from sqlalchemy import Column, Integer, String, Text, Boolean, Date, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(20), default=UserRole.user.value)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    checklists = relationship("Checklist", back_populates="owner")


class Checklist(Base):
    __tablename__ = "checklists"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Header Info
    site_name = Column(String(255), nullable=False)
    surveyor_name = Column(String(255))
    survey_date = Column(Date)
    site_address = Column(Text)
    client_name = Column(String(255))
    client_contact = Column(String(50))
    project_name = Column(String(255))

    # Building Specs (all text fields for flexibility)
    building_level = Column(String(100))
    ceiling_height = Column(String(100))  # meters
    skirting_size = Column(String(100))
    floor_type = Column(String(100))
    soffit_type = Column(String(100))
    existing_ceiling_trims = Column(Text)
    ceiling_void_depth = Column(String(100))  # mm
    floor_void_depth = Column(String(100))  # mm

    # Access & Logistics
    service_penetrations_scale = Column(String(100))
    goods_lift_available = Column(Boolean, default=False)
    goods_lift_notes = Column(Text)
    good_staircase_access = Column(Boolean, default=False)
    staircase_access_notes = Column(Text)
    loading_bay_restrictions = Column(Text)
    street_restrictions = Column(Text)
    noise_restrictions = Column(Text)

    # Finishes & Details
    mullion_perimeter_details = Column(Text)
    wall_deflection_needed = Column(Boolean, default=False)
    wall_deflection_notes = Column(Text)
    door_finish = Column(String(50))  # Veneer, PG, Laminate, Paint Grade, Other
    door_finish_other = Column(Text)
    frame_type = Column(String(50))  # Timber, Metal, Other
    frame_type_other = Column(Text)
    glazing_details = Column(Text)
    head_track_detail = Column(Text)

    # Project Status
    start_date = Column(Date)
    project_secured = Column(Boolean, default=False)
    programme_available = Column(Boolean, default=False)

    # Technical Requirements
    acoustic_baffles_required = Column(Boolean, default=False)
    fire_stopping_required = Column(Boolean, default=False)
    mullion_details = Column(Text)

    # Commercial
    pricing_details = Column(Text)
    supplier_notes = Column(Text)

    # Documentation
    site_photos = Column(JSON, default=list)
    additional_notes = Column(Text)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Monday.com integration
    monday_item_id = Column(String(50), nullable=True)

    owner = relationship("User", back_populates="checklists")
