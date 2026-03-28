# Fire Door Quoting - Business Logic Rules

**Version:** 1.1  
**Last Updated:** 2026-03-28  
**Owner:** Westpark Fire Safety

## Overview

This document defines the complete extraction, mapping, and output rules for the Fire Door Quoting system. All changes to business logic MUST be documented here.

---

## 1. Survey Types

### Type 1 (PDF Format)
- **Source:** FireDNA, RiskBase, BM TRADA surveys
- **Format:** PDF text files
- **Key Feature:** Contains ART (Asset Remedial Tracking) codes
- **Fire Strategy:** Always included (complete survey)
- **Option B Pricing:** ALWAYS available (not PENDING)

### Type 2 (Excel Format)
- **Source:** Manual Excel surveys
- **Format:** `.xlsx` or `.xls`
- **Key Feature:** Fault text descriptions (no ART codes)
- **Fire Strategy:** NOT included
- **Option B Pricing:** PENDING (requires fire strategy drawings)

---

## 2. Door ID Rules

### Type 1 (PDF)
- **Rule:** Door IDs MUST include floor suffix
- **Format:** `{ID}-{FLOOR}` (e.g., `A01-L2`, `A02-L3`)
- **Reason:** Multiple floors may have same door numbers
- **Example:**
  ```
  Floor 2: A01-L2, A02-L2, A03-L2
  Floor 3: A01-L3, A02-L3, A03-L3
  ```

### Type 2 (Excel)
- **Rule:** Use door IDs exactly as they appear in the survey
- **Format:** Typically numeric (e.g., `1`, `2`, `3`) or alphanumeric
- **No suffix required** (Excel surveys typically use unique IDs)

---

## 3. Fire Rating Extraction

### Type 1 (PDF)
- **Required Field:** Fire rating is MANDATORY for every door
- **Valid Values:**
  - FD30 (30-minute fire door)
  - FD30S (30-minute with smoke seals)
  - FD60 (60-minute fire door)
  - FD90 (90-minute fire door)
  - FD120 (120-minute fire door)
  - Nominal (non-fire-rated door)
  - Unknown (ONLY if truly missing from source)
  
- **Extraction Source:** 
  - Look for explicit "Fire Rating:" field
  - Parse from door description
  - Check compliance status text
  
- **Validation:** If ALL doors show "Unknown", extraction is failing

### Type 2 (Excel)
- **Fire Rating:** May be in separate column or embedded in description
- **Fallback:** If not present, mark as "Unknown"

---

## 4. ART Code → B-Code Mapping

### Type 1 (PDF with ART Codes)
**Source:** `BMTrada_ART_Codes_RateCard_Mapping.csv`

**Mapping Logic:**
1. Extract ART codes from PDF (e.g., ART01, ART02)
2. Map to WestPark B-codes via CSV lookup
3. If ART code not in CSV, log warning and skip

**Complete ART → B-Code Mappings (from BMTrada_ART_Codes_RateCard_Mapping.csv):**
- **ART01** → B11 (Hardwood re-lip — min density 640kg/m3)
- **ART02** → B12 (Hardwood timber insert per void/hole)
- **ART03** → B06 (Fire-stop frame-to-wall gap — intumescent mastic / ablative batt)
- **ART04** → B01 / B10 (B01 if gap issue requires seals; B10 if alignment issue)
- **ART05** → B03 (Replace overhead door closer — CE-marked BS EN 1154)
- **ART06** → B10 (Adjust / re-hang door leaf)
- **ART07** → B10 (Adjust / re-hang door leaf — address moisture cause first)
- **ART08** → B04 (Replace / fix hinge set — BS EN 1935 Grade 11)
- **ART09** → B10 (Adjust / re-hang door leaf)
- **ART10** → B05 (Replace lever handles / latch / lock — CE-marked ironmongery)
- **ART11** → B01 / B02 (B01 if smoke seals required; B02 if intumescent only)
- **ART12** → B05 (Replace lever handles / latch set — CE-marked ironmongery)
- **ART13** → B04 (Replace / fix hinge set — check screws vs full hinge replacement)
- **ART14** → **NO EQUIVALENT** — Damaged glazing. Flag door for manual review (see Section 4.1)
- **ART15** → B11 (Same repair as ART01 — hardwood re-lip)
- **ART16** → B06 (Fire-stop frame-to-wall gap)
- **ART17** → Replacement required (see Section 6 - Option B)
- **ART18** → Replacement required (see Section 6 - Option B)
- **ART19** → B07 (Add / replace fire door signage — 2 signs per leaf)
- **ART20** → Replacement required (see Section 6 - Option B)
- **ART21** → B06 (Fire-stop / refit architrave)
- **ART22** → B01 (Supply & fit intumescent + smoke seals)
- **ART23** → **FLAG FOR MANUAL REVIEW** — No applicable repair technique (see Section 4.2)
- **ART24** → Reserved / not in published list

### 4.1 Special Case: ART14 (Damaged Glazing)
**Rule:** ART14 has no B-code equivalent in the current rate card.

**Action:**
1. Do NOT auto-price this door in Option A
2. Flag the door in Notes column: "ART14 - Damaged glazing - Manual review required"
3. Mark Opt A as "NO" (manual pricing needed)

**Reason:** Gap in rate card — may require new B13 line item for glazing repairs.

### 4.2 Special Case: ART23 (No Applicable Repair Technique)
**Rule:** ART23 means damage is present but no accepted repair technique exists. Door likely needs replacement.

**Action:**
1. Do NOT auto-price this door in Option A or Option B
2. Flag the door in Notes column: "ART23 - No repair technique - Manual review required"
3. Mark both Opt A and Opt B as "NO"
4. Recommend manual inspection and quote

### 4.3 Multiple B-Codes Per Door (Type 1)
**Rule:** When a Type 1 door has multiple ART codes mapping to different B-codes:

**Priority for Column P (Primary B-Code):**
Use this priority order to select the single B-code for Quote Sheet formulas:
1. **B01** (seals) — highest priority
2. **B03** (closer)
3. **B04** (hinges)
4. **B10** (adjust/rehang)
5. **B05** (latch/handles)
6. **B02** (intumescent only)
7. **B06** (fire-stopping)
8. **B07** (signage)
9. **B11** (lipping)
10. **B12** (void infill)

**Column K (Action Description):**
List ALL applicable B-codes as a comma-separated list.

**Example:**
- Door has ART11 (B01/B02), ART05 (B03), ART08 (B04)
- Column P (Primary): B01 (highest priority)
- Column K: "B01, B03, B04"

### Type 2 (Excel with Fault Text)
**Source:** `map_fault_to_bcode()` function

**Mapping Rules:**
1. **Seals (B01):**
   - "seal" + ("coming away" OR "worn" OR "damaged" OR "missing" OR "not fitted")
   - Examples: "seals worn", "smoke seal damaged", "seals not fitted"

2. **Intumescent Only (B02):**
   - "intumescent" + NOT "smoke"
   - Example: "intumescent strip damaged"

3. **Self-Closing (B03):**
   - "closing" + NOT ("not closing" OR "not catching")
   - "closer" + any variation
   - Example: "door not closing properly"

4. **Hinges (B04):**
   - "hinge" OR "hinges"
   - Example: "hinges loose"

5. **Latch/Handles (B05):**
   - "latch" OR "handle" OR "lock"
   - Example: "latch not catching"

6. **Fire-Stopping (B06):**
   - "fire stop" OR "fire-stop" OR "firestopping"
   - Example: "inadequate fire-stopping"

7. **Signage (B07):**
   - "sign" OR "signage"
   - Example: "fire door sign missing"

8. **Hold-Open Devices (B08):**
   - "perco" OR "hold open" OR "hold-open"
   - Example: "Perco chains installed"

9. **Door Lipping (B11):**
   - "lipping" OR "re-lip"
   - Example: "door requires re-lipping"

10. **Adjust/Rehang (B10):**
    - "catching" OR "not catching" OR "adjust" OR "rehang"
    - Example: "door catching on floor"

11. **Void Infill (B12):**
    - "void" OR "hollow"
    - Example: "door leaf void requires infill"

**Priority Order (when multiple codes match):**
1. B01 (seals) — highest priority
2. B03 (closer)
3. B04 (hinges)
4. B10 (adjust/rehang)
5. Other codes

---

## 5. Door Schedule Column Structure (Updated 2026-03-29 - ISSUE 1 FIX)

### Critical Column Definitions

The Door Schedule uses the following column structure:

| Column | Name | Description | Example |
|--------|------|-------------|---------|
| A | DOOR ID | Unique door identifier | A01-L2, A02-L3 |
| B | LOCATION | Physical location | Ground Floor Lobby |
| C | DOOR TYPE | Type from survey | From Survey |
| D | CURRENT RATING | Fire rating | FD30S, FD60S, Unknown |
| E | LEAF CONFIG | Single or Double | Single Leaf, Double Leaf |
| F-M | Various | Size, Finish, Seals, etc. | Paint, To Check |
| N | OPT A REMEDIAL? | YES/NO/COMPLIANT | YES (needs remedial work) |
| O | OPT B REPLACE? | YES/NO/PENDING | YES (needs replacement) |
| **P** | **OPT A BASE ITEM** | **Primary B-code** | **B01, B03, B10** |
| **Q** | **QTY** | **Integer: 1 or 0** | **1 (non-compliant), 0 (compliant)** |
| **R** | **E/O OVERSIZE** | **Extra Over flag** | **NO, YES** |
| **S** | **E/O HARDWOOD** | **Extra Over flag** | **NO, YES** |
| **T** | **E/O EXTERNAL** | **Extra Over flag** | **NO, YES** |
| **U** | **E/O VISION** | **Extra Over flag** | **NO, YES** |
| **V** | **NOTES/FLAGS** | **ART codes, warnings** | **ARTs: ART01, ART03** |
| **W** | **ALL B CODES** | **Comma-separated B-codes** | **B10, B01, B06, B12, B07** |
| **X** | **OPT B REPLACEMENT CODE** | **A-series code for Option B** | **A01, A05, A09** |

### ISSUE 1 FIX (2026-03-29): Column Structure Correction

**Problem:** The 9-fixes implementation (2026-03-28) inadvertently overwrote columns R/S:
- OLD (INCORRECT): Columns R/S = ALL B CODES / OPT B REPLACEMENT CODE
- This overwrote the existing E/O (Extra Over) columns which are CRITICAL for pricing

**Solution:** Columns restored to preserve E/O pricing data:
- **Columns R-U**: E/O flags (OVERSIZE/HARDWOOD/EXTERNAL/VISION) - RESTORED to original position
- **Column V**: NOTES/FLAGS - RESTORED to original position
- **Column W**: ALL B CODES (comma-separated) - MOVED from R
- **Column X**: OPT B REPLACEMENT CODE (A-series) - MOVED from S

**Impact:** 
- E/O columns are now preserved for Extra Over pricing calculations
- Quote Sheet counting logic updated to read from columns W/X instead of R/S
- All formulas and Python code updated to reflect new column indices (W=23, X=24)

### Column Q: QTY (Quantity)

**Purpose:** Integer count for each door (1 or 0)

**Rules:**
- **Non-compliant doors:** QTY = 1 (Opt A = YES or Opt B = YES)
- **Compliant doors:** QTY = 0 (Opt A = COMPLIANT)
- **Never blank, never text, always integer**

**Previous Issue (Fixed 2026-03-28):**
- Column Q was storing comma-separated B-codes
- This made counting impossible
- **Fix:** Moved B-code list to column R, made Q an integer

### Column R: ALL B CODES (Comma-Separated List)

**Purpose:** Complete list of ALL B-series codes required for remedial work on this door

**Format:** Comma-separated, no quotes
- Example: `B10, B01, B06, B12, B07`
- Example: `B01, B03`
- Example: `` (blank for compliant doors)

**Used By:** Quote Sheet Option A wildcard COUNTIF (see Section 6)

**Rules:**
- **Multi-code doors:** List ALL codes (e.g., door needs seals + signage + re-hang)
- **Single-code doors:** Single code (e.g., just B03 closer)
- **Compliant doors:** Blank
- **Order:** Does not matter (wildcard search)

### Column S: OPT B REPLACEMENT CODE (A-Series)

**Purpose:** A-series replacement code for Option B (full replacement)

**Assignment Logic:**
For **ALL non-compliant doors** (Opt A = YES OR Opt B = YES):
- Map fire rating + leaf config → A-series code
- FD30/FD30S single ≤2040mm → A05
- FD60/FD60S single ≤2040mm → A09
- FD30 double ≤2040mm → A08
- NOMINAL single → A05 (default)
- NOMINAL double → A08 (default)

**Used By:** Quote Sheet Option B COUNTIF (see Section 7)

**Rules:**
- **ALL non-compliant doors get an A-code** (not just mandatory replacements)
- Mandatory replacements (ART17/18/20) use specific codes
- Remediable doors (Opt A = YES) ALSO get A-codes for Option B
- Compliant doors: Blank

**Critical Understanding (Fixed 2026-03-28):**
Option B = replace **ALL 33 non-compliant doors**, not just 2 mandatory replacements.

---

## 6. Quote Sheet Counting Logic (Wildcard COUNTIF)

### Option A (B-Series) - Wildcard Matching

**Problem Solved (2026-03-28):**
- B07 (signage), B10 (re-hang), B11 (lipping) were showing QTY = 0
- Root cause: Primary code (column P) only showed ONE code per door
- Doors with multiple codes were under-counted

**Solution: Wildcard COUNTIF Against Column R (ALL B CODES)**

For each B-series line item in Quote Sheet, count doors where that B-code appears **anywhere** in the ALL B CODES column (R).

**Python Logic:**
```python
# For B07 (signage) at Quote Sheet row 17
b07_count = 0
for row in door_schedule_rows:
    all_b_codes = door_schedule[row]['ALL B CODES']  # Column R
    if 'B07' in str(all_b_codes):  # Wildcard/substring match
        b07_count += 1

quote_sheet[17]['QTY'] = b07_count  # Column C
```

**Excel Formula Equivalent:**
```excel
=COUNTIF(DoorSchedule!R:R, "*B07*")
```

**Result:**
- B07: Counts ALL doors with signage failures (not just doors where B07 is primary)
- B10: Counts ALL doors needing re-hang
- B11: Counts ALL doors needing lipping

### Option B (A-Series) - Exact Match on Column S

**For each A-series line item in Quote Sheet, count doors where OPT B REPLACEMENT CODE (column S) exactly matches that A-code.**

**Python Logic:**
```python
# For A05 (FD30S single ≤2040mm) at Quote Sheet row 30
a05_count = 0
for row in door_schedule_rows:
    opt_b_code = door_schedule[row]['OPT B REPLACEMENT CODE']  # Column S
    if opt_b_code == 'A05':  # Exact match
        a05_count += 1

quote_sheet[30]['QTY'] = a05_count  # Column C
```

**Excel Formula Equivalent:**
```excel
=COUNTIF(DoorSchedule!S:S, "A05")
```

**Result:**
- A01: Counts doors assigned A01 (FD30 single ≤2040mm, no smoke)
- A05: Counts doors assigned A05 (FD30S single ≤2040mm, with smoke)
- A09: Counts doors assigned A09 (FD60S single ≤2040mm)

**Expected Total for Option B:** ~33 doors for Alpha Sights (all non-compliant)

---

## 7. Option A (Remedial Works)

### Calculation Logic
1. Count doors with `Opt A = YES` in Door Schedule
2. Group by B-code (Base Item column P + ALL codes column Q)
3. Calculate: `QTY × RATE = TOTAL` for each B-code
4. Write numbers directly (not formulas) to Quote Sheet

### Quote Sheet Structure
- **Rows 11-22:** Individual B-code line items (A.01–A.12)
- **Row 23:** Option A TOTAL (SUM of rows 11-22)
- **Columns:**
  - C: QTY (number)
  - E: RATE (number from Rate Card)
  - F: TOTAL (number = QTY × RATE)

### Quote Sheet Row-to-B-Code Mapping
**CRITICAL:** Each Quote Sheet row must count ONLY doors where that exact B-code appears in column P or Q of Door Schedule.

| Quote Sheet Row | B-Code | Description |
|-----------------|--------|-------------|
| Row 11 (A.01) | B01 | Intumescent + smoke seals |
| Row 12 (A.02) | B02 | Intumescent only |
| Row 13 (A.03) | B03 | Self-closing device |
| Row 14 (A.04) | B04 | Hinge sets |
| Row 15 (A.05) | B05 | Latch/handles |
| Row 16 (A.06) | B06 | Fire-stopping |
| Row 17 (A.07) | B07 | Signage |
| Row 18 (A.08) | B08 | Hold-open device |
| Row 19 (A.09) | B09 | Drop seal |
| Row 20 (A.10) | B10 | Adjust/rehang |
| Row 21 (A.11) | B11 | Hardwood lipping |
| Row 22 (A.12) | B12 | Void infill |

### VALIDATION RULES (Issue #2 Fix)
After writing Quote Sheet quantities, the system MUST:
1. Sum all QTY values from rows 11-22
2. Compare to total doors with OptA=YES in Door Schedule
3. If sum of QTY values does NOT equal or exceed the count of OptA=YES doors, log ERROR
   - Example: If 31 doors have OptA=YES, sum of all B-code counts should be ≥31 (can be higher due to multi-code doors)

### Client Summary
- **C10:** NET COST (Option A total)
- **D10:** OPTION A TOTAL (same as C10)
- **D13:** TOTAL INVESTMENT (sum of all options)

**Critical:** All three cells MUST be numbers (not formulas) to display immediately in Excel.

---

## 6. Option B (Full Replacement)

**CRITICAL UNDERSTANDING (Updated 2026-03-28):**

Option B is NOT just for mandatory replacements (ART17/ART18/ART20). Option B provides a **complete alternative approach** where ALL non-compliant doors are replaced with certified fire doors instead of doing remedial works.

**OLD (INCORRECT) Understanding:**
- ❌ Option B = only the 2-3 doors that MUST be replaced (ART17/ART18/ART20)

**CORRECT Understanding:**
- ✅ Option B = replace ALL 33 non-compliant doors (complete certified door replacement alternative)
- Client choice: Option A (remedial + mandatory replacements) vs Option B (all new certified doors)
- Example: Alpha Sights had 6 compliant + 33 non-compliant doors
  - Option A: £17.5K (remedial works on 33 doors + replace 2 mandatory)
  - Option B: £37K (replace ALL 33 non-compliant with new certified doors)

### Type 1 (PDF) - ALWAYS PRICED
**Rule:** Option B MUST be priced based on fire rating, leaf configuration, AND door height

**CRITICAL: FD30 ≠ FD30S**
- **FD30:** Fire door WITHOUT smoke seals
- **FD30S:** Fire door WITH smoke seals
- The **S suffix** is critical for correct pricing

**A-Series Codes (Replacement Doors) - Full Mapping Table:**

| Code | Fire Rating | Leaf Config | Height Range | Notes |
|------|-------------|-------------|--------------|-------|
| **A01** | FD30 | Single | ≤2040mm | No smoke seals |
| **A02** | FD30 | Single | 2040–2400mm | No smoke seals |
| **A03** | FD30 | Single | 2400–2730mm | No smoke seals |
| **A04** | FD30 | Double | ≤2040mm | No smoke seals |
| **A05** | FD30S | Single | ≤2040mm | WITH smoke seals |
| **A06** | FD30S | Single | 2040–2400mm | WITH smoke seals |
| **A07** | FD30S | Single | 2400–2730mm | WITH smoke seals |
| **A08** | FD30S | Double | ≤2040mm | WITH smoke seals |
| **A09** | FD60S | Single | ≤2040mm | WITH smoke seals |
| **A10** | FD60S | Single | 2040–2400mm | WITH smoke seals |
| **A11** | FD60S | Double | ≤2040mm | WITH smoke seals |
| **A12** | E/O | Any | Any | Hardwood Veneer Finish (uplift) |
| **A13** | E/O | Any | Any | External Grade Spec (uplift) |
| **A14** | E/O | Any | Any | Vision Panel ≤300x600mm |
| **A15** | E/O | Any | Any | Vision Panel >300x600mm |

**Default Mappings (when fire rating is unclear):**
- **Nominal Single** → A05 (defaults to FD30S ≤2040mm)
- **Nominal Double** → A08 (defaults to FD30S double)

**Pricing Logic:**
1. Extract fire rating from survey (FD30, FD30S, FD60S, etc.)
   - **Distinguish FD30 from FD30S** by checking for "S" suffix
2. Extract leaf configuration (Single Leaf / Double Leaf)
3. Extract door height in mm from dimensions
4. Map to corresponding A-series code using height ranges:
   - ≤2040mm → base code
   - 2040–2400mm → next size up
   - 2400–2730mm → largest size
5. Calculate: `QTY × RATE = TOTAL`

**Example 1 (FD30 - no smoke seals):**
- 2 doors: FD30 (no S), double leaf, 2000mm height
- Code: **A04** (FD30 — Double, ≤2040mm)
- Rate: £650 per door (from Rate Card)
- Total: 2 × £650 = £1,300

**Example 2 (FD30S - with smoke seals):**
- 3 doors: FD30S, single leaf, 2100mm height
- Code: **A06** (FD30S — Single, 2040–2400mm)
- Rate: £425 per door (from Rate Card)
- Total: 3 × £425 = £1,275

**Example 3 (FD60S):**
- 1 door: FD60S, single leaf, 2050mm height
- Code: **A10** (FD60S — Single, 2040–2400mm)
- Rate: £575 per door (from Rate Card)
- Total: 1 × £575 = £575

### VALIDATION RULES (Issue #1 Fix)
For replacement doors (ART17, ART18, or ART20):
1. The A-series code MUST be written to Door Schedule column P during extraction
2. If OptB=YES but column P is None or blank, log ERROR — this should NEVER happen
3. Fire rating + leaf config + height → A-series code mapping is MANDATORY
4. If fire rating cannot be extracted, system MUST:
   - Log ERROR showing which door failed extraction
   - Use fallback A05 (FD30S single ≤2040mm) as emergency default
   - Flag the door for manual review in Notes column

**Code Location:**
- During Door Schedule population (rows 4+)
- Check: `if needs_replacement and not a_series_code: log ERROR`

### Type 2 (Excel) - PENDING
**Rule:** Option B shows "PENDING — fire strategy required"

**Reason:** Type 2 surveys lack fire strategy drawings needed to specify replacement doors

**Output:**
- Quote Sheet rows 26–40: All zeros or blank
- Client Summary E11: "PENDING — fire strategy required"
- UI Message: Display warning after download (see Type 2 Survey Notice)

---

## 7. COMPLIANT Logic

**Rule:** Door is COMPLIANT only if it has NO codes AND NO faults

**Logic:**
```python
if not codes and not faults:
    status = "COMPLIANT"
else:
    status = "YES" if needs_remedial else "NO"
```

**Common Mistake:** Using OR instead of AND
- ❌ Wrong: `not codes or not faults` (too permissive)
- ✅ Correct: `not codes and not faults` (strict)

---

## 8. Excel Output Requirements

### Quote Sheet
1. **Header Fields (rows 2–6):**
   - B2: Quote Ref (WP-2026-XXX)
   - B3: Date (DD/MM/YYYY format)
   - B4: Client name
   - B5: Site (blank for Type 2)
   - B6: Building (blank for Type 2)

2. **Line Items (rows 11–22):**
   - Write calculated NUMBERS (not formulas)
   - QTY, RATE, TOTAL all numeric

3. **Option A TOTAL (row 23):**
   - F23 = calculated number (SUM of rows 11–22)

4. **Option B TOTAL (row ~42):**
   - F42 = calculated number (SUM of Option B line items)

**CRITICAL VALIDATION (Issue #3 Fix):**
- TOTAL rows MUST always be written as numbers before saving
- If a TOTAL row is None or 0 when line items exist, treat as a BUG not a valid state
- System MUST validate:
  - If any Option A line items have QTY > 0, then F23 MUST be a number > 0
  - If any Option B line items have QTY > 0, then Option B TOTAL row MUST be a number > 0
  - Never write None to TOTAL rows — write 0 as minimum

### Client Summary
1. **Header Fields:**
   - B3: Client (copied from Quote Sheet B4)
   - B4: Site (copied from Quote Sheet B5)
   - B5: Building (copied from Quote Sheet B6)
   - E6: Date (copied from Quote Sheet B3)
   - B7: Quote Ref (copied from Quote Sheet B2)

2. **Totals (rows 10, 13):**
   - C10: NET COST (Option A total)
   - D10: OPTION A TOTAL
   - E11: OPTION B TOTAL (or "PENDING" for Type 2)
   - D13: TOTAL INVESTMENT

**Critical:** Write numbers, not formulas. Excel cached values issue.

### Door Schedule
1. **Column Mapping:**
   - A: Door ID (with floor suffix for Type 1)
   - B: Location
   - C–I: Door details (type, rating, config, size, finish, seals, closer)
   - N: Opt A (YES/NO/COMPLIANT)
   - O: Opt B (YES/NO)
   - P: Base Item (B-code for Quote Sheet formulas)

2. **Color Coding:**
   - Green (COMPLIANT): No faults, no remedial work needed
   - Yellow (YES): Faults found, remedial work needed
   - Red (NO): Unable to inspect or critical issues

---

## 8.1 Material Call-Off Sheet

### Component-to-B-Code Mapping (Updated 2026-03-28)
The Material Call-Off sheet tracks components needed for remedial works. Each component row must count doors from Door Schedule by B-code.

**CRITICAL:** Use wildcard COUNTIF against Door Schedule column R (ALL B CODES) — same logic as Quote Sheet Option A (see Section 6).

**Counting Method:**
- For each B-code, count doors where that code appears **anywhere** in column R (ALL B CODES)
- This ensures multi-code doors are counted for ALL their required components
- Example: Door with "B10, B01, B06, B12, B07" counts toward B01, B06, B07, B10, B12 material call-offs

| Row | Component | B-Code | Calculation |
|-----|-----------|--------|-------------|
| 13 | Overhead closers | B03 | Count B03 doors |
| 14 | Hinge sets | B04 | Count B04 doors |
| 15 | Intumescent + smoke seals | B01 | Count B01 doors |
| 16 | Intumescent only | B02 | Count B02 doors |
| 17 | Signage | B07 | Count B07 doors × 2 (2 signs per door) |
| 18 | Lever handles/latch | B05 | Count B05 doors |
| 19 | Drop seal | B09 | Count B09 doors |
| 20 | Intumescent mastic | B06 | Count B06 doors |
| 21 | Hardwood lipping | B11 | Count B11 doors |
| 22 | Hardwood void infill | B12 | Count B12 doors |

**Example:**
If Door Schedule has:
- B01=22 doors → Material Call-Off row 15 = 22
- B03=1 door → Material Call-Off row 13 = 1
- B05=4 doors → Material Call-Off row 18 = 4
- B06=1 door → Material Call-Off row 20 = 1
- B12=1 door → Material Call-Off row 22 = 1

**Validation:**
After populating Material Call-Off, log all counts to help diagnose discrepancies.

---

## 9. Type 2 Survey Notice

**When:** User generates quote from Type 2 survey (Excel format)

**Where:** Frontend UI, below download button

**Message:**
> ⚠️ Option B (full replacement) could not be priced — fire strategy drawings were not included in this survey. To unlock Option B pricing, ask the client for their fire strategy drawings and forward to the estimating team.

**Implementation:**
- Backend: Set `X-Survey-Type: TYPE_2` header in response
- Frontend: Read header and conditionally show message

---

## 10. Validation Rules

### Pre-Processing Checks
1. **File Format:**
   - Valid: .pdf, .xlsx, .xls, .txt
   - Invalid: All others → HTTP 400

2. **Client Name:**
   - Required field
   - Must be non-empty string
   - Used in output filename and headers

3. **Door Data:**
   - Minimum 1 door required
   - Maximum ~200 doors (practical limit)

### Post-Extraction Checks
1. **Fire Rating (Type 1 only):**
   - If ALL doors show "Unknown", log ERROR
   - Check extraction logic

2. **Option B Pricing (Type 1 only):**
   - If 0 replacement doors but survey shows faults, log WARNING
   - Verify Opt B column logic

3. **Totals:**
   - If Option A total = £0 but faults exist, log ERROR
   - Check B-code mapping and rate lookup

---

## 11. Rate Card Management

### Database Priority
1. **Primary Source:** PostgreSQL database (rate_card_items table)
2. **Fallback:** CSV file if database unavailable
3. **Admin:** Users can edit prices via /rates endpoint

### Rate Structure
- **ART Code:** BMTrada standard code for repairs (ART01, ART02... ART24)
- **B-Code (Remedial):** WestPark internal code for repairs (B01-B12)
  - Maps from ART codes via CSV
  - Used in Option A (remedial works)
- **A-Code (Replacement):** WestPark replacement door codes (A01–A15)
  - Used in Option B (full replacement)
  - Maps to Rate Card for VLOOKUP pricing
- **Quote Sheet Labels:** 
  - Option A rows use "A.01"–"A.12" labels (corresponds to B01-B12 remedial codes)
  - Option B rows use "B.01"–"B.15" labels for display (maps to A01-A15 in Rate Card)
- **Unit Price:** £ per item/door

### Rate Card Columns
**As of 2026-03-27:** T&J (Tape & Jointing) column has been REMOVED per Matt's instruction.

**Current structure:**
- Column A: Code (A01-A17, B01-B12, C01-C05)
- Column B: Description
- Column D: Materials (£)
- Column E: Labour (£)
- Column F: ~~Tape & Jointing~~ (REMOVED)
- Column G: Humping (£) — only for A-series replacement doors
- Column H: Notes (for mock/pending rates)

**Internal Cost Calculation:**
- Option A (Remedial): Materials + Labour
- Option B (Replacement): Materials + Labour + Humping

**Client Price:** Internal Cost ÷ (1 - Margin%) — margin applied via Quote Sheet R2 cell

### 11.1 Rate Status (Updated 2026-03-27)

**CONFIRMED RATES FROM ALEX:**

**A-SERIES (Replacement Doors):**
- A01: Materials=£593.08, Labour=£250, Humping=£40 → Total=£883.08
- A02: Materials=£682.18, Labour=£250, Humping=£40 → Total=£972.18
- A03: Materials=£770.18, Labour=£250, Humping=£40 → Total=£1060.18
- A04: Materials=£993.73, Labour=£350, Humping=£80 → Total=£1423.73
- A05: Materials=£593.08, Labour=£250, Humping=£40 → Total=£883.08
- A06: Materials=£682.18, Labour=£250, Humping=£40 → Total=£972.18
- A07: Materials=£770.18, Labour=£250, Humping=£40 → Total=£1060.18
- A08: Materials=£993.73, Labour=£350, Humping=£80 → Total=£1423.73
- A09: Materials=£768.65, Labour=£250, Humping=£40 → Total=£1058.65
- A10: Materials=£865.15, Labour=£250, Humping=£40 → Total=£1155.15
- A11: Materials=£1229.20, Labour=£350, Humping=£80 → Total=£1659.20
- A12 (E/O Hardwood Veneer): Materials=£100.00 → Total=£100.00
- A14 (E/O FD30 Vision Panel ≤300x600): Materials=£139.18 → Total=£139.18
- A16 (E/O FD60 Vision Panel ≤300x600): Materials=£206.00 → Total=£206.00

**B-SERIES (Remedial Works):**
- B01: Materials=£67.65, Labour=£75 → Total=£142.65
- B02: Materials=£67.65, Labour=£75 → Total=£142.65
- B03: Materials=£45.00, Labour=£37.50 → Total=£82.50
- B04: Materials=£15.00, Labour=£75 → Total=£90.00
- B05: Materials=£25.00, Labour=£75 → Total=£100.00
- B06: Materials=£10.00, Labour=£75 → Total=£85.00
- B07: Materials=£10.00, Labour=£37.50 → Total=£47.50
- B11: Materials=£30.00, Labour=£37.50 → Total=£67.50

**C-SERIES (Preliminaries):**
- C04a (Out-of-hours weekday): Labour=£150.00 → Total=£150.00
- C04b (Out-of-hours Sunday): Labour=£300.00 → Total=£300.00

**MOCK RATES (PENDING CONFIRMATION):**

⚠️ These rates are estimates. Matt must confirm with Alex/client before sending quote.

- **A13** (E/O External Grade): £150.00 — *"Alex to confirm — under investigation"*
- **A15** (E/O FD30 Vision Panel >300x600): £200.00 — *"Alex to confirm price for larger FD30 panel"*
- **A17** (E/O FD60 Vision Panel >300x600): £280.00 — *"Alex to confirm price for larger FD60 panel"*
- **B08** (Hold-open device): £325.00 — *"Alex cannot price access control items — quote separately per job"*
- **B09** (Drop seal): £125.00 — *"Alex cannot price access control items — quote separately per job"*
- **B10** (Adjust/re-hang door leaf): £300.00 — *"Hourly rate £37.50/hr or minimum 1 day carpenter £300 cost — Matt to confirm per-door rate"*
- **B12** (Void infill): £500.00 — *"Hourly rate £62.50/hr or minimum 1 day magic man £500 cost — Matt to confirm per-door rate"*
- **C01** (Mobilisation): £170.00 — *"Alex to confirm call-out rate"*
- **C02** (Waste removal): £300.00 — *"Alex: £300 minimum per visit — not per door. Matt to confirm how to allocate across jobs"*
- **C03** (Certification): £40.00 — *"Alex to confirm per-door certification rate"*
- **C05** (Scaffold): £500.00 — *"Job by job basis — Alex cannot provide standard rate"*

**Output Flagging:**
When mock rates are used in a quote, the system adds a "⚠️ MOCK RATE" note in the Rate Card sheet (Column H) to alert Matt that this line item needs confirmation before client submission.

---

## 12. Compliance Notes

### Type 1 Compliance Note
```
This report identifies fire doors requiring remedial works to achieve compliance with Approved Document B and the Regulatory Reform (Fire Safety) Order 2005. Works are categorized as Option A (remedial works) or Option B (full replacement). All prices exclude VAT and are subject to site survey confirmation.
```

### Type 2 Compliance Note
```
This report identifies fire doors requiring remedial works based on visual inspection. Option A provides remedial works to address identified faults. Option B (full replacement) cannot be priced without fire strategy drawings - please request these from the client if replacement doors are required. All prices exclude VAT and are subject to site survey confirmation.
```

**Rule:** Use the correct note based on survey type. Do not mix Type 1 and Type 2 language.

---

## 13. Known Issues & Fixes

### Issue: Excel Shows £0 on Open
- **Cause:** openpyxl cannot reliably set cached formula values
- **Solution:** Write calculated numbers directly (not formulas)
- **Affected Cells:** Quote Sheet totals, Client Summary totals

### Issue: Duplicate Door IDs
- **Cause:** Multiple floors with same numbering (A01, A02...)
- **Solution:** Add floor suffix to Door ID (A01-L2, A01-L3)
- **Type:** Type 1 surveys only

### Issue: Ghost Rows from Previous Extraction
- **Cause:** Template not fully cleared before population
- **Solution:** Clear extended range (A–V) in Door Schedule before writing

---

## 14. Change Log

### 2026-03-27 (Update 3) - Alpha Sights Fix #2
- **Section 6:** MAJOR UPDATE - Complete A-series mapping table with S suffix distinction + height ranges
  - **Critical:** FD30 ≠ FD30S (S suffix = smoke seals)
  - Added full mapping table with 15 A-codes (A01-A15)
  - FD30 (no smoke): A01-A04
  - FD30S (with smoke): A05-A08
  - FD60S (with smoke): A09-A11
  - Height ranges: ≤2040mm, 2040-2400mm, 2400-2730mm
  - Example: FD30 Double ≤2040mm → A04 (not A08)
  - Example: FD30S Double ≤2040mm → A08
  - Pricing logic now requires: fire rating + leaf config + door height
  - Added default mappings for Nominal doors
  - Added 3 worked examples showing correct code selection

### 2026-03-24 (Update 2)
- **Section 4:** Fixed ART→B-code mappings - replaced incorrect mappings with complete correct data from BMTrada_ART_Codes_RateCard_Mapping.csv
  - All 24 ART codes now correctly documented
  - Example corrections: ART01 → B11 (lipping), ART03 → B06 (fire-stopping)
- **Section 4.1:** Added ART14 special case rule - damaged glazing has no B-code equivalent, flag for manual review
- **Section 4.2:** Added ART23 special case rule - no applicable repair technique exists, flag for manual review
- **Section 4.3:** Added multiple B-codes priority rule for Type 1 surveys (B01 > B03 > B04 > B10 > B05 > B02 > B06 > B07)
- **Section 6:** Fixed replacement door codes - corrected from B-series to A-series (A01–A15)
  - Added A09 (FD60S Single ≤2040mm)
  - Added A10 (FD60S Single 2040–2400mm)
  - Added A11 (FD60S Double ≤2040mm)
  - Added A12-A15 (Extra Over items: veneer, external grade, vision panels)
  - Updated all references to match Rate Card VLOOKUP codes
- **Section 11:** Clarified A-code vs B-code naming (remedial B-codes vs replacement A-codes)

### 2026-03-24 (Initial)
- Created initial FIRE_DOOR_RULES.md
- Documented all extraction, mapping, and output rules
- Added Type 1 vs Type 2 differentiation
- Added Option B pricing rules
- Added validation and compliance notes
- Added known issues section

---

## 15. Maintenance

**When to Update This File:**
- Any change to extraction logic
- New B-code or A-code added
- New fault text pattern
- Change to validation rules
- Change to output format
- Bug fix that affects business logic

**Review Frequency:** Monthly or after major changes

**Approval Required:** Mauricio Lopez (owner)

---

*End of FIRE_DOOR_RULES.md*
