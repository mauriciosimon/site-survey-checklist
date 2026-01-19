from sqlalchemy import Column, Integer, String, Text, Boolean, Date, Numeric, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"


class DealStage(str, enum.Enum):
    leads = "Leads"
    estimating = "Estimating"
    submitted = "Submitted"
    won = "Won"
    lost = "Lost"
    declined = "Declined"


class DealGrade(str, enum.Enum):
    grade_1 = "Grade 1"  # Hot - Pink (#ffadad)
    grade_2 = "Grade 2"  # Warm - Orange (#fdab3d)
    grade_3 = "Grade 3"  # Cold - Green (#9cd326)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(20), default=UserRole.user.value)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    checklists = relationship("Checklist", back_populates="owner")


class Deal(Base):
    """Deal model based on Monday.com Opportunity board structure"""
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    monday_item_id = Column(String(50), unique=True, index=True, nullable=True)  # For Monday.com sync

    # Core fields (from Monday columns)
    name = Column(String(255), nullable=False)  # name
    owner_name = Column(String(255))  # deal_owner
    stage = Column(String(20), default=DealStage.leads.value)  # deal_stage (group)
    grade = Column(String(20))  # color_mkt89c3f - Grade 1/2/3 for pipeline dashboards

    # Company & Contact
    company_name = Column(String(255))  # text_mksp2w2b (Company - new)
    contact_name = Column(String(255))  # text0 (Contact - new)
    email = Column(String(255))  # email_mksyzvf9
    phone = Column(String(50))  # phone_mksyet5a

    # Deal details
    deal_type = Column(String(50))  # dropdown_mkzf2pz2: New business, Renewal, Upsell
    products = Column(JSON, default=list)  # dropdown_mkzfv82s: Fibre, Support, VoIP, 365, CCTV

    # Dates
    next_interaction = Column(Date)  # date
    return_date = Column(Date)  # date_mkt86yvg
    quote_sent_date = Column(Date)  # date_mkt85aje
    decision_date = Column(Date)  # date_mkt85f7z
    close_date = Column(Date)  # deal_close_date
    status_update_date = Column(Date)  # date_mktzcz9a

    # Probability
    close_probability = Column(Integer)  # numeric_mkt8frbn (0-100)

    # Location
    location_address = Column(Text)  # location_mksy2kz1.address
    location_lat = Column(Numeric(10, 7))  # location_mksy2kz1.lat
    location_lng = Column(Numeric(10, 7))  # location_mksy2kz1.lng

    # Links & Files
    link_url = Column(Text)  # link_mktk2t5j
    files = Column(JSON, default=list)  # file_mkpkxwgs

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    checklists = relationship("Checklist", back_populates="deal")


class Checklist(Base):
    __tablename__ = "checklists"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=True)  # Link to Monday Opportunity

    # Header Info
    site_name = Column(String(255), nullable=False)
    surveyor_name = Column(String(255))
    survey_date = Column(Date)
    site_address = Column(Text)
    client_name = Column(String(255))
    client_contact = Column(String(50))
    project_name = Column(String(255))

    # Building Specs
    building_level = Column(Integer)
    ceiling_height = Column(Numeric(5, 2))  # meters
    skirting_size = Column(String(20))  # 100mm, 150mm, 200mm, Other
    floor_type = Column(String(50))  # Raised Floor, Concrete, Screed, Other
    soffit_type = Column(String(50))  # Rib Deck, Concrete, Other
    existing_ceiling_trims = Column(Text)
    ceiling_void_depth = Column(Integer)  # mm
    floor_void_depth = Column(Integer)  # mm

    # Access & Logistics
    service_penetrations_scale = Column(Integer)  # 1-10
    goods_lift_available = Column(Boolean, default=False)
    good_staircase_access = Column(Boolean, default=False)
    loading_bay_restrictions = Column(Text)
    street_restrictions = Column(Text)
    noise_restrictions = Column(Text)

    # Finishes & Details
    mullion_perimeter_details = Column(Text)
    wall_deflection_needed = Column(Boolean, default=False)
    door_finish = Column(String(50))  # Veneer, PG, Laminate, Paint Grade, Other
    frame_type = Column(String(20))  # Timber, Metal
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

    owner = relationship("User", back_populates="checklists")
    deal = relationship("Deal", back_populates="checklists")
