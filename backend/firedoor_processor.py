"""
Fire Door Quoting Processor
Handles extraction and mapping of fire door survey data to rate card codes.
"""

import os
import re
import csv
import json
import logging
import pdfplumber
import httpx
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font
try:
    from anthropic import Anthropic
    import anthropic
    ANTHROPIC_SDK_AVAILABLE = True
except Exception as e:
    ANTHROPIC_SDK_AVAILABLE = False
    anthropic = None
    Anthropic = None
    
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Log versions for debugging
logger = logging.getLogger(__name__)

# Import database dependencies (after logger is defined)
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from database import get_db
    from models import RateCardItem
    DATABASE_AVAILABLE = True
except Exception as e:
    logger.warning(f"Database import failed: {e}. Will use CSV fallback.")
    DATABASE_AVAILABLE = False
    get_db = None
    RateCardItem = None
if ANTHROPIC_SDK_AVAILABLE and anthropic:
    logger.info(f"Anthropic SDK version: {anthropic.__version__}")
logger.info(f"httpx version: {httpx.__version__}")

# Lazy initialization of Anthropic client
_anthropic_client = None
_use_raw_http = False

def call_anthropic_api(prompt: str, max_tokens: int = 4096) -> str:
    """
    Call Anthropic API directly via HTTP (fallback when SDK fails).
    
    Args:
        prompt: The prompt to send
        max_tokens: Maximum tokens in response
        
    Returns:
        The text response from Claude
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    
    logger.info("Using raw HTTP API call to Anthropic (SDK unavailable or failed)")
    
    response = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        },
        json={
            "model": "claude-sonnet-4-20250514",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}]
        },
        timeout=60.0
    )
    response.raise_for_status()
    result = response.json()
    return result["content"][0]["text"]

def get_anthropic_client():
    """Get or create Anthropic client (lazy initialization with fallback to raw HTTP)."""
    global _anthropic_client, _use_raw_http
    
    if _use_raw_http:
        return None  # Signal to use raw HTTP
    
    if _anthropic_client is None:
        if not ANTHROPIC_SDK_AVAILABLE:
            logger.warning("Anthropic SDK not available, using raw HTTP API")
            _use_raw_http = True
            return None
        
        try:
            logger.info("Attempting to initialize Anthropic SDK client")
            _anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            logger.info("Anthropic SDK client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic SDK: {str(e)}")
            logger.info("Falling back to raw HTTP API")
            _use_raw_http = True
            return None
    
    return _anthropic_client

# Load ART code mapping
ART_MAPPING = {}
SCRIPT_DIR = Path(__file__).parent
MAPPING_CSV_PATH = SCRIPT_DIR / "reference_files" / "BMTrada_ART_Codes_RateCard_Mapping.csv"

def load_art_mapping_from_db():
    """
    Load ART code to rate card mapping from database.
    Returns True if successful, False if database is empty or unavailable.
    """
    global ART_MAPPING
    
    if not DATABASE_AVAILABLE:
        return False
    
    try:
        db = next(get_db())
        items = db.query(RateCardItem).all()
        
        if not items:
            logger.info("Rate card database is empty. Will load from CSV.")
            return False
        
        for item in items:
            ART_MAPPING[item.art_code] = {
                'description': item.description,
                'rate_card_code': item.rate_card_code,
                'unit_price': item.unit_price,
                'notes': f"Last updated: {item.updated_at}" if item.updated_at else ""
            }
        
        logger.info(f"Loaded {len(items)} rate card items from database")
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"Failed to load from database: {e}. Will fallback to CSV.")
        return False


def load_art_mapping_from_csv():
    """Load ART code to rate card mapping from CSV (fallback)."""
    global ART_MAPPING
    with open(MAPPING_CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            art_code = row['ART Code']
            ART_MAPPING[art_code] = {
                'description': row['Description'],
                'rate_card_code': row['WestPark Rate Card Code'],
                'unit_price': None,  # CSV doesn't have prices
                'notes': row['Notes']
            }
    logger.info(f"Loaded {len(ART_MAPPING)} rate card items from CSV")


def load_art_mapping():
    """
    Load ART code mapping. Try database first, fallback to CSV.
    Database contains user-editable prices. CSV is the default reference.
    """
    global ART_MAPPING
    
    # Try database first
    if load_art_mapping_from_db():
        logger.info("Using rate card from database (with user-edited prices)")
        return
    
    # Fallback to CSV
    logger.info("Using rate card from CSV (default prices)")
    load_art_mapping_from_csv()


# Load mapping on module import
load_art_mapping()


def detect_format(file_path: str, filename: str) -> str:
    """
    Detect survey format type.
    
    Returns:
        'TYPE_1' - PDF with FireDNA/RiskBase/BM TRADA/ART codes
        'TYPE_2' - Excel with door/gaps/seals fault columns
        'UNKNOWN' - Cannot determine format
    """
    ext = Path(filename).suffix.lower()
    
    if ext == '.pdf':
        # Try to read first few pages and look for TYPE_1 indicators
        try:
            with pdfplumber.open(file_path) as pdf:
                first_page_text = pdf.pages[0].extract_text() if len(pdf.pages) > 0 else ""
                second_page_text = pdf.pages[1].extract_text() if len(pdf.pages) > 1 else ""
                combined_text = (first_page_text + " " + second_page_text).lower()
                
                # Check for TYPE_1 indicators
                type1_keywords = ['firedna', 'riskbase', 'bm trada', 'art', 'fire door survey']
                if any(keyword in combined_text for keyword in type1_keywords):
                    return 'TYPE_1'
        except Exception as e:
            print(f"Error detecting PDF format: {e}")
            return 'UNKNOWN'
    
    elif ext in ['.xlsx', '.xls']:
        # Try to read and check for TYPE_2 column structure
        try:
            wb = load_workbook(file_path, read_only=True)
            ws = wb.active
            
            # Get header row (usually row 1)
            headers = [cell.value.lower() if cell.value else "" for cell in ws[1]]
            
            # Check for TYPE_2 indicators (door, gaps, seals, etc.)
            type2_keywords = ['door', 'gap', 'seal', 'fault', 'remedial']
            if any(any(keyword in header for keyword in type2_keywords) for header in headers):
                return 'TYPE_2'
        except Exception as e:
            print(f"Error detecting Excel format: {e}")
            return 'UNKNOWN'
    
    return 'UNKNOWN'


def extract_type1_pdf(file_path: str) -> List[Dict]:
    """
    Extract door data from Type 1 PDF using Claude API.
    
    Returns:
        List of door dictionaries with keys: door_id, location, faults, art_codes
    """
    # Extract full text from PDF
    full_text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n\n"
    
    # Use Claude to extract structured data
    prompt = f"""Extract all fire door data from this survey report. For each door, extract:
1. Door ID/Number
2. Location/Description
3. List of faults found
4. ART codes mentioned (if any)

Return as JSON array with this structure:
[
  {{
    "door_id": "FD-001",
    "location": "Main Entrance",
    "faults": ["Gap too large", "Seal missing"],
    "art_codes": ["ART04", "ART11"]
  }},
  ...
]

Survey text:
{full_text}

Return ONLY the JSON array, no other text."""

    client = get_anthropic_client()
    
    # Use SDK if available, otherwise raw HTTP
    if client is not None:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = response.content[0].text
    else:
        response_text = call_anthropic_api(prompt, max_tokens=4096)
    
    # Parse JSON response
    try:
        doors = json.loads(response_text)
        return doors
    except json.JSONDecodeError:
        # Try to extract JSON from response
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return []


def map_fault_to_bcode(fault_text: str) -> Optional[str]:
    """
    Map fault description to B-series code based on keywords.
    
    B-series mapping rules:
    B01 - Intumescent + smoke seals
    B02 - Intumescent only
    B03 - Door closer
    B04 - Hinges
    B05 - Latch/handles
    B06 - Frame fire stopping / architrave
    B07 - Fire door signage
    B10 - Adjust/re-hang door
    B11 - Hardwood re-lip
    B12 - Timber insert for voids
    """
    fault_lower = fault_text.lower()
    
    # B01 - Smoke seals (with intumescent)
    if any(keyword in fault_lower for keyword in ['smoke seal', 'smoke strip', 'perimeter seal']) and 'intumescent' in fault_lower:
        return 'B01'
    
    # B02 - Intumescent only
    if 'intumescent' in fault_lower and 'smoke' not in fault_lower:
        return 'B02'
    
    # B03 - Door closer
    if any(keyword in fault_lower for keyword in ['closer', 'overhead closer', 'door closer']):
        return 'B03'
    
    # B04 - Hinges
    if any(keyword in fault_lower for keyword in ['hinge', 'dropped', 'drop']):
        return 'B04'
    
    # B05 - Latch/handles
    if any(keyword in fault_lower for keyword in ['latch', 'handle', 'lock', 'keep']):
        return 'B05'
    
    # B06 - Frame/architrave
    if any(keyword in fault_lower for keyword in ['frame', 'architrave', 'fire stop', 'firestop', 'gap to wall']):
        return 'B06'
    
    # B07 - Signage
    if any(keyword in fault_lower for keyword in ['sign', 'signage', 'label']):
        return 'B07'
    
    # B10 - Re-hang/adjust
    if any(keyword in fault_lower for keyword in ['adjust', 're-hang', 'rehang', 'alignment', 'warped', 'twisted', 'gap too']):
        return 'B10'
    
    # B11 - Re-lip
    if any(keyword in fault_lower for keyword in ['lipping', 'lip', 'edge damage']):
        return 'B11'
    
    # B12 - Timber insert
    if any(keyword in fault_lower for keyword in ['void', 'hole', 'insert', 'recessed']):
        return 'B12'
    
    return None


def extract_type2_excel(file_path: str) -> List[Dict]:
    """
    Extract door data from Type 2 Excel file and map faults to B-codes.
    
    Returns:
        List of door dictionaries with keys: door_id, location, faults, b_codes
    """
    wb = load_workbook(file_path)
    all_doors = []
    
    # Process all sheets (some surveys have Floor 1, Floor 2, etc.)
    for sheet in wb.worksheets:
        # Find header row (usually row 1 or 2)
        header_row = 1
        headers = [cell.value.lower() if cell.value else "" for cell in sheet[1]]
        
        # If row 1 doesn't look like headers, try row 2
        if not any('door' in h or 'gap' in h or 'seal' in h for h in headers):
            header_row = 2
            headers = [cell.value.lower() if cell.value else "" for cell in sheet[2]]
        
        # Find column indices
        door_col = next((i for i, h in enumerate(headers) if 'door' in h and ('no' in h or 'number' in h or 'ref' in h)), None)
        
        # Fault columns: any column with door-related keywords, excluding the door number column
        fault_cols = [i for i, h in enumerate(headers) if i != door_col and any(
            keyword in h for keyword in ['gap', 'seal', 'frame', 'hinge', 'lock', 'glass', 'strip', 'closer', 'ironmongery', 'wall']
        )]
        
        # If no specific fault columns found, use all columns except first 3 (usually ID/ref columns)
        if not fault_cols:
            fault_cols = list(range(3, len(headers)))
        
        # Extract doors
        for row_idx, row in enumerate(sheet.iter_rows(min_row=header_row+1, values_only=True), start=header_row+1):
            if not row or not any(row):  # Skip empty rows
                continue
                
            door_id = row[door_col] if door_col is not None and door_col < len(row) else f"{sheet.title}-Door-{row_idx}"
            
            # Collect faults from relevant columns
            faults = []
            b_codes = []
            
            for col_idx in fault_cols:
                if col_idx < len(row) and row[col_idx]:
                    fault_text = str(row[col_idx]).strip()
                    # Skip "OK", "None", "N/A", "NO", empty values
                    if fault_text and fault_text.upper() not in ['OK', 'NONE', 'N/A', 'NO', 'YES', '-']:
                        faults.append(fault_text)
                        # Map to B-code
                        b_code = map_fault_to_bcode(fault_text)
                        if b_code:
                            b_codes.append(b_code)
            
            if faults:  # Only add doors with actual faults
                all_doors.append({
                    'door_id': f"{sheet.title}-{door_id}",
                    'location': sheet.title,  # Use sheet name as location
                    'faults': faults,
                    'b_codes': list(set(b_codes))  # Remove duplicates
                })
    
    return all_doors


def map_art_to_rate_card(art_codes: List[str]) -> List[str]:
    """Map ART codes to WestPark rate card codes using the CSV mapping."""
    rate_card_codes = []
    for art_code in art_codes:
        if art_code in ART_MAPPING:
            rc_code = ART_MAPPING[art_code]['rate_card_code']
            if rc_code and rc_code.strip() and rc_code not in ['FLAG FOR MANUAL REVIEW', 'NO EQUIVALENT']:
                # Handle multi-code entries like "B01 / B02"
                codes = [c.strip() for c in rc_code.split('/')]
                rate_card_codes.extend(codes)
    
    return list(set(rate_card_codes))  # Remove duplicates


def populate_excel_template(doors: List[Dict], client_name: str, template_path: str, output_path: str):
    """
    Populate Excel template with door data and color code rows.
    
    Writes to "Door Schedule" sheet with proper column mapping:
    - Column A: Door ID
    - Column B: Location
    - Column C-I: Door details (type, rating, config, size, finish, seals, closer)
    - Column P: Primary rate card code (for Quote Sheet formulas)
    
    Args:
        doors: List of door dictionaries
        client_name: Client name for the header
        template_path: Path to template Excel file
        output_path: Path to save output file
    """
    import logging
    from pathlib import Path
    
    logger = logging.getLogger(__name__)
    
    # Validate template exists
    template_file = Path(template_path)
    if not template_file.exists():
        error_msg = f"Template file not found: {template_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    logger.info(f"Loading template from: {template_path}")
    logger.info(f"Output will be saved to: {output_path}")
    logger.info(f"Processing {len(doors)} doors for client: {client_name}")
    
    try:
        wb = load_workbook(template_path)
        logger.info(f"Template loaded successfully. Sheets: {wb.sheetnames}")
    except Exception as e:
        error_msg = f"Failed to load template workbook: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    
    # Update Rate Card sheet with database prices
    if DATABASE_AVAILABLE:
        try:
            db = next(get_db())
            rate_items = db.query(RateCardItem).all()
            
            if rate_items:
                # Create mapping: rate_card_code -> unit_price
                price_map = {}
                for item in rate_items:
                    # One ART code can map to multiple rate card codes (e.g., "B01 / B02")
                    codes = [c.strip() for c in item.rate_card_code.split('/')]
                    for code in codes:
                        if code and code not in price_map:
                            price_map[code] = item.unit_price
                
                logger.info(f"Loaded {len(price_map)} rate card prices from database")
                
                # Update Rate Card sheet
                if "Rate Card" in wb.sheetnames:
                    rate_card_sheet = wb["Rate Card"]
                    updated_count = 0
                    
                    # Scan rows 6-39 (where rate card codes live)
                    for row_num in range(6, 40):
                        code_cell = rate_card_sheet.cell(row=row_num, column=1)  # Column A
                        code = code_cell.value
                        
                        if code and str(code) in price_map:
                            price_str = price_map[str(code)]
                            # Parse price (e.g., "£45.00" -> 45.00)
                            try:
                                price_value = float(price_str.replace('£', '').replace(',', '').strip())
                                # Write to column H (TOTAL RATE)
                                total_cell = rate_card_sheet.cell(row=row_num, column=8)
                                total_cell.value = price_value
                                updated_count += 1
                                logger.info(f"Updated {code} price to £{price_value}")
                            except (ValueError, AttributeError) as e:
                                logger.warning(f"Could not parse price for {code}: {price_str}")
                    
                    logger.info(f"Updated {updated_count} rate card prices in Excel template")
                else:
                    logger.warning("Rate Card sheet not found in template")
            else:
                logger.info("No rate card items in database - using template defaults")
            
            db.close()
        except Exception as e:
            logger.warning(f"Failed to load database prices: {e}. Using template defaults.")
    else:
        logger.info("Database not available - using template default prices")
    
    # Update client name in Quote Sheet
    try:
        quote_sheet = wb["Quote Sheet"]
        quote_sheet['B4'] = client_name  # B4 is the Client field
        logger.info(f"Updated Quote Sheet with client name: {client_name}")
    except KeyError as e:
        error_msg = f"Quote Sheet not found in template. Available sheets: {wb.sheetnames}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    
    # Get Door Schedule sheet for populating door data
    try:
        ws = wb["Door Schedule"]
        logger.info("Door Schedule sheet found")
    except KeyError as e:
        error_msg = f"Door Schedule sheet not found in template. Available sheets: {wb.sheetnames}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    
    # Define color fills
    green_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")  # Light green
    yellow_fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")  # Light yellow
    red_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")  # Light red
    
    # Data starts at row 4 (row 3 is headers)
    start_row = 4
    
    # Clear existing data (rows 4-100)
    for row_num in range(4, 100):
        for col in range(1, 17):  # Columns A-P
            ws.cell(row=row_num, column=col).value = None
            ws.cell(row=row_num, column=col).fill = PatternFill()  # Clear fill
    
    # Populate door data
    for idx, door in enumerate(doors):
        row_num = start_row + idx
        
        # Get codes (either b_codes from Type 2 or map art_codes from Type 1)
        codes = door.get('b_codes', [])
        if not codes and 'art_codes' in door:
            codes = map_art_to_rate_card(door['art_codes'])
        
        # Primary code (first code if multiple, or "MANUAL REVIEW" if none)
        primary_code = codes[0] if codes else ''
        all_codes_str = ', '.join(codes) if codes else 'MANUAL REVIEW'
        
        # Column mapping based on Door Schedule template:
        # A=DOOR ID, B=LOCATION, C=DOOR TYPE, D=CURRENT RATING, E=LEAF CONFIG,
        # F=LEAF SIZE, G=FINISH, H=SEALS, I=CLOSER, ...P=PRIMARY CODE
        ws[f'A{row_num}'] = door['door_id']
        ws[f'B{row_num}'] = door.get('location', '')
        ws[f'C{row_num}'] = 'From Survey'  # Door type placeholder
        ws[f'D{row_num}'] = 'Unknown'  # Rating placeholder
        ws[f'E{row_num}'] = 'Single Leaf'  # Config placeholder
        ws[f'F{row_num}'] = 'Unknown'  # Size placeholder
        ws[f'G{row_num}'] = 'Paint'  # Finish placeholder
        ws[f'H{row_num}'] = 'To Check'  # Seals placeholder
        ws[f'I{row_num}'] = 'To Check'  # Closer placeholder
        
        # Column J-O can be used for fault details
        faults_str = '; '.join(door.get('faults', []))
        ws[f'J{row_num}'] = faults_str[:250]  # Truncate if too long
        
        # Column P: Primary rate card code (used by Quote Sheet formulas)
        ws[f'P{row_num}'] = primary_code
        
        # Column Q: All codes for reference
        ws[f'Q{row_num}'] = all_codes_str
        
        # Color code based on number of codes
        color_fill = None
        if not codes:
            color_fill = red_fill  # Red - needs manual review
        elif len(codes) == 1:
            color_fill = green_fill  # Green - single clear code
        else:
            color_fill = yellow_fill  # Yellow - multiple codes
        
        # Apply color to all columns A-Q
        if color_fill:
            for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'P', 'Q']:
                ws[f'{col}{row_num}'].fill = color_fill
    
    # Save workbook
    try:
        logger.info(f"Saving workbook to: {output_path}")
        wb.save(output_path)
        logger.info("Workbook saved successfully")
    except Exception as e:
        error_msg = f"Failed to save workbook: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    
    # Verify file was created
    output_file = Path(output_path)
    if not output_file.exists():
        error_msg = f"Output file was not created at: {output_path}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    
    file_size = output_file.stat().st_size
    logger.info(f"Output file created successfully. Size: {file_size} bytes")
    
    return output_path
