"""
Fire Door Quoting Processor
Handles extraction and mapping of fire door survey data to rate card codes.
"""

import os
import re
import csv
import pdfplumber
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font
from anthropic import Anthropic
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Initialize Anthropic client
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Load ART code mapping
ART_MAPPING = {}
MAPPING_CSV_PATH = "/root/clawd/projects/westpark-surveys/firedoor-data/Fire Door Costing/BMTrada_ART_Codes_RateCard_Mapping.csv"

def load_art_mapping():
    """Load ART code to rate card mapping from CSV."""
    global ART_MAPPING
    with open(MAPPING_CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            art_code = row['ART Code']
            ART_MAPPING[art_code] = {
                'description': row['Description'],
                'rate_card_code': row['WestPark Rate Card Code'],
                'notes': row['Notes']
            }

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

    response = anthropic_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Parse JSON response
    import json
    try:
        doors = json.loads(response.content[0].text)
        return doors
    except json.JSONDecodeError:
        # Try to extract JSON from response
        json_match = re.search(r'\[.*\]', response.content[0].text, re.DOTALL)
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
    ws = wb.active
    
    # Find header row and relevant columns
    headers = [cell.value.lower() if cell.value else "" for cell in ws[1]]
    
    # Find column indices
    door_col = next((i for i, h in enumerate(headers) if 'door' in h and ('id' in h or 'ref' in h or 'no' in h)), None)
    location_col = next((i for i, h in enumerate(headers) if 'location' in h or 'description' in h), None)
    fault_cols = [i for i, h in enumerate(headers) if any(keyword in h for keyword in ['gap', 'seal', 'fault', 'defect', 'remedial'])]
    
    doors = []
    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        door_id = row[door_col] if door_col is not None else f"Door {row_idx}"
        location = row[location_col] if location_col is not None else ""
        
        # Collect faults from relevant columns
        faults = []
        b_codes = []
        
        for col_idx in fault_cols:
            if col_idx < len(row) and row[col_idx]:
                fault_text = str(row[col_idx])
                if fault_text.strip():
                    faults.append(fault_text)
                    # Map to B-code
                    b_code = map_fault_to_bcode(fault_text)
                    if b_code:
                        b_codes.append(b_code)
        
        if faults:  # Only add doors with faults
            doors.append({
                'door_id': str(door_id),
                'location': str(location),
                'faults': faults,
                'b_codes': list(set(b_codes))  # Remove duplicates
            })
    
    return doors


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
    
    Args:
        doors: List of door dictionaries
        client_name: Client name for the header
        template_path: Path to template Excel file
        output_path: Path to save output file
    """
    wb = load_workbook(template_path)
    ws = wb.active
    
    # Update client name in template (assuming it's in cell B2 or similar)
    # TODO: Find exact cell location in template
    ws['B2'] = client_name
    
    # Define color fills
    green_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")  # Light green
    yellow_fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")  # Light yellow
    red_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")  # Light red
    
    # Find data start row (usually row 5 or 6 after header rows)
    start_row = 6
    
    # Populate door data
    for idx, door in enumerate(doors):
        row_num = start_row + idx
        
        # Column mapping (adjust based on actual template structure)
        # Assuming: A=Door ID, B=Location, C=Faults, D=Rate Card Codes
        ws[f'A{row_num}'] = door['door_id']
        ws[f'B{row_num}'] = door.get('location', '')
        ws[f'C{row_num}'] = ', '.join(door.get('faults', []))
        
        # Get codes (either b_codes from Type 2 or map art_codes from Type 1)
        codes = door.get('b_codes', [])
        if not codes and 'art_codes' in door:
            codes = map_art_to_rate_card(door['art_codes'])
        
        ws[f'D{row_num}'] = ', '.join(codes) if codes else 'MANUAL REVIEW'
        
        # Color code based on number of codes
        if not codes:
            # Red - needs manual review
            for col in ['A', 'B', 'C', 'D']:
                ws[f'{col}{row_num}'].fill = red_fill
        elif len(codes) == 1:
            # Green - single clear code
            for col in ['A', 'B', 'C', 'D']:
                ws[f'{col}{row_num}'].fill = green_fill
        else:
            # Yellow - multiple codes (needs verification)
            for col in ['A', 'B', 'C', 'D']:
                ws[f'{col}{row_num}'].fill = yellow_fill
    
    wb.save(output_path)
    return output_path
