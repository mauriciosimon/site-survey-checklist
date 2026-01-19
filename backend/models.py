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


class LeadStatus(str, enum.Enum):
    """Lead status/stage from Satoris Leads board"""
    new_lead = "New Lead"           # #ff6d3b (Dark Orange)
    working_on_it = "Working on it" # #fdab3d (Orange)
    prospect = "Prospect"           # #0086c0 (Blue)
    unqualified = "Unqualified"     # #df2f4a (Red)


class LeadPriority(str, enum.Enum):
    """Lead priority levels from Satoris"""
    low = "Low"                 # #0086c0 (Blue)
    medium = "Medium"           # #ffcb00 (Yellow)
    high = "High"               # #fdab3d (Orange)
    critical = "Critical"       # #df2f4a (Red)


class LeadSource(str, enum.Enum):
    """Lead source/channel from Satoris"""
    fractional_dubai = "Fractional Dubai"
    networking = "Networking"
    existing_contact = "Existing contact"
    linkedin = "Linkedin"
    wom = "WOM"  # Word of Mouth


class AccountStatus(str, enum.Enum):
    """Account status from Satoris Accounts board"""
    qualified = "Qualified"     # #fdab3d (Orange)
    active = "Active"           # #00c875 (Green)
    inactive = "Inactive"       # #df2f4a (Red)
    prospect = "Prospect"       # #007eb5 (Blue)


class AccountLabel(str, enum.Enum):
    """Account label/type from Satoris Accounts board"""
    contractor = "Contractor"                           # #4eccc6 (Australia)
    main_contractor = "Main Contractor"                 # #00c875 (Green)
    property_developer = "Property Developer"           # #ff007f (Dark Pink)
    construction_engineering = "Construction and Engineering"  # #784bd1 (Dark Purple)
    real_estate = "Real Estate and Property"            # #9d50dd (Purple)
    interior_design = "Interior Design and Furnishings" # #037f4c (Grass Green)
    food_hospitality = "Food and Hospitality"           # #579bfc (Bright Blue)
    consulting_financial = "Consulting and Financial Services"  # #cab641 (Mustered)


class ContactType(str, enum.Enum):
    """Contact type from Satoris Contacts board"""
    client = "Client"                           # #00c875 (Green)
    past_client = "Past client"                 # #cd9282 (Old Rose)
    potential_lead = "Potential Lead"           # #784bd1 (Dark Purple)
    in_progress = "In progress"                 # #5559df (Indigo)
    architecture = "Architecture"               # #579bfc (Bright Blue)
    interior_design = "Interior design"         # #9d50dd (Purple)
    design_build = "Design & Build"             # #cab641 (Mustered)
    fit_out_contractor = "Fit-Out Contractor"   # #fdab3d (Orange)
    smart_building = "Smart Building Solutions" # #333333 (Soft Black)
    main_contractor = "Main contractor"         # #bb3354 (Dark Red)
    joinery = "Joinery"                         # #ff007f (Dark Pink)
    partner = "Partner"                         # #ff5ac4 (Light Pink)
    mep_contractor = "MEP Contractors"          # #225091 (Navy)


class ContactIcpFit(str, enum.Enum):
    """Contact ICP Fit status from Satoris"""
    yes = "Yes"       # #00c875 (Green)
    maybe = "Maybe"   # #fdab3d (Orange)
    no = "No"         # #df2f4a (Red)


class ContactOutreachStage(str, enum.Enum):
    """Contact outreach stage from Satoris"""
    not_touched = "Not touched"           # #df2f4a (Red)
    profile_viewed = "Profile viewed"     # #007eb5 (Blue Links)
    engaged = "Engaged (Like/comment)"    # #9d50dd (Purple)
    connection_sent = "Connection sent"   # #037f4c (Grass Green)
    connected = "Connected"               # #579bfc (Bright Blue)
    dm_sent = "DM Sent"                   # #cab641 (Mustered)
    conversation_live = "Conversation live"  # #fdab3d (Orange)
    qualified = "Qualified"               # #00c875 (Green)
    parked = "Parked/not ICP"             # #ff007f (Dark Pink)


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


class Lead(Base):
    """Lead model based on Satoris Monday.com Leads board schema"""
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    monday_item_id = Column(String(50), unique=True, index=True, nullable=True)  # For Monday.com sync

    # Core fields
    name = Column(String(255), nullable=False)  # Lead/Company name (item name)
    status = Column(String(30), default=LeadStatus.new_lead.value)  # lead_status: New Lead, Working on it, Prospect, Unqualified
    priority = Column(String(20))  # priority: Low, Medium, High, Critical
    source = Column(String(50))  # status column: Networking, Linkedin, Existing contact, WOM, Fractional Dubai

    # Owner
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner_name = Column(String(255))  # lead_owner (text representation)

    # Contact Info
    contact_name = Column(String(255))  # lead_company (confusingly named in Monday - it's the person's name)
    job_title = Column(String(255))  # text column
    email = Column(String(255))  # lead_email
    phone = Column(String(50))  # lead_phone

    # Dates
    next_interaction_date = Column(Date)  # date column
    qualified_date = Column(Date)  # date4 column (follow up / date qualified)

    # Notes
    notes = Column(Text)  # Additional notes

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", backref="leads")


class Account(Base):
    """Account model based on Satoris Monday.com Accounts board schema"""
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    monday_item_id = Column(String(50), unique=True, index=True, nullable=True)  # For Monday.com sync

    # Core fields
    name = Column(String(255), nullable=False)  # Account/Company name (item name)
    status = Column(String(30), default=AccountStatus.prospect.value)  # status9: Qualified, Active, Inactive, Prospect
    label = Column(String(50))  # color_mkvcf1b0: Contractor, Main Contractor, Property Developer, etc.

    # Industry & Business Info
    industry = Column(Text)  # industry dropdown (can be multiple, stored as comma-separated or JSON)
    employee_count = Column(String(50))  # employee_count: 1-10, 11-50, 51-100, 101-250, etc.
    account_type = Column(String(100))  # text_mkzj1hb9 (Type field)

    # Contact & Web
    website = Column(Text)  # company_domain
    company_profile_url = Column(Text)  # company_profile link

    # Location
    address = Column(Text)  # location.address
    location_lat = Column(Numeric(10, 7))  # location.lat
    location_lng = Column(Numeric(10, 7))  # location.lng

    # Owner
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner_name = Column(String(255))  # Owner name (text representation)
    owner_job_title = Column(String(255))  # text_mkzj6z1z (Job title field)

    # Notes
    notes = Column(Text)  # Additional notes

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", backref="accounts")
    contacts = relationship("Contact", back_populates="account")


class Contact(Base):
    """Contact model based on Satoris Monday.com Contacts board schema"""
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    monday_item_id = Column(String(50), unique=True, index=True, nullable=True)  # For Monday.com sync

    # Core fields
    name = Column(String(255), nullable=False)  # Contact name (item name)
    company = Column(String(255))  # text column - Company name
    contact_type = Column(String(50))  # status: Client, Past client, Potential Lead, Architecture, etc.

    # Job info
    job_title = Column(String(255))  # text_mkzj9zfp
    title_role = Column(String(50))  # title5 dropdown: CEO, COO, CIO, BDM, PM, Co-founder, etc.
    tier = Column(String(50))  # text_mkzj1q6x: Tier 1, Tier 2, Tier 3

    # Contact info
    email = Column(String(255))  # contact_email
    phone = Column(String(50))  # contact_phone
    linkedin_url = Column(Text)  # linkedin__1
    location = Column(String(255))  # location__1

    # Sales/Outreach fields
    icp_fit = Column(String(20))  # color_mkzj6yzf: Yes, Maybe, No
    outreach_stage = Column(String(50))  # color_mkzjj431: Not touched, Profile viewed, Connected, etc.
    source = Column(String(50))  # color_mkveb8kg
    next_action_date = Column(Date)  # date_mkzjzmwx

    # Additional info
    industry = Column(String(255))  # text_mkv6vp03
    description = Column(Text)  # about__1
    about = Column(Text)  # long_text_mksawnbc
    birthday = Column(Date)  # date
    tags = Column(JSON, default=list)  # tag_mkveenam

    # Relationships
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner_name = Column(String(255))  # Owner name (text representation)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    account = relationship("Account", back_populates="contacts")
    owner = relationship("User", backref="contacts")


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
