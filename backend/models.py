from sqlalchemy import Column, Integer, String, Text, Boolean, Date, Numeric, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"


class DealStage(str, enum.Enum):
    """Deal stage/group from Satoris Deals board"""
    prospects = "Prospects"              # #0086c0 (Blue)
    preparing_proposal = "Preparing proposal"  # #fdab3d (Orange)
    proposal_sent = "Proposal sent"      # #9cd326 (Lime Green)
    closed_won = "Closed Won"            # #00c875 (Green)
    lost = "Lost"                        # #df2f4a (Red)
    completed = "Completed"              # #c4c4c4 (Gray)


class DealStatus(str, enum.Enum):
    """Deal status from Satoris Deals board (deal_stage column)"""
    new_deal = "New deal"                    # #579bfc (Bright Blue)
    prospect = "Prospect"                    # #0086c0 (Blue)
    preparing_proposal = "Preparing proposal"  # #fdab3d (Orange)
    proposal = "Proposal"                    # #cab641 (Mustered)
    proposal_sent = "Proposal sent"          # #9cd326 (Lime Green)
    waiting_for_review = "Waiting for review"  # #784bd1 (Dark Purple)
    need_info = "Need info"                  # #9d50dd (Purple)
    qualified = "Qualified"                  # #037f4c (Grass Green)
    closed_won = "Closed won"                # #00c875 (Green)
    lost = "Lost"                            # #df2f4a (Red)
    completed = "Completed"                  # #c4c4c4 (Gray)


class DealType(str, enum.Enum):
    """Deal type from Satoris Deals board"""
    monthly = "Monthly"    # #00c875 (Green)
    project = "Project"    # #0086c0 (Blue)


class DealGrade(str, enum.Enum):
    """Deal grade/temperature from Satoris"""
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


class TaskStatus(str, enum.Enum):
    """Task status from Satoris Tasks board"""
    to_do = "To do"                       # #ff6d3b (Dark Orange)
    working_on_it = "Working on it"       # #fdab3d (Orange)
    done = "Done"                         # #00c875 (Green)
    stuck = "Stuck"                       # #df2f4a (Red)
    on_hold = "On hold"                   # #cd9282 (Old Rose)
    need_info = "Need info"               # #9d50dd (Purple)
    waiting_for_review = "Waiting for review"  # #579bfc (Bright Blue)


class TaskPriority(str, enum.Enum):
    """Task priority levels"""
    critical = "Critical"   # #df2f4a (Red)
    high = "High"           # #fdab3d (Orange)
    medium = "Medium"       # #ffcb00 (Yellow)
    low = "Low"             # #0086c0 (Blue)


class TaskType(str, enum.Enum):
    """Task type from Satoris Tasks board"""
    finance = "Finance"         # #9cd326 (Lime Green)
    birocratic = "Birocratic"   # #66ccff (Turquoise)
    marketing = "Marketing"     # #ffadad (Peach)
    other = "Other"             # #cab641 (Mustered)


class OpportunityStage(str, enum.Enum):
    """Opportunity stage from BTG Opportunity board"""
    leads = "Leads"                     # #ff6d3b (Dark Orange) - New lead
    estimating = "Estimating"           # #ffcb00 (Yellow)
    submitted = "Submitted"             # #cab641 (Mustered)
    submitted_revisions = "Submitted Revisions"  # #fdab3d (Orange)
    small_works = "Small works"         # #66ccff (Turquoise)
    won = "Won"                         # #00c875 (Green)
    signed_small_works = "Signed - Small works"  # #037f4c (Grass Green)
    lost = "Lost"                       # #df2f4a (Red)
    declined = "Declined"               # #c4c4c4 (Grey)


class OpportunityGrade(str, enum.Enum):
    """Opportunity grade/temperature - color-coded priority tiers"""
    grade_1 = "Grade 1"  # #ffadad (Peach/Pink) - Highest Priority / Hot
    grade_2 = "Grade 2"  # #fdab3d (Orange) - Medium Priority / Warm
    grade_3 = "Grade 3"  # #9cd326 (Lime Green) - Lower Priority / Cold


class Workspace(Base):
    """Workspace model to organize data like Monday.com workspaces"""
    __tablename__ = "workspaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    monday_workspace_id = Column(String(50), unique=True, index=True, nullable=True)
    icon = Column(String(10))  # Single character or emoji
    color = Column(String(20))  # Hex color code
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    deals = relationship("Deal", back_populates="workspace")
    leads = relationship("Lead", back_populates="workspace")
    accounts = relationship("Account", back_populates="workspace")
    contacts = relationship("Contact", back_populates="workspace")
    tasks = relationship("Task", back_populates="workspace")
    opportunities = relationship("Opportunity", back_populates="workspace")
    checklists = relationship("Checklist", back_populates="workspace")


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
    """Deal model based on Satoris Monday.com Deals board schema"""
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=True, index=True)
    monday_item_id = Column(String(50), unique=True, index=True, nullable=True)  # For Monday.com sync

    # Core fields
    name = Column(String(255), nullable=False)  # Item name
    stage = Column(String(30), default=DealStage.prospects.value)  # Board group: Prospects, Preparing proposal, etc.
    status = Column(String(30), default=DealStatus.new_deal.value)  # deal_stage column status
    grade = Column(String(20))  # Grade 1/2/3 for pipeline temperature

    # Owner
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner_name = Column(String(255))  # deal_owner (text representation)

    # Company & Contact (text fields, not relations)
    company_name = Column(String(255))  # Company name from account mirror
    contact_name = Column(String(255))  # text0 (Contact name)
    email = Column(String(255))  # Email
    phone = Column(String(50))  # Phone

    # Deal details
    deal_type = Column(String(20))  # dropdown_mkxsyxw3: Monthly, Project
    value = Column(Numeric(12, 2))  # deal_value (GBP currency)
    deal_length = Column(Integer)  # Deal length in months (formula field)

    # Dates
    next_interaction = Column(Date)  # date column
    proposal_sent_date = Column(Date)  # date_mksary1j
    close_date = Column(Date)  # deal_close_date

    # Files
    files = Column(JSON, default=list)  # file_mks57s05

    # Relationships to other entities
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    workspace = relationship("Workspace", back_populates="deals")
    owner = relationship("User", backref="deals")
    account = relationship("Account", backref="deals")
    lead = relationship("Lead", backref="deals")
    checklists = relationship("Checklist", back_populates="deal")


class Lead(Base):
    """Lead model based on Satoris Monday.com Leads board schema"""
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=True, index=True)
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
    workspace = relationship("Workspace", back_populates="leads")
    owner = relationship("User", backref="leads")


class Account(Base):
    """Account model based on Satoris Monday.com Accounts board schema"""
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=True, index=True)
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
    workspace = relationship("Workspace", back_populates="accounts")
    owner = relationship("User", backref="accounts")
    contacts = relationship("Contact", back_populates="account")


class Contact(Base):
    """Contact model based on Satoris Monday.com Contacts board schema"""
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=True, index=True)
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
    workspace = relationship("Workspace", back_populates="contacts")
    account = relationship("Account", back_populates="contacts")
    owner = relationship("User", backref="contacts")


class Task(Base):
    """Task model based on Satoris Monday.com Tasks board schema"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=True, index=True)
    monday_item_id = Column(String(50), unique=True, index=True, nullable=True)  # For Monday.com sync

    # Core fields
    name = Column(String(255), nullable=False)  # Task name (item name)
    status = Column(String(30), default=TaskStatus.to_do.value)  # To do, Working on it, Done, Stuck, etc.
    priority = Column(String(20))  # Critical, High, Medium, Low
    task_type = Column(String(30))  # Finance, Birocratic, Marketing, Other

    # Dates
    due_date = Column(Date)  # date4
    close_date = Column(Date)  # date

    # Context/Related items
    related_to = Column(String(255))  # Text field for linking context (deal name, lead name, etc.)

    # Foreign keys for relationships
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)

    # Assignment
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner_name = Column(String(255))  # Owner name (text representation)

    # Additional info
    notes = Column(Text)
    files = Column(JSON, default=list)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    workspace = relationship("Workspace", back_populates="tasks")
    deal = relationship("Deal", backref="tasks")
    lead = relationship("Lead", backref="tasks")
    account = relationship("Account", backref="tasks")
    contact = relationship("Contact", backref="tasks")
    owner = relationship("User", backref="tasks")


class Opportunity(Base):
    """Opportunity model based on BTG Monday.com Opportunity board schema"""
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=True, index=True)
    monday_item_id = Column(String(50), unique=True, index=True, nullable=True)

    # Core fields
    name = Column(String(255), nullable=False)  # Opportunity name
    stage = Column(String(50), default=OpportunityStage.leads.value)  # Leads, Estimating, Submitted, Won, Lost
    grade = Column(String(20))  # Grade 1, Grade 2, Grade 3 (color-coded priority)

    # Contact & Company
    contact_name = Column(String(255))  # text0 - Contact name
    company_name = Column(String(255))  # text_mksp2w2b - Company name
    email = Column(String(255))
    phone = Column(String(50))

    # Financial
    sale_price = Column(Numeric(12, 2))  # numeric_mkt4jyp4 - Sale price in GBP
    close_probability = Column(Integer)  # numeric_mkt8frbn - Close probability %

    # Owner/Estimator
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner_name = Column(String(255))  # Estimator name

    # Survey
    survey_required = Column(Boolean, default=False)  # color_mktk467z - Is survey required

    # Quote info
    quote_template = Column(String(50))  # West Park, Client
    quotes_done = Column(Integer)  # No. of quotes done
    revisions_made = Column(Boolean, default=False)
    num_revisions = Column(Integer)

    # Dates
    next_interaction = Column(Date)  # date - Next interaction
    return_date = Column(Date)  # date_mkt86yvg
    quote_sent_date = Column(Date)  # date_mkt85aje
    decision_date = Column(Date)  # date_mkt85f7z
    close_date = Column(Date)  # deal_close_date
    start_date = Column(Date)  # Start from timeline
    end_date = Column(Date)  # End from timeline

    # Location
    location_address = Column(Text)
    location_lat = Column(Numeric(10, 7))
    location_lng = Column(Numeric(10, 7))

    # Files & Links
    files = Column(JSON, default=list)
    link = Column(Text)

    # Supplier quotes
    supplier_quotes = Column(JSON, default=list)  # dropdown_mktkt0j7 - SIG, FORZA, SAS, FUSION

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    workspace = relationship("Workspace", back_populates="opportunities")
    owner = relationship("User", backref="opportunities")


class Checklist(Base):
    __tablename__ = "checklists"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=True, index=True)
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

    workspace = relationship("Workspace", back_populates="checklists")
    owner = relationship("User", back_populates="checklists")
    deal = relationship("Deal", back_populates="checklists")
