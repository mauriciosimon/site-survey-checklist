from sqlalchemy import Column, Integer, String, Text, Boolean, Date, Numeric, DateTime, JSON
from sqlalchemy.sql import func
from database import Base


class Checklist(Base):
    __tablename__ = "checklists"

    id = Column(Integer, primary_key=True, index=True)

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
